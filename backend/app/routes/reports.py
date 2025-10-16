from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
import random

router = APIRouter()

@router.get("/")
async def get_report(range: str = "week", db: AsyncSession = Depends(get_db)):
    return {
        "summary": {
            "totalIncidents": random.randint(40, 60),
            "totalWarnings": random.randint(100, 150),
            "resolvedAlerts": random.randint(140, 180),
            "averageResponseTime": round(random.uniform(2, 4), 1),
            "uptime": round(random.uniform(98, 99.9), 1),
            "totalDataPoints": random.randint(20000, 30000)
        },
        "timeline": [],
        "sensorBreakdown": [],
        "incidentTypes": [],
        "predictions": {"nextWeekRisk": "medium", "likelyIncidents": [], "confidence": 78}
    }

@router.get("/incidents")
async def get_incident_report(db: AsyncSession = Depends(get_db)):
    return []
