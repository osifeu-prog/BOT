from utils.i18n import t
from utils.config import BOT_USERNAME

def get_main_menu(lang, user_id):
    affiliate_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    return [
        [{"text": t(lang, "🛒 רכישת הקורס", "🛒 Buy Course"), "callback_data": "menu_buy"}],
        [{"text": t(lang, "🎰 משחק סלוטס", "🎰 Play Slots"), "callback_data": "menu_slots"}],
        [{"text": t(lang, "💰 שתף והרווח (לינק אישי)", "💰 Share & Earn"), "callback_data": "menu_share"}]
    ]
