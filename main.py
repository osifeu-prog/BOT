from fastapi import FastAPI, Request
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message
from handlers.callback_router import handle_callback
import uvicorn, os

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        
        # זיהוי סוג ההודעה (טקסט או כפתור) ושליחה לראוטר המתאים
        if "message" in data:
            await handle_message(data["message"])
        elif "callback_query" in data:
            await handle_callback(data["callback_query"])
            
        return {"status": "ok"}
    except Exception as e:
        print(f"Error in webhook: {e}")
        return {"status": "error"}

@app.get("/")
def read_root():
    return {"status": "Diamond VIP Bot is Running Smoothly"}

if __name__ == "__main__":
    # שימוש בפורט מהקונפיגורציה המתוקנת
    uvicorn.run(app, host="0.0.0.0", port=PORT)