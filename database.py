# database.py

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("❌ DATABASE_URL not found. Make sure your .env file is set correctly.")

# Create the asynchronous SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create the async session maker
async_session_maker = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Optional base for standalone models (if not using separate models.py)
Base = declarative_base()

