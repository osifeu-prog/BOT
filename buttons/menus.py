def get_main_menu(lang='he', user_id=''):
    return [
        [{"text": "🎮 אולם המשחקים & זכיינות", "callback_data": "open_games"}, {"text": "💰 הארנק שלי", "callback_data": "wallet"}],
        [{"text": "🎓 קורסים והשכלה", "callback_data": "open_courses"}, {"text": "📈 TradingView Live", "web_app": {"url": "https://www.tradingview.com/chart"}}],
        [{"text": "🏆 טבלת מובילים", "callback_data": "leaderboard"}, {"text": "🤖 שאל את ה-AI", "callback_data": "ai_mode"}],
        [{"text": "📞 תמיכה ועזרה", "callback_data": "help"}, {"text": "🛒 רכישת בוט כזה", "url": "https://t.me/OsifShopbot"}]
    ]

def get_games_menu(user_owned_games=[]):
    menu = [
        [{"text": "🎲 קוביות המזל (חינם)", "callback_data": "play_dice"}],
        [{"text": "🎰 סלוט משין (50 SLH)", "callback_data": "play_slots"}]
    ]
    # בדיקה אם המשתמש קנה את הזיכיון למשחק הצלף
    if "sniper" in user_owned_games:
        menu.append([{"text": "🔫 הצלף (שלך!) - שתף והרווח", "callback_data": "share_sniper"}])
    else:
        menu.append([{"text": "🔒 קנה זיכיון 'הצלף' (500 SLH)", "callback_data": "buy_sniper"}])
    
    menu.append([{"text": "🔙 חזרה לתפריט הראשי", "callback_data": "back_home"}])
    return menu

def get_wallet_actions(user_id):
    return [
        [{"text": "📤 העבר לחבר", "callback_data": "transfer_start"}, {"text": "📥 בקש תשלום", "callback_data": "request_pay"}],
        [{"text": "📜 היסטוריית פעולות", "callback_data": "history"}],
        [{"text": "🔙 חזרה", "callback_data": "back_home"}]
    ]

def get_reply_keyboard():
    return {"keyboard": [[{"text": "🔙 חזרה לתפריט"}]], "resize_keyboard": True}