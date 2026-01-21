from utils.i18n import LanguageCode, t

def get_course_menu(lang: LanguageCode):
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
