
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI(title="FreePlay Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlayRequest(BaseModel):
    user_id: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/games/slots")
def play_slots(req: PlayRequest):
    symbols = ["🍒","🍋","⭐","7️⃣"]
    result = [random.choice(symbols) for _ in range(3)]
    win = len(set(result)) == 1
    points = 10 if win else 1
    return {"result": result, "win": win, "points": points}

@app.get("/shop/items")
def shop_items():
    return [
        {"id":"vip","name":"VIP Access","price":100},
        {"id":"admin_basic","name":"Admin Basic","price":500}
    ]

@app.post("/admin/login")
def admin_login(username: str, password: str):
    if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
        return {"token":"demo-admin-token"}
    raise HTTPException(status_code=401, detail="Unauthorized")
