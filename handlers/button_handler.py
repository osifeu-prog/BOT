from utils.send_message import send_message

def handle_button(chat_id, callback_data):
    print("Button pressed:", callback_data)

    if callback_data == "button_pressed":
        text = "הכפתור נלחץ! הנה ההודעה שחוזרת."
        return send_message(chat_id, text)

    return send_message(chat_id, "לא זיהיתי את הכפתור.")
