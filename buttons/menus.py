"""
buttons/menus.py
=================
תפריטים ראשיים ותפריט קורס.
"""
def get_main_menu():
    return [
        [{"text": "📦 רכישת הפרויקט", "callback_data": "menu_buy"}],
        [{"text": "📚 קורס מלא — כל הקבצים", "callback_data": "menu_course"}],
        [{"text": "🧠 איך הבוט עובד?", "callback_data": "menu_how"}],
        [{"text": "🎛 איך טלגרם עובד?", "callback_data": "menu_ui"}],
        [{"text": "🎰 שחק SLOTS", "callback_data": "menu_slots"}],
        [{"text": "🏆 טבלת מובילים", "callback_data": "menu_leaders"}],
        [{"text": "❓ תמיכה", "callback_data": "menu_help"}],
    ]

def get_course_menu():
    return [
        [{"text": "📘 מדריך התקנה", "callback_data": "course|INSTALL|0"}],
        [{"text": "🧠 איך הבוט עובד", "callback_data": "course|HOW_IT_WORKS|0"}],
        [{"text": "🎛 איך טלגרם עובד", "callback_data": "course|TELEGRAM_UI|0"}],
        [{"text": "🏗 ארכיטקטורה", "callback_data": "course|ARCH|0"}],
        [{"text": "🛠 התאמה אישית", "callback_data": "course|CUSTOMIZE|0"}],
        [{"text": "🎰 קוד משחק SLOTS", "callback_data": "course|SLOTS_CODE|0"}],
        [{"text": "🤖 Template לבוט חדש", "callback_data": "course|TEMPLATE|0"}],
        [{"text": "📂 כל הקוד מוסבר", "callback_data": "course|FULL_CODE|0"}],
    ]
