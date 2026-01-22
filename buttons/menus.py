from utils.i18n import t
import os

def get_main_menu(lang, user_id):
    return [
        [{"text": "🚀 הגישה לנבחרת ה-VIP", "callback_data": "menu_buy"}],
        [{"text": "🤝 מרכז שותפים (רווחים)", "callback_data": "menu_affiliate"}, {"text": "📊 הדירוג שלי", "callback_data": "menu_rank"}],
        [{"text": "🎰 קזינו סוחרים", "callback_data": "menu_games"}, {"text": "🧮 מחשבון סיכונים", "callback_data": "menu_tools"}],
        [{"text": "📞 תמיכה ומענה אנושי", "url": "https://t.me/osifeu"}]
    ]

def get_games_menu():
    return [
        [{"text": "🎰 סלוטס יהלומים", "callback_data": "menu_slots"}],
        [{"text": "🎡 גלגל המזל", "callback_data": "menu_wheel"}],
        [{"text": "🔙 חזרה", "callback_data": "menu_main"}]
    ]
