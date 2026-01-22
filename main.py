from fastapi import FastAPI, Request
from utils.config import TELEGRAM_API_URL, PORT
from handlers.router import handle_message, user_modes
from handlers.callback_router import handle_callback
import uvicorn, os

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        
        # טיפול בטקסט רגיל
        if "message" in data:
            await handle_message(data["message"])
            
        # טיפול בכפתורים (Callbacks)
        elif "callback_query" in data:
            await handle_callback(data["callback_query"])
            
        return {"status": "ok"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error"}

@app.get("/")
def read_root():
    return {"status": "Diamond VIP Bot Online"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))