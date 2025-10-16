from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

router = APIRouter()

@router.get("/")
async def get_all_workers(db: AsyncSession = Depends(get_db)):
    return [{"id": 1, "name": "John Doe", "worker_id": "W1001", "status": "active"}]

@router.get("/active")
async def get_active_workers(db: AsyncSession = Depends(get_db)):
    return [{"id": 1, "name": "John Doe", "location": "Workshop"}]

@router.get("/logs")
async def get_worker_logs(days: int = 7, db: AsyncSession = Depends(get_db)):
    return []
