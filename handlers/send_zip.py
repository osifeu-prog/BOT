from utils.telegram import send_message
from utils.config import ZIP_LINK

async def send_zip(chat):
    user_id = chat["id"]
    await send_message(user_id, f"📦 הנה הקובץ שלך:\n{ZIP_LINK}")
