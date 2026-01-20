from utils.send_message import send_message
from keyboards.second_stage import second_stage_buttons

def handle_button(chat_id, callback_data):

    if callback_data == "start_flow":
        return send_message(
            chat_id,
            "מצוין! עכשיו בחר אחת מהאפשרויות:",
            reply_markup=second_stage_buttons()
        )

    if callback_data == "option_1":
        return send_message(chat_id, "בחרת באפשרות 1!")

    if callback_data == "option_2":
        return send_message(chat_id, "בחרת באפשרות 2!")

    return send_message(chat_id, "לא זיהיתי את הבחירה.")
