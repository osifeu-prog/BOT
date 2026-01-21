def get_main_menu(lang: str = "he"):
    # אפשר להרחיב לשפות נוספות בעתיד
    return [
        {"text": "📦 רכישת הפרויקט", "callback_data": "menu_buy"},
        {"text": "📘 איך הבוט עובד?", "callback_data": "menu_how"},
        {"text": "🎛 איך טלגרם עובד?", "callback_data": "menu_ui"},
        {"text": "🎰 שחק SLOTS", "callback_data": "menu_slots"},
        {"text": "🏆 טבלת מובילים", "callback_data": "menu_leaders"},
        {"text": "❓ תמיכה", "callback_data": "menu_help"},
    ]
