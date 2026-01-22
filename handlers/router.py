import requests, time
from utils.config import TELEGRAM_API_URL, ADMIN_ID, OPENAI_KEY, BOT_USERNAME
from buttons.menus import get_main_menu, get_reply_keyboard
from db.users import update_user_economy, get_user_stats, transfer_slh

user_modes = {}
user_cooldowns = {}

async def handle_message(message):
    user_id = str(message["from"]["id"])
    text = message.get("text", "")
    now = time.time()

    if user_id in user_cooldowns and now - user_cooldowns[user_id] < 0.5: return
    user_cooldowns[user_id] = now

    # --- הפעלת בוט עם לינק זכיינות ---
    if text.startswith("/start game_sniper_"):
        referrer_id = text.split("_")[-1]
        if referrer_id != user_id:
            update_user_economy(referrer_id, slh_add=50) # הבונוס לזכיין
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": referrer_id, "text": "💰 **מכירה מוצלחת!** מישהו נכנס דרך הלינק שלך. הרווחת 50 SLH."})
        
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, "text": "🔫 **הגעת דרך משחק הצלף!**\nברוך הבא ל-Arcade.",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })
        return

    # פקודת תשלום (העברה בין חברים)
    if text.startswith("/pay"):
        try:
            _, target, amount = text.split()
            if transfer_slh(user_id, target, int(amount)):
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": f"✅ העברת {amount} SLH ל-{target}."})
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": target, "text": f"💰 קיבלת {amount} SLH מ-{user_id}!"})
            else:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "❌ יתרה לא מספקת או משתמש לא קיים."})
        except:
             requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "⚠️ פורמט שגוי. נסה: /pay ID AMOUNT"})
        return

    # --- פקודות רגילות ---
    if text == "/start" or text == "🔙 חזרה לתפריט":
        user_modes[user_id] = None
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id, 
            "text": "💎 **Diamond VIP Arcade**\nברוך הבא למערכת.",
            "reply_markup": {"inline_keyboard": get_main_menu('he', user_id)}
        })
        return

    # --- לוגיקת AI ---
    if "AI" in text or text == "🤖 שאל את ה-AI":
        user_modes[user_id] = "ai"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🤖 אנליסט מחובר. שאל חופשי."})
        return

    if user_modes.get(user_id) == "ai" and not text.startswith("/"):
        requests.post(f"{TELEGRAM_API_URL}/sendChatAction", json={"chat_id": user_id, "action": "typing"})
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "system", "content": "אתה מומחה פיננסי."}, {"role": "user", "content": text}]}
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers={"Authorization": f"Bearer {OPENAI_KEY}"}).json()
            reply = r.get('choices', [{}])[0].get('message', {}).get('content', "Error")
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": reply})
        except: pass
        return

    if text == "/admin" and user_id == str(ADMIN_ID):
         requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": user_id, "text": "🕶 **Welcome Master.**"})