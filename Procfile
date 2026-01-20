from flask import Flask, request
import os
from handlers.start_handler import handle_start
from handlers.button_handler import handle_button

app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        text = data["message"].get("text", "")
        chat_id = data["message"]["chat"]["id"]

        if text == "/start":
            return handle_start(chat_id)

    if "callback_query" in data:
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        callback_data = data["callback_query"]["data"]
        return handle_button(chat_id, callback_data)

    return "ok"
