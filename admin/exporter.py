import pandas as pd
from io import BytesIO
from app.database.manager import db

async def export_users_to_excel(update, context):
    uids = db.r.smembers("users_list")
    data = []
    for uid in uids:
        user_data = db.r.hgetall(f"user:{uid}:profile")
        data.append(user_data)
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=output,
        filename="nfty_crm_users.xlsx",
        caption="📂 דוח משתמשים מלא מהדאטהבייס"
    )
