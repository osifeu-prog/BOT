import os
from utils.send_message import send_message
from db.redis_client import test_redis
from db.postgres_client import init_table, insert_test_message, get_messages
from lessons.db_lesson import get_db_lesson_text
from payments.crypto_pay import create_lesson_invoice

# כאן אפשר בעתיד לשמור ב‑DB מי שילם
# כרגע נעשה גרסה פשוטה

def handle_button(chat_id, callback_data):
    print("Button pressed:", callback_data)

    if callback_data == "button_pressed":
        return send_message(chat_id, "הכפתור נלחץ! הנה ההודעה שחוזרת.")

    if callback_data == "test_redis":
        result = test_redis()
        return send_message(chat_id, f"Redis: {result}")

    if callback_data == "test_postgres":
        init = init_table()
        insert = insert_test_message("Hello from Telegram bot!")
        rows = get_messages()
        return send_message(chat_id, f"Postgres:\n{init}\n{insert}\n{rows}")

    if callback_data == "lesson_db":
        price = os.getenv("LESSON_DB_PRICE", "10")
        try:
            amount = float(price)
        except ValueError:
            amount = 10.0

        invoice_url = create_lesson_invoice(amount)
        if not invoice_url:
            return send_message(chat_id, "לא הצלחתי ליצור חשבונית תשלום כרגע. נסה שוב מאוחר יותר.")

        text = (
            f"מחיר השיעור: {amount} USDT\n"
            "לחץ על הקישור כדי לשלם:\n"
            f"{invoice_url}\n\n"
            "לאחר התשלום, שלח לי:  'קיבלתי שיעור DB'\n"
            "ואפתח לך את התוכן."
        )
        return send_message(chat_id, text)

    return send_message(chat_id, "לא זיהיתי את הכפתור.")
