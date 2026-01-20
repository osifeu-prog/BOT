import random, json, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.manager import db

async def start_mines(update, context):
    query = update.callback_query
    uid = query.from_user.id
    user = db.get_user(uid)
    
    # הגדרות לפי Tier
    tier_config = {
        "Free": {"mines": 5, "mult": 1.1},
        "Pro": {"mines": 3, "mult": 1.3},
        "VIP": {"mines": 2, "mult": 1.5}
    }
    
    tier = user.get("tier", "Free")
    config = tier_config.get(tier, tier_config["Free"])
    
    state = {
        "mines": random.sample(range(25), config["mines"]),
        "revealed": [],
        "mult": config["mult"],
        "active": True
    }
    db.r.set(f"game:mines:{uid}", json.dumps(state), ex=600)
    await render_board(query, state)

async def handle_mine_click(update, context):
    query = update.callback_query
    uid = query.from_user.id
    cell = int(query.data.split("_")[-1])
    
    game_data = db.r.get(f"game:mines:{uid}")
    if not game_data: return
    state = json.loads(game_data)
    
    if cell in state["mines"]:
        await query.edit_message_text("💥 בום! הפסדת. נסה שוב?")
        db.r.delete(f"game:mines:{uid}")
    else:
        state["revealed"].append(cell)
        db.r.set(f"game:mines:{uid}", json.dumps(state), ex=600)
        await render_board(query, state)

async def render_board(query, state):
    kb = []
    for i in range(0, 25, 5):
        row = [InlineKeyboardButton("💎" if j in state["revealed"] else "❓", 
               callback_data=f"m_c_{j}") for j in range(i, i+5)]
        kb.append(row)
    await query.edit_message_text(f"💎 מצא את היהלומים! (Tier: {state.get('tier', 'Free')})", reply_markup=InlineKeyboardMarkup(kb))
