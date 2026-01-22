from utils.config import ADMIN_USERNAME

def get_main_menu(lang, user_id):
    return [
        [{"text": "🎓 קורסים ומסלולי הצטרפות", "callback_data": "menu_courses"}],
        [{"text": "💎 רכישת טוקנים (Packs)", "callback_data": "menu_tokens"}],
        [{"text": "🤝 שותפים ורווחים", "callback_data": "menu_affiliate"}, {"text": "📊 הדירוג שלי", "callback_data": "menu_rank"}],
        [{"text": "🎰 קזינו ומשחקים", "callback_data": "menu_games"}],
        [{"text": "🤖 רכישת בוט כזה לעצמך", "callback_data": "buy_bot"}],
        [{"text": "📞 תמיכה ומענה אנושי", "url": f"https://t.me/{ADMIN_USERNAME}"}]
    ]

def get_courses_menu():
    return [
        [{"text": "🏆 מסלול VIP מלא (99)", "callback_data": "buy_vip"}],
        [{"text": "📚 שיעור בודד (22)", "callback_data": "buy_lesson"}],
        [{"text": "🔙 חזרה", "callback_data": "menu_main"}]
    ]
