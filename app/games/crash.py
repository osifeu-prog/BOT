import random
import asyncio
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

async def start_crash(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    # Check balance
    balance = int(user.get("balance", 0))
    bet_amount = 100
    
    if balance < bet_amount:
        await query.answer("❌ אין מספיק מטבעות! יתרה מינימלית: 100 🪙", show_alert=True)
        return
    
    # Deduct bet
    db.r.hincrby(f"user:{uid}:profile", "balance", -bet_amount)
    
    # Generate crash point
    crash_point = round(random.uniform(1.1, 10.0), 2)
    
    # Create game state
    game_state = {
        "players": {str(uid): {"bet": bet_amount, "cashed": False}},
        "crash_point": crash_point,
        "current_multiplier": 1.0,
        "active": True,
        "bet_amount": bet_amount
    }
    
    db.r.setex(f"game:crash:{uid}", 300, json.dumps(game_state))
    
    keyboard = [
        [InlineKeyboardButton("💰 משוך רווחים", callback_data="crash_cashout")],
        [InlineKeyboardButton("🏠 חזרה", callback_data="start")]
    ]
    
    await query.edit_message_text(
        text="🚀 **משחק Crash התחיל!**\n\nהמרווח עולה... לחץ על 'משוך' לפני שהמטוס מתרסק!\n\n📈 מכפיל נוכחי: 1.00x",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    # Start game loop in background
    asyncio.create_task(run_crash_game(query, uid, game_state))

async def run_crash_game(query, uid, game_state):
    multiplier = 1.0
    
    while multiplier < game_state["crash_point"] and game_state["active"]:
        await asyncio.sleep(1)  # Update every second
        multiplier += 0.1
        multiplier = round(multiplier, 2)
        
        game_state["current_multiplier"] = multiplier
        db.r.setex(f"game:crash:{uid}", 300, json.dumps(game_state))
        
        # Update message
        try:
            await query.edit_message_text(
                text=f"🚀 **משחק Crash**\n\n📈 מכפיל נוכחי: {multiplier:.2f}x\n💥 נקודת התרסקות: {game_state['crash_point']}x\n\nלחץ 'משוך' לקבלת הרווחים!",
                reply_markup=query.message.reply_markup
            )
        except:
            break  # Message might be edited elsewhere
    
    if game_state["active"]:
        # Crashed without cashing out
        await query.edit_message_text(
            text=f"💥 המטוס התרסק ב-{multiplier:.2f}x!\n😔 הפסדת {game_state['bet_amount']} מטבעות.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 נסה שוב", callback_data="play_crash")],
                [InlineKeyboardButton("🏠 חזרה", callback_data="start")]
            ])
        )

async def handle_crash_click(update, context):
    query = update.callback_query
    data = query.data
    
    if data == "crash_cashout":
        await crash_cashout(update, context)

async def crash_cashout(update, context):
    query = update.callback_query
    uid = query.from_user.id
    
    game_key = f"game:crash:{uid}"
    if not db.r.exists(game_key):
        await query.answer("❌ המשחק נגמר או לא קיים!", show_alert=True)
        return
    
    game_state = json.loads(db.r.get(game_key))
    
    if not game_state["active"]:
        await query.answer("❌ המשחק כבר נגמר!", show_alert=True)
        return
    
    # Cash out
    game_state["active"] = False
    multiplier = game_state["current_multiplier"]
    bet_amount = game_state["bet_amount"]
    win_amount = int(bet_amount * multiplier)
    
    # Update balance
    db.r.hincrby(f"user:{uid}:profile", "balance", win_amount)
    db.log_transaction(uid, win_amount, f"Cashed out crash game at x{multiplier}")
    
    db.r.setex(game_key, 300, json.dumps(game_state))
    
    await query.edit_message_text(
        text=f"🎉 משיכה מוצלחת ב-{multiplier:.2f}x!\n💰 זכית ב-{win_amount} מטבעות!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 נסה שוב", callback_data="play_crash")],
            [InlineKeyboardButton("🏠 חזרה", callback_data="start")]
        ])
    )
