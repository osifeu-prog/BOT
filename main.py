import os
from flask import Flask, request
from handlers.start_handler import handle_start
from handlers.button_handler import handle_button

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
