"""Background ROI processor"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from .database import AsyncSessionLocal, Investment, Transaction, User
import logging

logger = logging.getLogger(__name__)

async def process_investment_payouts():
    while True:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Investment).where(Investment.status == 'active')
                )
                investments = result.scalars().all()
                
                for inv in investments:
                    time_since = datetime.utcnow() - inv.last_payout
                    if time_since >= timedelta(hours=24):
                        payout = inv.amount * inv.daily_roi
                        
                        user_result = await session.execute(
                            select(User).where(User.id == inv.user_id)
                        )
                        user = user_result.scalar_one()
                        user.balance += payout
                        inv.total_earned += payout
                        inv.last_payout = datetime.utcnow()
                        
                        trans = Transaction(
                            user_id=user.id,
                            type='investment_payout',
                            amount=payout,
                            description=f'ROI from {inv.plan}'
                        )
                        session.add(trans)
                        await session.commit()
                        logger.info(f"✅ Payout ${payout:.2f} to {user.telegram_id}")
        except Exception as e:
            logger.error(f"❌ Payout error: {e}")
        
        await asyncio.sleep(3600)

async def start_background_tasks():
    logger.info("🔄 Starting background tasks")
    asyncio.create_task(process_investment_payouts())
