import requests
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY
from buttons.menus import get_main_menu, get_reply_keyboard, get_games_menu
from db.users import update_user_economy, get_user_stats

async def handle_message(message):
    user_id = str(message["from"]["id"])
    text = message.get("text", "")
    
    # מניעת קריסה אם המשתמש שולח משהו שהוא לא טקסט (כמו קובץ)
    if not text and "dice" not in message: return

    # לוגיקת משחקים (Dice)
    if "dice" in message:
        val, emo = message["dice"]["value"], message["dice"]["emoji"]
        update_user_economy(user_id, xp_add=10)
        if (emo == "🏀" and val >= 4) or (emo == "🎳" and val == 6) or (emo == "🎯" and val == 6):
            update_user_economy(user_id, slh_add=50)
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🔥 סנסציה! זכית ב-50 SLH!"})
        return

    # פקודות מערכת
    if text == "/start" or text == "🔙 חזרה":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🏆 **Diamond Arcade VIP**",
            "reply_markup": {"keyboard": get_reply_keyboard()["keyboard"], "resize_keyboard": True}
        })
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "בחר פעולה מהתפריט:",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })
        return

    if text == "💰 הארנק שלי":
        try:
            xp, slh, bal = get_user_stats(user_id)
            msg = f"💳 **הארנק הדיגיטלי**\n\n🪙 SLH: {slh}\n✨ XP: {xp}\n💰 יתרה: {bal}"
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})
        except:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "⚠️ הארנק בשיפוצים, נסה שוב בעוד רגע."})
        return

    if text == "🎮 משחקים ופרסים":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🎰 בחר משחק:", "reply_markup": {"inline_keyboard": get_games_menu()}
        })
        return

    # מענה AI חכם - רק אם זה לא אחד מהכפתורים
    system_buttons = ["💰 הארנק שלי", "🎮 משחקים ופרסים", "🎓 קורסים", "📞 עזרה", "/admin"]
    if not text.startswith("/") and text not in system_buttons and OPENAI_KEY:
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "אתה מומחה שוק ההון בבוט ה-VIP. ענה קצר ולעניין בעברית."},
                {"role": "user", "content": text}
            ]
        }
        res = requests.post("https://api.openai.com/v1/chat/completions", 
                            json=payload, headers={"Authorization": f"Bearer {OPENAI_KEY}"}).json()
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": res['choices'][0]['message']['content']})
