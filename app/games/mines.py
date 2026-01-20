"""
💣 MINES GAME - גרסה משודרגת עם אנימציות מתקדמות
משחק המוקשים עם גרפיקה, אנימציות, ואפקטים מיוחדים
"""

import json
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from app.database.manager import db
from app.utils.leaderboard import leaderboard
from app.utils.themes import get_theme, apply_theme
from app.security import smart_rate_limiter

# ============ ANIMATION CONSTANTS ============
MINES_EMOJIS = ["💣", "💥", "🔥", "☠️", "⚠️"]
DIAMOND_EMOJIS = ["💎", "✨", "🌟", "💠", "🔶"]
CELL_STATES = {
    "hidden": "⬜",
    "mine": "💣",
    "diamond": "💎",
    "exploded": "💥",
    "flagged": "🚩",
    "safe": "✅"
}

# ============ GAME CONFIGURATION ============
TIER_CONFIG = {
    "Free": {"mines": 5, "multiplier_base": 1.1, "max_bet": 100, "grid_size": 5},
    "Pro": {"mines": 3, "multiplier_base": 1.3, "max_bet": 500, "grid_size": 5},
    "VIP": {"mines": 2, "multiplier_base": 1.5, "max_bet": 1000, "grid_size": 5}
}

BET_OPTIONS = [10, 25, 50, 100, 250, 500, 1000]

