"""
buttons/menus.py
=================
מגדיר את תפריט הכפתורים הראשי של הבוט.
"""

def get_main_menu(lang: str = "he"):
    """
    מחזיר רשימת כפתורים לתפריט הראשי.

    כרגע השפה לא משנה את הטקסטים,
    אבל אפשר להרחיב בעתיד לפי lang.
    """
    return [
        {"text": "📦 רכישת הפרויקט", "callback_data": "menu_buy"},
        {"text": "📚 קורס מלא — כל הקבצים", "callback_data": "menu_course"},
        {"text": "🧠 איך הבוט עובד?", "callback_data": "menu_how"},
        {"text": "🎛 איך טלגרם עובד?", "callback_data": "menu_ui"},
        {"text": "🎰 שחק SLOTS", "callback_data": "menu_slots"},
        {"text": "🏆 טבלת מובילים", "callback_data": "menu_leaders"},
        {"text": "❓ תמיכה", "callback_data": "menu_help"},
    ]
