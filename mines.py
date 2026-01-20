import random
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import update_user_stat, r, save_game_state, get_game_state

GRID_SIZE = 5
TOTAL_CELLS = 25

async def start_mines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    
    mines_count = 3
    bet_amount = 50 
    
    user_profile = r.hgetall(f"user:{uid}:profile")
    user_bal = int(user_profile.get("balance", 0))
    
    if user_bal < bet_amount:
        await query.answer("❌ אין לך מספיק טוקנים להימור זה!", show_alert=True)
        return

    update_user_stat(uid, "balance", -bet_amount)
    
    mines_locations = random.sample(range(TOTAL_CELLS), mines_count)
    game_state = {
        "mines": mines_locations,
        "revealed": [],
        "bet": bet_amount,
        "active": True
    }
    
    save_game_state(uid, "mines", game_state)
    await render_mines_board(query, game_state, uid)

async def render_mines_board(query, game_state, uid):
    keyboard = []
    for i in range(0, TOTAL_CELLS, 5):
        row = []
        for j in range(i, i + 5):
            if j in game_state["revealed"]:
                icon = "💎" if j not in game_state["mines"] else "💥"
            else:
                icon = "❓"
            row.append(InlineKeyboardButton(icon, callback_data=f"mine_click_{j}"))
        keyboard.append(row)
    
    if game_state["active"]:
        if len(game_state["revealed"]) > 0:
            multiplier = round(1 + (len(game_state["revealed"]) * 0.25), 2)
            cash_out_val = int(game_state["bet"] * multiplier)
            keyboard.append([InlineKeyboardButton(f"💰 משוך רווח: {cash_out_val} 🪙 (x{multiplier})", callback_data="mine_cashout")])
    
    keyboard.append([InlineKeyboardButton("🔙 חזור לתפריט", callback_data="nav_home")])
    
    text = "💣 <b>MINES</b> 💣\n\nמצא את היהלומים! כל יהלום מעלה את המכפיל.\nזהירות מהמוקשים!"
    
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except Exception: pass

async def handle_mine_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data

    game_data = get_game_state(uid, "mines")
    if not game_data or not game_data["active"]:
        await query.answer("המשחק הסתיים או לא קיים.")
        return

    if data == "mine_cashout":
        multiplier = 1 + (len(game_data["revealed"]) * 0.25)
        win_amt = int(game_data["bet"] * multiplier)
        update_user_stat(uid, "balance", win_amt)
        update_user_stat(uid, "wins", 1)
        game_data["active"] = False
        r.delete(f"game:mines:{uid}")
        await query.answer(f"💵 זכית ב-{win_amt} טוקנים!", show_alert=True)
        from Main import start
        await start(update, context)
        return

    cell_idx = int(data.split("_")[-1])
    if cell_idx in game_data["revealed"]: return

    if cell_idx in game_data["mines"]:
        game_data["active"] = False
        game_data["revealed"].append(cell_idx)
        r.delete(f"game:mines:{uid}")
        await render_mines_board(query, game_data, uid)
        await query.message.reply_text("💥 <b>BOOM!</b> הפסדת את ההימור.")
    else:
        game_data["revealed"].append(cell_idx)
        save_game_state(uid, "mines", game_data)
        await render_mines_board(query, game_data, uid)