# ============ ANIMATION MANAGER ============
class MinesAnimationManager:
    """מנהל אנימציות למשחק המוקשים"""
    
    @staticmethod
    async def reveal_animation(query, cell_index: int, is_mine: bool, duration: float = 0.5):
        """אנימציית גילוי תא"""
        if is_mine:
            frames = ["💣", "💥", "🔥", "☠️"]
        else:
            frames = ["💎", "✨", "🌟", "💎"]
        
        original_text = query.message.text
        original_markup = query.message.reply_markup
        
        for frame in frames:
            try:
                # יצירת לוח מעודכן עם האנימציה
                temp_board = await MinesGameManager.create_board_display(
                    query.from_user.id, 
                    highlight_cell=cell_index,
                    highlight_emoji=frame
                )
                
                await query.edit_message_text(
                    text=f"🎮 **משחק המוקשים**\n\n{temp_board}\n\n🔄 **מגלה תא...** {frame}",
                    reply_markup=original_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
                await asyncio.sleep(duration / len(frames))
            except:
                break
        
        return True
    
    @staticmethod
    async def cashout_animation(query, amount: int, multiplier: float):
        """אנימציית משיכת רווחים"""
        frames = [
            "💰", "💵", "💸", "🤑", 
            "🎊", "🎉", "🏆", "🌟",
            "✨", "🔥", "🚀", "💫"
        ]
        
        for i, frame in enumerate(frames):
            try:
                text = f"🎉 **משיכה מוצלחת!** {frame}\n\n"
                text += f"💰 **סכום הזכייה:** {amount:,} מטבעות\n"
                text += f"📈 **מכפיל סופי:** x{multiplier:.2f}\n\n"
                
                # אנימציית ספירת מטבעות
                if i < 8:
                    coins = "🪙" * min(i + 1, 10)
                    text += f"{coins}"
                
                await query.edit_message_text(text=text)
                await asyncio.sleep(0.15)
            except:
                pass
        
        return True
    
    @staticmethod
    async def game_over_animation(query, lost_amount: int):
        """אנימציית סיום משחק (הפסד)"""
        explosion_frames = ["💣", "💥", "🔥", "☠️", "😵", "💔"]
        
        for frame in explosion_frames:
            try:
                await query.edit_message_text(
                    text=f"💥 **המשחק נגמר!** {frame}\n\n"
                         f"😔 הפסדת {lost_amount} מטבעות...\n\n"
                         f"💡 טיפ: נסה שוב עם אסטרטגיה אחרת!",
                    parse_mode=ParseMode.MARKDOWN
                )
                await asyncio.sleep(0.3)
            except:
                pass
        
        return True
    
    @staticmethod
    async def multiplier_countup(query, start: float, end: float, duration: float = 1.0):
        """אנימציית ספירת מכפיל עולה"""
        steps = 20
        step_size = (end - start) / steps
        
        for i in range(steps + 1):
            current = start + (step_size * i)
            try:
                await query.edit_message_text(
                    text=f"📈 **המכפיל עולה!**\n\n"
                         f"🎯 מכפיל נוכחי: **x{current:.2f}**\n"
                         f"💰 רווח פוטנציאלי: **{int(query.message.text.split('💰 ')[1].split(' ')[0]) * current:.0f}** מטבעות",
                    reply_markup=query.message.reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
                await asyncio.sleep(duration / steps)
            except:
                break
        
        return True

# ============ GAME MANAGER ============
class MinesGameManager:
    """מנהל הלוגיקה של משחק המוקשים"""
    
    @staticmethod
    def get_user_tier_config(user_id: int) -> Dict:
        """קבל הגדרות דרגה למשתמש"""
        user = db.get_user(user_id)
        tier = user.get("tier", "Free")
        return TIER_CONFIG.get(tier, TIER_CONFIG["Free"])
    
    @staticmethod
    async def create_board_display(user_id: int, highlight_cell: int = None, highlight_emoji: str = None) -> str:
        """צור תצוגה גרפית של הלוח"""
        game_state = MinesGameManager.get_game_state(user_id)
        if not game_state:
            return "לוח לא זמין"
        
        grid_size = game_state.get("grid_size", 5)
        revealed = game_state.get("revealed", [])
        mines = game_state.get("mines", [])
        flagged = game_state.get("flagged", [])
        
        board_text = ""
        for row in range(grid_size):
            row_text = ""
            for col in range(grid_size):
                cell_index = row * grid_size + col
                
                if cell_index == highlight_cell and highlight_emoji:
                    row_text += f"{highlight_emoji} "
                elif cell_index in revealed:
                    if cell_index in mines:
                        row_text += "💣 "
                    else:
                        # ספור יהלומים שכנים
                        neighbor_diamonds = MinesGameManager.count_neighbor_diamonds(cell_index, revealed, mines, grid_size)
                        if neighbor_diamonds > 0:
                            row_text += f"{neighbor_diamonds}️⃣ "
                        else:
                            row_text += "💎 "
                elif cell_index in flagged:
                    row_text += "🚩 "
                else:
                    row_text += "⬜ "
            
            board_text += row_text + "\n"
        
        return board_text
    
    @staticmethod
    def count_neighbor_diamonds(cell_index: int, revealed: List[int], mines: List[int], grid_size: int) -> int:
        """ספור יהלומים שכנים לתא"""
        count = 0
        row, col = divmod(cell_index, grid_size)
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < grid_size and 0 <= new_col < grid_size:
                    neighbor_index = new_row * grid_size + new_col
                    if neighbor_index in revealed and neighbor_index not in mines:
                        count += 1
        
        return count
    
    @staticmethod
    def create_new_game(user_id: int, bet_amount: int) -> Dict:
        """צור משחק חדש"""
        config = MinesGameManager.get_user_tier_config(user_id)
        grid_size = config["grid_size"]
        total_cells = grid_size * grid_size
        
        # יצירת מוקשים
        mines_count = config["mines"]
        mines = random.sample(range(total_cells), mines_count)
        
        # יצירת לוח
        game_state = {
            "user_id": user_id,
            "bet_amount": bet_amount,
            "mines": mines,
            "revealed": [],
            "flagged": [],
            "grid_size": grid_size,
            "multiplier": 1.0,
            "game_over": False,
            "won": False,
            "created_at": datetime.now().isoformat(),
            "last_action": datetime.now().isoformat(),
            "config": config
        }
        
        # שמור במסד הנתונים
        game_key = f"mines:{user_id}:active"
        db.r.setex(game_key, 1800, json.dumps(game_state))  # 30 דקות
        
        return game_state
    
    @staticmethod
    def get_game_state(user_id: int) -> Optional[Dict]:
        """קבל מצב משחק נוכחי"""
        game_key = f"mines:{user_id}:active"
        game_data = db.r.get(game_key)
        
        if game_data:
            return json.loads(game_data)
        return None
    
    @staticmethod
    def update_game_state(user_id: int, updates: Dict):
        """עדכן מצב משחק"""
        game_state = MinesGameManager.get_game_state(user_id)
        if not game_state:
            return False
        
        game_state.update(updates)
        game_state["last_action"] = datetime.now().isoformat()
        
        game_key = f"mines:{user_id}:active"
        db.r.setex(game_key, 1800, json.dumps(game_state))
        
        return True
    
    @staticmethod
    def calculate_multiplier(game_state: Dict, new_revealed_cell: int = None) -> float:
        """חשב מכפיל נוכחי"""
        config = game_state.get("config", TIER_CONFIG["Free"])
        base_multiplier = config["multiplier_base"]
        revealed_count = len(game_state.get("revealed", []))
        
        if new_revealed_cell is not None:
            # מכפיל גדל עם כל יהלום שנחשף
            multiplier = base_multiplier ** (revealed_count + 1)
        else:
            multiplier = base_multiplier ** revealed_count
        
        return round(multiplier, 2)
    
    @staticmethod
    def reveal_cell(user_id: int, cell_index: int) -> Tuple[bool, Optional[float]]:
        """גלה תא ובדוק אם הוא מוקש"""
        game_state = MinesGameManager.get_game_state(user_id)
        if not game_state:
            return False, None
        
        if cell_index in game_state["revealed"]:
            return False, None  # תא כבר נחשף
        
        if cell_index in game_state["flagged"]:
            return False, None  # תא מסומן
        
        # הוסף לרשימת תאים שנחשפו
        game_state["revealed"].append(cell_index)
        
        # בדוק אם זה מוקש
        if cell_index in game_state["mines"]:
            game_state["game_over"] = True
            game_state["won"] = False
            MinesGameManager.update_game_state(user_id, game_state)
            return True, None  # פגיעה במוקש
        
        # חשב מכפיל חדש
        new_multiplier = MinesGameManager.calculate_multiplier(game_state, cell_index)
        game_state["multiplier"] = new_multiplier
        
        MinesGameManager.update_game_state(user_id, game_state)
        return False, new_multiplier  # יהלום נמצא
    
    @staticmethod
    def toggle_flag(user_id: int, cell_index: int) -> bool:
        """הוסף/הסר דגל מתא"""
        game_state = MinesGameManager.get_game_state(user_id)
        if not game_state:
            return False
        
        if cell_index in game_state["flagged"]:
            game_state["flagged"].remove(cell_index)
        else:
            # הגבל מספר דגלים למספר המוקשים
            max_flags = len(game_state["mines"])
            if len(game_state["flagged"]) < max_flags:
                game_state["flagged"].append(cell_index)
        
        MinesGameManager.update_game_state(user_id, game_state)
        return True
    
    @staticmethod
    def cashout_game(user_id: int) -> Tuple[bool, int, float]:
        """משוך רווחים וסיים משחק"""
        game_state = MinesGameManager.get_game_state(user_id)
        if not game_state or game_state["game_over"]:
            return False, 0, 0.0
        
        # חשב זכייה
        bet_amount = game_state["bet_amount"]
        multiplier = game_state["multiplier"]
        win_amount = int(bet_amount * multiplier)
        
        # עדכן יתרה
        db.add_balance(user_id, win_amount, f"Mines game cashout (x{multiplier})")
        
        # עדכן סטטיסטיקות
        leaderboard.update_score(user_id, 'total_wins', 1)
        leaderboard.update_score(user_id, 'total_winnings', win_amount)
        leaderboard.update_score(user_id, 'mines_wins', 1)
        
        # סיים משחק
        game_state["game_over"] = True
        game_state["won"] = True
        game_state["cashout_amount"] = win_amount
        MinesGameManager.update_game_state(user_id, game_state)
        
        # מחק משחק פעיל
        game_key = f"mines:{user_id}:active"
        db.r.delete(game_key)
        
        return True, win_amount, multiplier

# ============ TELEGRAM HANDLERS ============
async def start_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """התחל משחק מוקשים חדש או הצג משחק קיים"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    
    # בדיקת הגבלת rate
    allowed, wait_time = smart_rate_limiter.check_rate_limit(user_id, 'mines_game')
    if not allowed:
        await query.answer(f"⏳ אנא המתן {wait_time} שניות לפני משחק נוסף", show_alert=True)
        return
    
    # בדוק אם יש משחק פעיל
    game_state = MinesGameManager.get_game_state(user_id)
    
    if game_state and not game_state.get("game_over", False):
        # הצג משחק קיים
        await show_mines_game(update, context, game_state)
    else:
        # התחל משחק חדש - בחירת סכום הימור
        await choose_bet_amount(update, context)

async def choose_bet_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """בחירת סכום הימור למשחק חדש"""
    query = update.callback_query
    user_id = query.from_user.id
    
    user = db.get_user(user_id)
    balance = int(user.get("balance", 0))
    tier = user.get("tier", "Free")
    config = TIER_CONFIG.get(tier, TIER_CONFIG["Free"])
    
    text = f"""
💣 **משחק המוקשים - {tier}**

💰 **היתרה שלך:** {balance:,} 🪙
🎯 **דרגה:** {tier} ({config['mines']} מוקשים)
📈 **מכפיל בסיס:** x{config['multiplier_base']}
🔢 **גודל לוח:** {config['grid_size']}x{config['grid_size']}

👇 **בחר סכום הימור:**
"""
    
    # יצירת כפתורי הימור
    keyboard = []
    row = []
    
    for bet in BET_OPTIONS:
        if bet <= config["max_bet"] and bet <= balance:
            btn_text = f"💰 {bet}"
        else:
            btn_text = f"🔒 {bet}"
        
        callback_data = f"mines_bet_{bet}" if bet <= balance and bet <= config["max_bet"] else "mines_invalid_bet"
        
        row.append(InlineKeyboardButton(btn_text, callback_data=callback_data))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton("✍️ סכום אחר", callback_data="mines_custom_bet"),
        InlineKeyboardButton("📖 הדרכה", callback_data="mines_guide")
    ])
    
    keyboard.append([
        InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start"),
        InlineKeyboardButton("🎮 משחקים אחרים", callback_data="game_select")
    ])
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_bet_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בבחירת סכום הימור"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "mines_invalid_bet":
        await query.answer("❌ סכום זה אינו זמין עבור הדרגה או היתרה שלך", show_alert=True)
        return
    elif data == "mines_custom_bet":
        await choose_custom_bet(update, context)
        return
    elif data == "mines_guide":
        await show_mines_guide(update, context)
        return
    
    # קבל סכום ההימור
    bet_amount = int(data.split("_")[2])
    
    # בדוק יתרה
    user = db.get_user(user_id)
    balance = int(user.get("balance", 0))
    
    if balance < bet_amount:
        await query.answer("❌ אין לך מספיק מטבעות!", show_alert=True)
        return
    
    # הורד את ההימור
    if not db.deduct_balance(user_id, bet_amount, "Mines game bet"):
        await query.answer("❌ שגיאה בהורדת היתרה", show_alert=True)
        return
    
    # צור משחק חדש
    game_state = MinesGameManager.create_new_game(user_id, bet_amount)
    
    # אנימציית התחלת משחק
    await MinesAnimationManager.multiplier_countup(query, 1.0, 1.0, 0.5)
    
    # הצג את הלוח
    await show_mines_game(update, context, game_state)

async def choose_custom_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """בחירת סכום הימור מותאם אישית"""
    query = update.callback_query
    user_id = query.from_user.id
    
    user = db.get_user(user_id)
    tier = user.get("tier", "Free")
    config = TIER_CONFIG.get(tier, TIER_CONFIG["Free"])
    
    text = f"""
💰 **הזן סכום הימור מותאם אישית**

📊 **הגבלות:**
• מינימום: 10 מטבעות
• מקסימום: {config['max_bet']} מטבעות (לדרגת {tier})
• יתרה נוכחית: {int(user.get('balance', 0)):,} 🪙

✍️ **שלח את הסכום הרצוי בצ'אט:**
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 חזרה", callback_data="play_mines")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    # שמור מצב המתנה להקלדה
    context.user_data['waiting_for_mines_bet'] = True

async def show_mines_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """הצגת הדרכה למשחק"""
    query = update.callback_query
    
    text = """
📖 **הדרכת משחק המוקשים**

🎯 **מטרה:** חשף יהלומים מבלי לפגוע במוקשים!

🔄 **איך לשחק:**
1. בחר סכום הימור
2. לחץ על ריבועים כדי לחשוף אותם
3. כל יהלום מגדיל את המכפיל
4. לחץ "משוך" כדי לשמור על הרווחים
5. אם תפגע במוקש - ההפסד הוא סכום ההימור

💎 **יהלומים:** מגדילים את המכפיל
💣 **מוקשים:** מסיימים את המשחק בהפסד

📈 **מכפילים:**
• כל יהלום מגדיל את המכפיל
• ניתן למשוך בכל עת
• ככל שחושפים יותר יהלומים - המכפיל גדל

🎓 **טיפים:**
• התחל מאזורים פתוחים
• סמן מוקשים חשודים עם 🚩
• אל תחכה יותר מדי - משוך בזמן!
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 התחל משחק", callback_data="play_mines"),
         InlineKeyboardButton("🔙 חזרה", callback_data="play_mines")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def show_mines_game(update: Update, context: ContextTypes.DEFAULT_TYPE, game_state: Dict = None):
    """הצג את הלוח הנוכחי"""
    query = update.callback_query if hasattr(update, 'callback_query') else None
    user_id = update.effective_user.id
    
    if not game_state:
        game_state = MinesGameManager.get_game_state(user_id)
    
    if not game_state:
        if query:
            await query.answer("❌ לא נמצא משחק פעיל", show_alert=True)
        return
    
    # יצירת תצוגת הלוח
    board_display = await MinesGameManager.create_board_display(user_id)
    
    # מידע נוסף
    bet_amount = game_state["bet_amount"]
    multiplier = game_state["multiplier"]
    revealed_count = len(game_state.get("revealed", []))
    mines_count = len(game_state.get("mines", []))
    flagged_count = len(game_state.get("flagged", []))
    
    tier = game_state.get("config", {}).get("tier", "Free")
    potential_win = int(bet_amount * multiplier)
    
    text = f"""
💣 **משחק המוקשים - {tier}**

{board_display}

📊 **סטטיסטיקות:**
💰 **הימור:** {bet_amount:,} 🪙
📈 **מכפיל נוכחי:** x{multiplier:.2f}
💎 **יהלומים נמצאו:** {revealed_count}
🚩 **דגלים:** {flagged_count}/{mines_count}
🎯 **רווח פוטנציאלי:** {potential_win:,} 🪙

💡 **טיפ:** השתמש בדגלים לסמן מוקשים חשודים!
"""
    
    # יצירת לוח מקשים
    grid_size = game_state.get("grid_size", 5)
    keyboard = []
    
    for row in range(grid_size):
        row_buttons = []
        for col in range(grid_size):
            cell_index = row * grid_size + col
            
            if cell_index in game_state.get("revealed", []):
                if cell_index in game_state.get("mines", []):
                    btn_text = "💣"
                else:
                    neighbor_diamonds = MinesGameManager.count_neighbor_diamonds(
                        cell_index, 
                        game_state.get("revealed", []),
                        game_state.get("mines", []),
                        grid_size
                    )
                    btn_text = f"{neighbor_diamonds}️⃣" if neighbor_diamonds > 0 else "💎"
            elif cell_index in game_state.get("flagged", []):
                btn_text = "🚩"
            else:
                btn_text = "⬜"
            
            row_buttons.append(
                InlineKeyboardButton(btn_text, callback_data=f"mines_click_{cell_index}")
            )
        
        keyboard.append(row_buttons)
    
    # כפתורי פעולות
    action_buttons = []
    
    if not game_state.get("game_over", False):
        action_buttons.append(
            InlineKeyboardButton("🚩 סימון דגל", callback_data="mines_toggle_flag_mode")
        )
        action_buttons.append(
            InlineKeyboardButton("💰 משוך", callback_data="mines_cashout")
        )
    
    keyboard.append(action_buttons)
    
    keyboard.append([
        InlineKeyboardButton("🔄 משחק חדש", callback_data="play_mines"),
        InlineKeyboardButton("🏠 תפריט", callback_data="start")
    ])
    
    if query:
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_mines_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בלחיצה על תא בלוח"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # בדוק אם במצב סימון דגלים
    flag_mode = context.user_data.get('mines_flag_mode', False)
    
    if data == "mines_toggle_flag_mode":
        context.user_data['mines_flag_mode'] = not flag_mode
        mode_text = "פעיל" if not flag_mode else "לא פעיל"
        await query.answer(f"🚩 מצב דגלים: {mode_text}", show_alert=True)
        await show_mines_game(update, context)
        return
    elif data == "mines_cashout":
        await handle_cashout(update, context)
        return
    
    # קבל אינדקס התא
    cell_index = int(data.split("_")[2])
    
    # בדוק אם המשחק פעיל
    game_state = MinesGameManager.get_game_state(user_id)
    if not game_state or game_state.get("game_over", False):
        await query.answer("❒ המשחק נגמר, התחל משחק חדש", show_alert=True)
        return
    
    # בדוק אם במצב דגלים
    if flag_mode:
        # סימון/ביטול דגל
        MinesGameManager.toggle_flag(user_id, cell_index)
        await query.answer("🚩 דגל עודכן", show_alert=True)
        await show_mines_game(update, context)
        return
    
    # בדוק אם התא כבר נחשף או מסומן
    if cell_index in game_state.get("revealed", []) or cell_index in game_state.get("flagged", []):
        await query.answer("❌ לא ניתן ללחוץ על תא זה", show_alert=True)
        return
    
    # אנימציית גילוי
    await MinesAnimationManager.reveal_animation(query, cell_index, False)
    
    # גלה את התא
    is_mine, new_multiplier = MinesGameManager.reveal_cell(user_id, cell_index)
    
    if is_mine:
        # פגיעה במוקש - סיום המשחק
        await MinesAnimationManager.game_over_animation(query, game_state["bet_amount"])
        
        # עדכן סטטיסטיקות
        leaderboard.update_score(user_id, 'total_losses', 1)
        leaderboard.update_score(user_id, 'mines_losses', 1)
        
        # הצג לוח סופי
        await show_mines_game(update, context)
    else:
        # יהלום נמצא
        await query.answer(f"💎 יהלום נמצא! מכפיל חדש: x{new_multiplier:.2f}", show_alert=True)
        
        # אנימציית עליית מכפיל
        await MinesAnimationManager.multiplier_countup(
            query, 
            game_state["multiplier"], 
            new_multiplier,
            0.7
        )
        
        # הצג לוח מעודכן
        await show_mines_game(update, context)

async def handle_cashout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בבקשת משיכת רווחים"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # משוך רווחים
    success, win_amount, multiplier = MinesGameManager.cashout_game(user_id)
    
    if not success:
        await query.answer("❌ לא ניתן למשוך כרגע", show_alert=True)
        return
    
    # אנימציית זכייה
    await MinesAnimationManager.cashout_animation(query, win_amount, multiplier)
    
    # הצג מסך סיום
    text = f"""
🎉 **משיכה מוצלחת!**

💰 **סכום הזכייה:** {win_amount:,} מטבעות
📈 **מכפיל סופי:** x{multiplier:.2f}
🎮 **יהלומים שנחשפו:** {len(MinesGameManager.get_game_state(user_id).get('revealed', [])) if MinesGameManager.get_game_state(user_id) else 0}

🏆 **כל הכבוד!** הרווחים נוספו לחשבונך.
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 משחק חדש", callback_data="play_mines"),
         InlineKeyboardButton("🏠 תפריט ראשי", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בהקלדת סכום הימור מותאם אישית"""
    if not context.user_data.get('waiting_for_mines_bet', False):
        return
    
    user_id = update.effective_user.id
    text = update.message.text
    
    # בדוק אם הקלט מספר
    if not text.isdigit():
        await update.message.reply_text("❌ נא להזין מספר בלבד")
        return
    
    bet_amount = int(text)
    
    # בדוק הגבלות
    user = db.get_user(user_id)
    balance = int(user.get("balance", 0))
    tier = user.get("tier", "Free")
    config = TIER_CONFIG.get(tier, TIER_CONFIG["Free"])
    
    if bet_amount < 10:
        await update.message.reply_text("❌ המינימום הוא 10 מטבעות")
        return
    
    if bet_amount > config["max_bet"]:
        await update.message.reply_text(f"❌ המקסימום לדרגת {tier} הוא {config['max_bet']} מטבעות")
        return
    
    if bet_amount > balance:
        await update.message.reply_text(f"❌ אין לך מספיק מטבעות. יתרה: {balance:,}")
        return
    
    # נקה מצב המתנה
    context.user_data['waiting_for_mines_bet'] = False
    
    # הורד את ההימור
    if not db.deduct_balance(user_id, bet_amount, "Mines game custom bet"):
        await update.message.reply_text("❌ שגיאה בהורדת היתרה")
        return
    
    # צור משחק חדש
    game_state = MinesGameManager.create_new_game(user_id, bet_amount)
    
    # אנימציה והצג לוח
    try:
        await update.message.reply_text(f"✅ הימור של {bet_amount} מטבעות התקבל!")
        
        # צור שאילתה מדומה להצגת הלוח
        class MockQuery:
            def __init__(self, message):
                self.message = message
                self.from_user = message.from_user
            
            async def edit_message_text(self, *args, **kwargs):
                return await self.message.reply_text(*args, **kwargs)
            
            async def answer(self, *args, **kwargs):
                pass
        
        mock_query = MockQuery(update.message)
        
        # הצג את הלוח
        await show_mines_game(update, context, game_state)
    except Exception as e:
        await update.message.reply_text(f"❌ שגיאה: {str(e)}")

# ============ REGISTER HANDLERS ============
def register_mines_handlers(application):
    """רישום מטפלים למשחק המוקשים"""
    application.add_handler(CallbackQueryHandler(start_mines, pattern="^play_mines$"))
    application.add_handler(CallbackQueryHandler(handle_bet_selection, pattern="^mines_bet_"))
    application.add_handler(CallbackQueryHandler(handle_mines_click, pattern="^mines_click_"))
    application.add_handler(CallbackQueryHandler(handle_cashout, pattern="^mines_cashout$"))
    application.add_handler(CallbackQueryHandler(choose_custom_bet, pattern="^mines_custom_bet$"))
    application.add_handler(CallbackQueryHandler(show_mines_guide, pattern="^mines_guide$"))
    application.add_handler(CallbackQueryHandler(handle_mines_click, pattern="^mines_toggle_flag_mode$"))
    
    # מטפל להודעות טקסט (לסכומים מותאמים אישית)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

if __name__ == "__main__":
    print("✅ מודול משחק המוקשים נטען בהצלחה")
