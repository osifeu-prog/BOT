import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

async def start_mines(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    # Get tier settings
    tier = user.get("tier", "Free")
    if tier == "Free":
        mines_count = 5
        multiplier = 1.1
    elif tier == "Pro":
        mines_count = 3
        multiplier = 1.3
    else:  # VIP
        mines_count = 2
        multiplier = 1.5
    
    # Initialize game state
    game_key = f"game:mines:{uid}"
    if not db.r.exists(game_key):
        # Create new game
        cells = list(range(25))
        mines = random.sample(cells, mines_count)
        diamonds = [cell for cell in cells if cell not in mines]
        
        game_state = {
            "mines": mines,
            "diamonds": diamonds,
            "revealed": [],
            "multiplier": multiplier,
            "bet": 100,
            "game_over": False,
            "won": False
        }
        
        db.r.setex(game_key, 600, json.dumps(game_state))  # 10 minutes expiry
    else:
        game_state = json.loads(db.r.get(game_key))
    
    # Create board
    board = []
    for i in range(25):
        if i in game_state["revealed"]:
            if i in game_state["mines"]:
                board.append("💣")
            else:
                board.append("💎")
        else:
            board.append("⬜")
    
    # Format board as 5x5 grid
    board_text = ""
    for row in range(5):
        row_cells = board[row*5:(row+1)*5]
        board_text += " ".join(row_cells) + "\n"
    
    game_text = f"""
💣 **משחק המוקשים**

{board_text}

💎 **דרגה:** {tier}
💰 **הימור:** {game_state['bet']} מטבעות
🎯 **מכפיל נוכחי:** x{game_state['multiplier']:.1f}
⚠️ **מוקשים:** {mines_count}

**הוראות:** לחץ על ריבוע כדי לחשוף יהלום. היזהר ממוקשים!
"""
    
    # Create keyboard
    keyboard = []
    for row in range(5):
        row_buttons = []
        for col in range(5):
            index = row * 5 + col
            if index in game_state["revealed"]:
                if index in game_state["mines"]:
                    row_buttons.append(InlineKeyboardButton("💣", callback_data=f"m_{index}"))
                else:
                    row_buttons.append(InlineKeyboardButton("💎", callback_data=f"m_{index}"))
            else:
                row_buttons.append(InlineKeyboardButton("⬜", callback_data=f"m_{index}"))
        keyboard.append(row_buttons)
    
    keyboard.append([
        InlineKeyboardButton("🏦 משוך רווחים", callback_data="m_cashout"),
        InlineKeyboardButton("🔄 משחק חדש", callback_data="play_mines")
    ])
    keyboard.append([InlineKeyboardButton("🏠 חזרה לתפריט", callback_data="start")])
    
    await query.edit_message_text(
        text=game_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_mine_click(update, context):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    
    if data == "m_cashout":
        await cashout_mines(update, context)
        return
    
    # Extract cell index
    cell_index = int(data.split("_")[1])
    
    game_key = f"game:mines:{uid}"
    if not db.r.exists(game_key):
        await query.answer("❌ המשחק נגמר או לא קיים! התחל משחק חדש.", show_alert=True)
        return
    
    game_state = json.loads(db.r.get(game_key))
    
    if game_state["game_over"]:
        await query.answer("❌ המשחק כבר נגמר! התחל משחק חדש.", show_alert=True)
        return
    
    if cell_index in game_state["revealed"]:
        await query.answer("❌ התא הזה כבר נחשף!", show_alert=True)
        return
    
    # Reveal cell
    game_state["revealed"].append(cell_index)
    
    if cell_index in game_state["mines"]:
        # Hit a mine - game over
        game_state["game_over"] = True
        game_state["won"] = False
        db.r.setex(game_key, 300, json.dumps(game_state))  # Keep for 5 minutes
        
        # Deduct bet
        bet = game_state["bet"]
        db.r.hincrby(f"user:{uid}:profile", "balance", -bet)
        db.log_transaction(uid, -bet, "Lost mines game")
        
        await query.answer("💣 נפגעת ממוקש! המשחק נגמר.", show_alert=True)
        await start_mines(update, context)  # Show updated board
        return
    
    # Found a diamond - increase multiplier
    game_state["multiplier"] *= 1.1
    db.r.setex(game_key, 600, json.dumps(game_state))
    
    await query.answer("💎 מצאת יהלום! המכפיל עלה.", show_alert=True)
    await start_mines(update, context)  # Show updated board

async def cashout_mines(update, context):
    query = update.callback_query
    uid = query.from_user.id
    
    game_key = f"game:mines:{uid}"
    if not db.r.exists(game_key):
        await query.answer("❌ המשחק נגמר או לא קיים!", show_alert=True)
        return
    
    game_state = json.loads(db.r.get(game_key))
    
    if game_state["game_over"]:
        await query.answer("❌ המשחק כבר נגמר!", show_alert=True)
        return
    
    # Calculate win
    bet = game_state["bet"]
    win_amount = int(bet * game_state["multiplier"])
    
    # Update balance
    db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
    db.log_transaction(uid, win_amount, f"Won mines game (x{game_state['multiplier']:.1f})")
    
    # Mark game as over
    game_state["game_over"] = True
    game_state["won"] = True
    db.r.setex(game_key, 300, json.dumps(game_state))
    
    await query.answer(f"🎉 משיכה מוצלחת! זכית ב-{win_amount} מטבעות.", show_alert=True)
    await start_mines(update, context)
