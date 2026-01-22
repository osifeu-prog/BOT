import requests, random
from utils.config import TELEGRAM_API_URL, ADMIN_USERNAME, TOKEN_PACKS, PRICE_SH, TON_WALLET
from buttons.menus import get_games_menu

async def handle_callback(callback):
    user_id = callback["from"]["id"]
    data = callback["data"]
    
    requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

    # ניווט תפריטים
    if data == "menu_main":
        from buttons.menus import get_main_menu
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🏆 תפריט ראשי:", 
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })

    elif data == "menu_games":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🎰 **ברוך הבא לקזינו ה-VIP!**\nבחר משחק והטל פור:",
            "reply_markup": {"inline_keyboard": get_games_menu()}
        })

    # לוגיקת משחקים
    elif data.startswith("game_"):
        emoji_map = {"game_slots": "🎰", "game_dice": "🎲", "game_dart": "🎯", "game_hoop": "🏀", "game_bowling": "🎳"}
        emoji = emoji_map.get(data, "🎲")
        requests.post(f"{TELEGRAM_API_URL}/sendDice", json={"chat_id": user_id, "emoji": emoji})
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🔥 תוצאה מדהימה! צבור נקודות והחלף אותם בטוקנים."})

    # שותפים ודירוג
    elif data == "menu_affiliate":
        ref_link = f"https://t.me/OsifShop_bot?start={user_id}"
        msg = f"🤝 **תוכנית השותפים:**\n\nהזמן חברים וקבל עמלה על כל רכישה!\n\nלינק אישי: {ref_link}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg, "parse_mode": "Markdown"})

    elif data == "menu_rank":
        from db.connection import get_conn
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
        rows = cur.fetchall()
        cur.close(); conn.close()
        res = "📊 **טבלת מובילים:**\n\n" + "\n".join([f"👤 ID: {r[0]} - {r[1]}" for r in rows])
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": res})

    # רכישת בוט ותפריטים נוספים
    elif data == "buy_bot":
        msg = f"🤖 **רוצה מערכת כזו משלך?**\nצור קשר עם המתכנת: @{ADMIN_USERNAME}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": msg})

    elif data == "menu_tokens":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": f"💎 **חבילות טוקנים:**\n\n{TOKEN_PACKS}"})

    elif data == "menu_courses":
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": f"📚 מסלול VIP מלא: {PRICE_SH}\nשלח צילום מסך לאחר העברה ל-TON."})
