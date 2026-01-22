from utils.i18n import t
import os

def get_main_menu(lang, user_id):
    bot_username = os.getenv("BOT_USERNAME", "OsifShopBot")
    share_link = f"https://t.me/{bot_username}?start={user_id}"
    
    return [
        [{"text": "🚀 " + t(lang, "גישה לקורס הדיגיטלי", "Access Digital Course"), "callback_data": "menu_buy"}],
        [{"text": "💎 " + t(lang, "חנות יהלומים (Slots)", "Diamond Shop"), "callback_data": "menu_slots"}],
        [{"text": "🤝 " + t(lang, "תוכנית שותפים (50% עמלה)", "Affiliate Program"), "url": share_link}],
        [{"text": "📞 " + t(lang, "תמיכה טכנית", "Support"), "url": "https://t.me/osifeu"}]
    ]

def get_buyer_menu(lang):
    return [
        [{"text": "📚 " + t(lang, "צפייה בתכני הקורס", "View Course Content"), "url": "https://google.com"}], # החלף בלינק לקורס
        [{"text": "👥 " + t(lang, "קבוצת VIP", "VIP Group"), "url": "https://t.me/osifeu"}]
    ]

def get_admin_menu():
    return [
        [{"text": "📊 סטטיסטיקה", "callback_data": "admin_stats"}, {"text": "📢 הודעה לכולם", "callback_data": "admin_broadcast"}],
        [{"text": "⚙️ הגדרות מערכת", "callback_data": "admin_settings"}]
    ]
