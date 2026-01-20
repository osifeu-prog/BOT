from keyboards.main_menu import main_menu_keyboard
from utils.send_message import send_message

def handle_start(chat_id):
    text = "ברוך הבא! לחץ על הכפתור כדי להמשיך."
    return send_message(chat_id, text, reply_markup=main_menu_keyboard())
