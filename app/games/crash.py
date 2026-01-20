import random, asyncio, json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

async def start_crash(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    # הגדרת משחק חדש
    crash_point = round(random.uniform(1.1, 10.0), 2)
    game_state = {
        "players": {str(uid): {"bet": 100, "cashed": False}},
        "crash_point": crash_point,
        "current_multiplier": 1.0,
        "active": True
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
    
    # הרצת לולאת המשחק
    await run_crash_game(query, uid, game_state)

async def run_crash_game(query, uid, game_state):
    multiplier = 1.0
    while multiplier < game_state["crash_point"] and game_state["active"]:
        await asyncio.sleep(1)
        multiplier += 0.1
        game_state["current_multiplier"] = round(multiplier, 2)
        db.r.setex(f"game:crash:{uid}", 300, json.dumps(game_state))
        
        # עדכון הודעה
        await query.edit_message_text(
            text=f"🚀 **משחק Crash**\n\n📈 מכפיל נוכחי: {multiplier:.2f}x\n💥 נקודת התרסקות: {game_state['crash_point']}x\n\nלחץ 'משוך' לקבלת הרווחים!",
            reply_markup=query.message.reply_markup
        )
    
    if game_state["active"]:
        await query.edit_message_text("💥 המטרס התרסק! כל הכסף אבד.")
