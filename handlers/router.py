import requests, datetime
from utils.config import TELEGRAM_API_URL, ADMIN_ID

def handle_message(message):
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    dice = message.get("dice")

    # משחקי אנימציה - זיהוי תוצאה
    if dice:
        v, e = dice.get("value"), dice.get("emoji")
        win = 1000 if (e == "🎰" and v in [1, 22, 43, 64]) or (e == "🎯" and v == 6) or (e == "🏀" and v == 5) else 0
        if win > 0:
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": f"🎊 וואו! זכית ב-{win} SLH!"})
        return

    if text.startswith("/start"):
        msg = "💎 **DIAMOND ELITE PRO v11.0**\n\nמערכת ה-AI והמסחר המלאה שלך.\nבחר באופציה המבוקשת:"
        kb = {"inline_keyboard": [
            [{"text": "💳 ארנק ומיני-אפ", "web_app": {"url": "https://bot-production-2668.up.railway.app/"}}],
            [{"text": "🤖 AI יועץ (39 ש''ח ל-PRO)", "callback_data": "ai_vip_info"}],
            [{"text": "🎰 מתחם משחקים", "callback_data": "games_hub"}, {"text": "📈 יומן שוק", "callback_data": "market_journal"}],
            [{"text": "🏆 מובילים", "callback_data": "top_players"}, {"text": "👥 קבוצות ו-Earn", "callback_data": "earn_groups"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    user_id = str(callback["from"]["id"])
    data = callback["data"]
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    if data == "ai_vip_info":
        msg = "🎓 **עוזר AI פיננסי PRO**\n\nבפתיחת מסלול זה (39 ש''ח חד-פעמי) תקבל:\n✅ מדריך 'איך לייצר רווחים מהבוט'\n✅ ניהול תיק השקעות אוטומטי\n✅ גישה ל-OpenAI ללא הגבלה\n\nלהפעלה, העבר 39 ש''ח ב-Bit/TON ושלח צילום מסך לאדמין."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})

    elif data == "games_hub":
        kb = {"inline_keyboard": [
            [{"text": "🎰 סלוט", "callback_data": "play_🎰"}, {"text": "🏀 כדורסל", "callback_data": "play_🏀"}],
            [{"text": "🎯 קליעה למטרה", "callback_data": "play_🎯"}, {"text": "🎳 באולינג", "callback_data": "play_🎳"}]
        ]}
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": "בחר משחק:", "reply_markup": kb})

    elif data.startswith("play_"):
        emoji = data.split("_")[1]
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": chat_id, "emoji": emoji})

    elif data == "market_journal":
        msg = "📅 **יומן שוק אחרון:**\n1. ביטקוין: תמיכה ב-98k\n2. סנטימנט: חיובי מאוד\n3. עדכון: נוספו משימות חדשות!"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

    elif data == "top_players":
        msg = "🏆 **מובילי היהלומים:**\n1. Osif - 50,000 SLH\n2. AI_Bot - 20,000 SLH"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg})

    elif data == "earn_groups":
        msg = "👥 **קהילה ומשימות:**\n- [קבוצת דיונים](https://t.me/example)\n- [ערוץ עדכונים](https://t.me/example)\n\nהצטרף וקבל 1000 SLH!"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": msg, "disable_web_page_preview": False, "parse_mode": "Markdown"})
