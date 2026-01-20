
import os, time, random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="FreePlay Telegram Platform")

USERS = {}
COOLDOWN = 30  # seconds

class PlayReq(BaseModel):
    telegram_id: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/user/register")
def register(telegram_id: int):
    if telegram_id not in USERS:
        USERS[telegram_id] = {"points": 0, "xp": 0, "last_play": 0}
    return USERS[telegram_id]

@app.post("/game/slots")
def slots(req: PlayReq):
    user = USERS.get(req.telegram_id)
    if not user:
        raise HTTPException(404, "User not found")

    now = time.time()
    if now - user["last_play"] < COOLDOWN:
        raise HTTPException(429, "Cooldown")

    user["last_play"] = now
    symbols = ["🍒","🍋","⭐","7️⃣"]
    result = [random.choice(symbols) for _ in range(3)]
    win = len(set(result)) == 1
    user["points"] += 10 if win else 1
    user["xp"] += 2
    return {"result": result, "win": win, "user": user}
