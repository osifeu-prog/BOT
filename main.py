import os
from flask import Flask, request
from handlers.start_handler import handle_start
from handlers.button_handler import handle_button
from utils.send_message import send_message
from lessons.db_lesson import get_db_lesson_text

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Incoming update:", data)

        # הודעת טקסט רגילה
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            if text == "/start":
                return handle_start(chat_id)

            if text.strip() == "קיבלתי שיעור DB":
                return send_message(chat_id, get_db_lesson_text())

            if text.strip() == "סיימתי שלב":
                from db.user_progress import advance_user_step
                advance_user_step(chat_id)
                return send_message(chat_id, "מצוין! לחץ על 'המשך שיעור' כדי לעבור לשלב הבא.")

            if text.strip() == "מתנה שיעור DB":
                from db.user_progress import has_completed
                if not has_completed(chat_id):
                    return send_message(chat_id, "עליך להשלים את כל השלבים לפני שתוכל לתת את השיעור במתנה.")
                gift_link = f"https://t.me/{os.getenv('BOT_USERNAME')}?start=gift_db"
                return send_message(chat_id, f"🎁 הנה קישור מתנה:\n{gift_link}")

        # לחיצה על כפתור
        if "callback_query" in data:
            chat_id = data["callback_query"]["message"]["chat"]["id"]
            callback_data = data["callback_query"]["data"]
            return handle_button(chat_id, callback_data)

        return "ok"

    except Exception as e:
        print("ERROR in webhook:", e)
        return "error", 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)
