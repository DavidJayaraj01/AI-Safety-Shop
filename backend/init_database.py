#!/usr/bin/env python3
"""
Script to initialize database tables
Run this before seeding data
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import init_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Initialize database tables"""
    logger.info("Initializing database tables...")
    
    try:
        await init_db()
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
