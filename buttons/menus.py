from utils.config import ADMIN_USERNAME

def get_reply_keyboard():
    # מקלדת קבועה שמופיעה במקום המקלדת הרגילה
    return {
        "keyboard": [
            [{"text": "🎮 משחקים ופרסים"}, {"text": "💰 הארנק שלי"}],
            [{"text": "🎓 קורסים"}, {"text": "📞 עזרה"}]
        ],
        "resize_keyboard": True
    }

def get_main_menu(lang, user_id):
    return [
        [{"text": "✨ צפה בדמו (Mini App)", "web_app": {"url": "https://slh-nft.com/"}}],
        [{"text": "🤝 הזמן חברים (בונוס XP)", "callback_data": "menu_affiliate"}],
        [{"text": "📊 טבלת מובילים", "callback_data": "menu_rank"}],
        [{"text": "🤖 רכישת בוט כזה", "callback_data": "buy_bot"}]
    ]

def get_games_menu():
    return [
        [{"text": "🎰 סלוטס", "callback_data": "game_slots"}, {"text": "🎯 מטרה", "callback_data": "game_dart"}],
        [{"text": "🎳 באולינג", "callback_data": "game_bowling"}, {"text": "🏀 כדורסל", "callback_data": "game_hoop"}],
        [{"text": "🔙 חזרה", "callback_data": "menu_main"}]
    ]
