"""Multi-language support"""

TRANSLATIONS = {
    'en': {
        'welcome': "👋 Welcome {first_name}!\n💰 Balance: ${balance:.2f}",
        'casino': '🎰 Casino',
        'invest': '💰 Invest',
        'shop': '🛍️ Shop',
        'referral': '👥 Referral',
        'balance': '💰 Balance',
    },
    'he': {
        'welcome': "👋 שלום {first_name}!\n💰 יתרה: ${balance:.2f}",
        'casino': '🎰 קזינו',
        'invest': '💰 השקעה',
        'shop': '🛍️ חנות',
        'referral': '👥 הפניות',
        'balance': '💰 יתרה',
    },
    'ru': {
        'welcome': "👋 Привет {first_name}!\n💰 Баланс: ${balance:.2f}",
        'casino': '🎰 Казино',
        'invest': '💰 Инвестиции',
        'shop': '🛍️ Магазин',
        'referral': '👥 Рефералы',
        'balance': '💰 Баланс',
    }
}

def get_text(key, lang='en'):
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
