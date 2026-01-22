from utils.i18n import t

def get_main_menu(lang):
    return [
        [{"text": t(lang, "🛒 רכישת הקורס", "🛒 Buy Course"), "callback_data": "menu_buy"}],
        [{"text": t(lang, "🎰 משחק סלוטס", "🎰 Play Slots"), "callback_data": "menu_slots"}],
        [{"text": t(lang, "📖 שיעור ניסיון", "📖 Free Lesson"), "callback_data": "course|intro"}]
    ]

def get_buyer_menu(lang):
    return [
        [{"text": t(lang, "🎓 כניסה לקורס המלא", "🎓 Full Course Access"), "callback_data": "course|main"}],
        [{"text": t(lang, "📥 הורדת קוד (ZIP)", "📥 Download ZIP"), "callback_data": "menu_download"}]
    ]
