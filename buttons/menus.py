from utils.i18n import LanguageCode, t


def get_main_menu(lang: LanguageCode):
    """
    התפריט הראשי של הבוט.
    Main menu of the bot.
    """
    return [
        [
            {
                "text": t(lang, "📚 קורס מלא", "📚 Full Course"),
                "callback_data": "menu_course"
            }
        ],
        [
            {
                "text": t(lang, "🎰 משחק SLOTS", "🎰 SLOTS Game"),
                "callback_data": "menu_slots"
            }
        ],
        [
            {
                "text": t(lang, "💰 רכישת הערכה", "💰 Purchase Kit"),
                "callback_data": "menu_buy"
            }
        ],
        [
            {
                "text": t(lang, "📞 תמיכה", "📞 Support"),
                "callback_data": "menu_support"
            }
        ]
    ]


def get_course_menu(lang: LanguageCode):
    """
    תפריט שיעורי הקורס.
    Course lessons menu.
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

        [{"text": t(lang, "📣 שיווק הבוט ללקוחות", "📣 Marketing the bot to clients"),
          "callback_data": "course|MARKETING_BOT|0"}],

        [{"text": t(lang, "💼 איך למכור את הערכה הלאה", "💼 How to resell the kit"),
          "callback_data": "course|RESELLING_KIT|0"}],
    ]


def get_support_menu(lang: LanguageCode):
    """
    תפריט תמיכה.
    Support menu.
    """
    return [
        [
            {
                "text": t(lang, "📩 שלח הודעה לאדמין", "📩 Contact Admin"),
                "callback_data": "menu_contact_admin"
            }
        ],
        [
            {
                "text": t(lang, "🔙 חזרה", "🔙 Back"),
                "callback_data": "menu_back"
            }
        ]
    ]


def get_buy_menu(lang: LanguageCode):
    """
    תפריט רכישה.
    Purchase menu.
    """
    return [
        [
            {
                "text": t(lang, "💎 רכישת הערכה המלאה", "💎 Buy Full Kit"),
                "callback_data": "menu_buy_full"
            }
        ],
        [
            {
                "text": t(lang, "🔙 חזרה", "🔙 Back"),
                "callback_data": "menu_back"
            }
        ]
    ]
