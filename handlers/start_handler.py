from utils.send_message import send_message
from keyboards.first_button import first_button

def handle_start(chat_id):
    return send_message(
        chat_id,
        "ברוך הבא! לחץ על הכפתור כדי להתחיל.",
        reply_markup=first_button()
    )
