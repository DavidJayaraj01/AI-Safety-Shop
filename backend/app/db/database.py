from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Database URL - Use SQLite by default if PostgreSQL is not configured
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL or PostgreSQL not available, use SQLite
if not DATABASE_URL or "postgresql" in DATABASE_URL:
    # Create database directory if it doesn't exist
    db_dir = Path(__file__).parent.parent.parent / "data"
    db_dir.mkdir(exist_ok=True)
    db_path = db_dir / "ai_safety_monitoring.db"
    ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
    print(f"Using SQLite database at: {db_path}")
else:
    # Convert to async URL for asyncpg
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    print(f"Using PostgreSQL database")

# Create async engine with appropriate settings based on database type
if "sqlite" in ASYNC_DATABASE_URL:
    # SQLite doesn't support pool_size and max_overflow
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        future=True,
    )
else:
    # PostgreSQL supports connection pooling
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create async session maker
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()

# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Close database
async def close_db():
    await engine.dispose()
