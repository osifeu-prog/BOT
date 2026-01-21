from utils.telegram import send_message
from db.events import log_event

async def echo_handler(message):
    chat = message["chat"]
    user_id = chat["id"]
    text = message.get("text", "")

    log_event(user_id, "message", "echo", payload=text)

    await send_message(user_id, f"הודעתך: {text}")
