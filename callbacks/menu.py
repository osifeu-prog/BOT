from utils.telegram import send_message
from db.slots import play_slots
from utils.config import TON_WALLET, PRICE_SH

async def menu_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    
    if data == "menu_slots":
        await play_slots(user_id, "he")
    
    elif data == "menu_buy":
        pay_msg = f"💳 **רכישת הקורס המלא**\n\nמחיר: {PRICE_SH} ש''ח\nכתובת TON למשלוח:\n{TON_WALLET}\n\nלאחר ההעברה, שלח צילום מסך לאדמין לאישור."
        send_message(user_id, pay_msg)
