"""
menus.py
========
HE: בניית תפריטי Inline לפי שפה.
EN: Building inline menus by language.
"""

from utils.i18n import LanguageCode, t

def get_main_menu(lang: LanguageCode):
    """
    HE: תפריט ראשי.
    EN: Main menu.
    """
    return [
        [{"text": t(lang, "📦 רכישת הערכה", "📦 Buy the Starter Kit"), "callback_data": "menu_buy"}],
        [{"text": t(lang, "📚 קורס מלא", "📚 Full Course"), "callback_data": "menu_course"}],
        [{"text": t(lang, "🧠 איך הבוט עובד?", "🧠 How the bot works"), "callback_data": "menu_how"}],
        [{"text": t(lang, "🎛 איך טלגרם עובד?", "🎛 How Telegram UI works"), "callback_data": "menu_ui"}],
        [{"text": t(lang, "🎰 משחק SLOTS", "🎰 SLOTS Game"), "callback_data": "menu_slots"}],
        [{"text": t(lang, "🏆 טבלת מובילים", "🏆 Leaderboard"), "callback_data": "menu_leaders"}],
        [{"text": t(lang, "❓ תמיכה / יצירת קשר", "❓ Support / Contact"), "callback_data": "menu_help"}],
    ]

def get_course_menu(lang: LanguageCode):
    """
    HE: תפריט שיעורי הקורס.
    EN: Course lessons menu.
    """
    return [
        [{"text": t(lang, "📘 התקנה (Railway + Webhook)", "📘 Installation (Railway + Webhook)"),
          "callback_data": "course|INSTALL|0"}],
        [{"text": t(lang, "🧠 איך הבוט עובד", "🧠 How the bot works"),
          "callback_data": "course|HOW_IT_WORKS|0"}],
        [{"text": t(lang, "🎛 ממשק טלגרם", "🎛 Telegram UI"),
          "callback_data": "course|TELEGRAM_UI|0"}],
        [{"text": t(lang, "🏗 ארכיטקטורה", "🏗 Architecture"),
          "callback_data": "course|ARCH|0"}],
        [{"text": t(lang, "🛠 התאמה אישית", "🛠 Customization"),
          "callback_data": "course|CUSTOMIZE|0"}],
        [{"text": t(lang, "🎰 קוד משחק SLOTS", "🎰 SLOTS Code"),
          "callback_data": "course|SLOTS_CODE|0"}],
        [{"text": t(lang, "🤖 תבנית לבוט חדש", "🤖 Bot Template"),
          "callback_data": "course|TEMPLATE|0"}],
        [{"text": t(lang, "📂 כל הקוד מוסבר", "📂 Full Code Explained"),
          "callback_data": "course|FULL_CODE|0"}],
    ]
