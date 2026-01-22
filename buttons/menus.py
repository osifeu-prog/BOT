from utils.i18n import t
from utils.config import BOT_USERNAME

def get_main_menu(lang, user_id):
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    return [
        [{"text": t(lang, "🛒 קנה קורס", "🛒 Buy Course"), "callback_data": "menu_buy"}],
        [{"text": t(lang, "🎰 סלוטס", "🎰 Slots"), "callback_data": "menu_slots"}],
        [{"text": t(lang, "💰 לינק שותפים", "💰 Affiliate Link"), "url": link}]
    ]

def get_buyer_menu(lang):
    return [[{"text": t(lang, "📚 הקורס שלי", "📚 My Course"), "callback_data": "menu_course"}]]
