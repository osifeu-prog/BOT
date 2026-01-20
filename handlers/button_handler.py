from utils.send_message import send_message

def handle_button(chat_id, callback_data):
    if callback_data == "button_pressed":
        text = "הכפתור נלחץ! הנה ההודעה שחוזרת."
        return send_message(chat_id, text)
