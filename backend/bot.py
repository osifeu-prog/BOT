
from fastapi import APIRouter

router = APIRouter()

@router.post("/telegram")
async def telegram_webhook(update: dict):
    return {"ok": True}
