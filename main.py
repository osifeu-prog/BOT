import os
from flask import Flask, request
from handlers.start_handler import handle_start
from handlers.button_handler import handle_button
from utils.send_message import send_message
from lessons.db_lesson import get_db_lesson_text

# בתוך webhook(), אחרי if text == "/start":

if text.strip() == "קיבלתי שיעור DB":
    # כאן בעתיד אפשר לבדוק ב‑DB אם המשתמש באמת שילם
    # כרגע – נפתח לו את השיעור תמיד
    return send_message(chat_id, get_db_lesson_text())

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
