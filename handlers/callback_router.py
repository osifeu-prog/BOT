import requests
from utils.config import TELEGRAM_API_URL, BOT_USERNAME
from buttons.menus import get_main_menu, get_games_menu, get_wallet_actions
from db.users import update_user_economy, get_user_stats, get_leaderboard

# הדמייה של מסד נתונים למשחקים שנרכשו (בפרודקשן זה יהיה ב-SQL)
user_inventory = {} 

async def handle_callback(callback_query):
    user_id = str(callback_query["from"]["id"])
    data = callback_query.get("data", "")
    chat_id = callback_query["message"]["chat"]["id"]
    msg_id = callback_query["message"]["message_id"]

    # פונקציית עזר לעדכון הודעה
    def edit_text(text, markup=None):
        payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "Markdown"}
        if markup: payload["reply_markup"] = markup
        requests.post(f"{TELEGRAM_API_URL}/editMessageText", json=payload)

    # --- ניווט ראשי ---
    if data == "back_home":
        edit_text("💎 **Diamond VIP Arcade**\nבחר פעולה:", {"inline_keyboard": get_main_menu('he', user_id)})
    
    elif data == "wallet":
        xp, slh, bal, _ = get_user_stats(user_id)
        msg = f"💳 **הארנק שלך**\n\n🪙 **SLH:** {slh}\n✨ **XP:** {xp}\n💰 **יתרה:** {bal}"
        edit_text(msg, {"inline_keyboard": get_wallet_actions(user_id)})

    elif data == "history":
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"], "text": "📜 אין פעולות אחרונות להצגה", "show_alert": True})

    elif data == "transfer_start":
        edit_text("📤 **העברת מטבעות**\nכדי להעביר, הקלד הודעה:\n/pay ID AMOUNT\nלדוגמה: /pay 123456 50")

    elif data == "leaderboard":
        top = get_leaderboard()
        msg = "🏆 **TOP 5 WHALES**\n\n" + "\n".join([f"🥇 {u[0]}... - {u[1]} SLH" for i, u in enumerate(top)])
        edit_text(msg, {"inline_keyboard": [[{"text": "🔙 חזרה", "callback_data": "back_home"}]]})

    elif data == "open_courses":
        edit_text("🎓 **האקדמיה**\nכאן יופיעו הקורסים שלך.\nבקרוב!", {"inline_keyboard": [[{"text": "🔙 חזרה", "callback_data": "back_home"}]]})

    elif data == "help":
         edit_text("📞 **מרכז תמיכה**\nלכל בעיה פנה ל-@OsifUngar", {"inline_keyboard": [[{"text": "🔙 חזרה", "callback_data": "back_home"}]]})

    # --- משחקים וזכיינות ---
    elif data == "open_games":
        owned = user_inventory.get(user_id, [])
        edit_text("🎮 **Arcade & Franchise Store**\nבחר משחק לשחק או קנה זיכיון להפצה:", {"inline_keyboard": get_games_menu(owned)})

    elif data == "play_dice":
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": "🎲"})
        update_user_economy(user_id, xp_add=5)
    
    elif data == "buy_sniper":
        xp, slh, bal, _ = get_user_stats(user_id)
        if slh >= 500:
            update_user_economy(user_id, slh_add=-500)
            if user_id not in user_inventory: user_inventory[user_id] = []
            user_inventory[user_id].append("sniper")
            edit_text("✅ **רכשת את הזיכיון!**\nעכשיו אתה יכול להפיץ את המשחק ולהרוויח.", {"inline_keyboard": get_games_menu(["sniper"])})
        else:
            requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"], "text": "❌ אין לך מספיק SLH (צריך 500)", "show_alert": True})

    elif data == "share_sniper":
        link = f"https://t.me/{BOT_USERNAME}?start=game_sniper_{user_id}"
        edit_text(f"🔫 **הלינק שלך להפצה:**\n{link}\n\nכל משתמש שייכנס דרך הלינק הזה יזכה אותך ב-50 SLH!", {"inline_keyboard": [[{"text": "🔙 חזרה", "callback_data": "open_games"}]]})

    elif data == "ai_mode":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "🤖 **ה-AI הופעל.** כתוב את שאלתך כעת."})

    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_query["id"]})