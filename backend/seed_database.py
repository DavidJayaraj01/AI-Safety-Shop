#!/usr/bin/env python3
"""
Script to seed the database with sample cameras and detections
Run this script to populate the database with test data
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import AsyncSessionLocal
from app.db.seed_data import seed_all_data
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Seed the database with sample data"""
    logger.info("Starting database seeding...")
    
    async with AsyncSessionLocal() as session:
        try:
            await seed_all_data(session)
            logger.info("✅ Database seeding completed successfully!")
        except Exception as e:
            logger.error(f"❌ Error seeding database: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())
