from utils.telegram import send_message
from db.slots import play_slots
from utils.config import PRICE_SH, TON_WALLET

async def menu_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    
    if data == "menu_slots":
        play_slots(user_id)
    elif data == "menu_buy":
        msg = f"💳 שלח {PRICE_SH} שח לכתובת:\n`{TON_WALLET}`\nושלח צילום מסך לאדמין."
        send_message(user_id, msg)
