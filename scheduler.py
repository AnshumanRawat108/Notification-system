# scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update
from database import async_session_maker, engine
from models import Employee, Base
from email_utils import send_email


async def check_balances():
    async with async_session_maker() as session:
        result = await session.execute(select(Employee))
        employees = result.scalars().all()

        for emp in employees:
            if emp.balance <= emp.blocking_limit and not emp.is_blocked:
                # Block service and send email
                emp.is_blocked = True
                await send_email(
                    emp.email,
                    "Service Blocked",
                    f"Dear {emp.name}, your balance has dropped below the blocking limit. Your service has been blocked."
                )
                print(f"Blocked: {emp.name}")
            elif emp.balance <= emp.threshold_limit and not emp.is_blocked:
                # Just warn
                await send_email(
                    emp.email,
                    "Low Balance Warning",
                    f"Dear {emp.name}, your balance is near the threshold. Please recharge to avoid service block."
                )
                print(f"Warning sent to: {emp.name}")

        await session.commit()


async def start_scheduler():
    # Create tables if not present
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_balances, "interval", minutes=5)
    scheduler.start()
    print("🔄 Scheduler started. Checking balances every 5 minutes.")
