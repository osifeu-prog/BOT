import requests, time
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY

# מילון לשמירת זמני הודעות (Rate Limiting)
user_last_msg = {}

async def handle_message(message):
    user_id = message["from"]["id"]
    text = message.get("text", "")

    # הגנת הצפה (Rate Limit): הודעה אחת ל-2 שניות
    current_time = time.time()
    if user_id in user_last_msg and current_time - user_last_msg[user_id] < 1.5:
        return 
    user_last_msg[user_id] = current_time

    if text.startswith("/start"):
        from buttons.menus import get_main_menu
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "🏆 **ברוך הבא לנבחרת ה-VIP**\nבחר אפשרות מהתפריט:",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })
        return

    # הוספת אפקט "מקליד..." בזמן פנייה ל-AI
    if not text.startswith("/") and OPENAI_KEY:
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        
        # לוגיקת AI (כפי שהגדרנו קודם)
        ai_url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": "Expert crypto/stock mentor."}, {"role": "user", "content": text}]
        }
        try:
            res = requests.post(ai_url, json=payload, headers=headers).json()
            reply = res['choices'][0]['message']['content']
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": reply})
        except:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "משהו השתבש במוח הדיגיטלי שלי... נסה שוב."})
