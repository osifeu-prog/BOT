from utils.config import ADMIN_USERNAME

def get_main_menu(lang, user_id):
    return [
        [{"text": "✨ צפה בדמו (Mini App)", "web_app": {"url": "https://slh-nft.com/"}}],
        [{"text": "📊 TradingView (חיצוני)", "web_app": {"url": "https://www.tradingview.com/"}}],
        [{"text": "🎓 מסלולי הצטרפות", "callback_data": "menu_courses"}],
        [{"text": "💎 חבילות טוקנים", "callback_data": "menu_tokens"}],
        [{"text": "🎰 קזינו ומשחקים", "callback_data": "menu_games"}],
        [{"text": "🤝 שותפים", "callback_data": "menu_affiliate"}, {"text": "📊 דירוג", "callback_data": "menu_rank"}],
        [{"text": "🤖 רכישת בוט כזה", "callback_data": "buy_bot"}],
        [{"text": "📞 תמיכה", "url": f"https://t.me/{ADMIN_USERNAME}"}]
    ]

def get_games_menu():
    return [
        [{"text": "🎰 מכונת מזל", "callback_data": "game_slots"}, {"text": "🎲 קוביות", "callback_data": "game_dice"}],
        [{"text": "🎯 קליעה למטרה", "callback_data": "game_dart"}, {"text": "🏀 כדורסל", "callback_data": "game_hoop"}],
        [{"text": "🎳 באולינג", "callback_data": "game_bowling"}],
        [{"text": "🔙 חזרה לתפריט", "callback_data": "menu_main"}]
    ]
