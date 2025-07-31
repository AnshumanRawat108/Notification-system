import asyncio
from datetime import datetime
from email.message import EmailMessage

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker
from sqlalchemy import String, Float, select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiosmtplib import send

# ------------------ CONFIG ------------------
DATABASE_URL = "mysql+aiomysql://root:yourpassword@localhost:3306/notify_db"  # <--- Change this
SMTP_EMAIL = "your_email@gmail.com"            # <--- Change this
SMTP_PASSWORD = "your_email_password"          # <--- Change this
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

THRESHOLD_BALANCE = 500.0
BLOCKING_BALANCE = 100.0
# --------------------------------------------

# -------------- DATABASE SETUP --------------
class Base(DeclarativeBase):
    pass

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    balance: Mapped[float] = mapped_column(Float)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# --------------------------------------------

# -------------- EMAIL FUNCTION --------------
async def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    await send(
        msg,
        hostname=SMTP_SERVER,
        port=SMTP_PORT,
        username=SMTP_EMAIL,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
# --------------------------------------------

# ----------- BALANCE CHECK FUNCTION ---------
async def check_balances():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Checking balances...")

    async with async_session() as session:
        result = await session.execute(select(Employee))
        employees = result.scalars().all()

        for emp in employees:
            print(f"👤 {emp.name} → ₹{emp.balance}")
            if emp.balance <= BLOCKING_BALANCE:
                print(f"⛔ Service blocked for {emp.name} (₹{emp.balance})")
            elif emp.balance <= THRESHOLD_BALANCE:
                subject = "⚠️ Low Balance Alert"
                body = f"Hello {emp.name},\n\nYour current balance is ₹{emp.balance}. Please recharge soon to avoid service interruption.\n\nThanks."
                await send_email(emp.email, subject, body)
                print(f"📨 Email sent to {emp.email}")
# --------------------------------------------

# ---------------- MAIN APP ------------------
async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_balances, "interval", minutes=5)
    scheduler.start()

    print("✅ Notification System Running... (checks every 5 mins)")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
