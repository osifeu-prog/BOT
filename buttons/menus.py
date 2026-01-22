from utils.config import ADMIN_USERNAME

def get_main_menu(lang, user_id):
    return [
        [{"text": "✨ צפה בדמו של המערכת (Mini App)", "web_app": {"url": "https://tradingview.com"}}], # דוגמה לאפליקציה חיצונית
        [{"text": "🎓 מסלולי הצטרפות", "callback_data": "menu_courses"}],
        [{"text": "💎 חבילות טוקנים", "callback_data": "menu_tokens"}],
        [{"text": "🎰 קזינו ומשחקים", "callback_data": "menu_games"}],
        [{"text": "🤝 שותפים", "callback_data": "menu_affiliate"}, {"text": "📊 דירוג", "callback_data": "menu_rank"}],
        [{"text": "🤖 רכישת בוט כזה", "callback_data": "buy_bot"}],
        [{"text": "📞 תמיכה", "url": f"https://t.me/{ADMIN_USERNAME}"}]
    ]
