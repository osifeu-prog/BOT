from fastapi import FastAPI, Request
from handlers.router import handle_message
from handlers.callback_router import handle_callback

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    if "message" in data: await handle_message(data["message"])
    if "callback_query" in data: await handle_callback(data["callback_query"])
    return {"ok": True}