from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta
from typing import Optional
from app.db.database import get_db
from app.models.models import CVDetection, Alert, SensorData, Incident, AlertSeverity, Camera
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_date_range(period: str):
    """Get start and end dates based on period"""
    now = datetime.utcnow()
    
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - timedelta(days=7)
    elif period == "month":
        start = now - timedelta(days=30)
    elif period == "quarter":
        start = now - timedelta(days=90)
    elif period == "year":
        start = now - timedelta(days=365)
    else:
        start = now - timedelta(days=7)  # Default to week
    
    return start, now

@router.get("/")
async def get_report(period: str = "week", db: AsyncSession = Depends(get_db)):
    """Get comprehensive report with real data"""
    start_date, end_date = get_date_range(period)
    
    # Get CV detections count
    cv_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(CVDetection.timestamp >= start_date)
    )
    total_cv_detections = cv_result.scalar() or 0
    
    # Get alerts count
    alerts_result = await db.execute(
        select(func.count(Alert.id))
        .filter(Alert.timestamp >= start_date)
    )
    total_alerts = alerts_result.scalar() or 0
    
    # Get resolved alerts
    resolved_result = await db.execute(
        select(func.count(Alert.id))
        .filter(
            and_(
                Alert.timestamp >= start_date,
                Alert.acknowledged_at.isnot(None)
            )
        )
    )
    resolved_alerts = resolved_result.scalar() or 0
    
    # Get incidents count
    incidents_result = await db.execute(
        select(func.count(Incident.id))
        .filter(Incident.timestamp >= start_date)
    )
    total_incidents = incidents_result.scalar() or 0
    
    # Get sensor data points
    sensor_result = await db.execute(
        select(func.count(SensorData.id))
        .filter(SensorData.timestamp >= start_date)
    )
    total_sensor_data = sensor_result.scalar() or 0
    
    # Get critical violations
    critical_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.severity == "danger"
            )
        )
    )
    critical_violations = critical_result.scalar() or 0
    
    # Calculate average response time (time to acknowledge alerts)
    avg_response_result = await db.execute(
        select(func.avg(
            func.julianday(Alert.acknowledged_at) - func.julianday(Alert.timestamp)
        ) * 24)  # Convert days to hours
        .filter(
            and_(
                Alert.timestamp >= start_date,
                Alert.acknowledged_at.isnot(None)
            )
        )
    )
    avg_response_time = avg_response_result.scalar() or 0
    
    return {
        "summary": {
            "totalIncidents": total_incidents + total_cv_detections,
            "totalWarnings": total_alerts,
            "resolvedAlerts": resolved_alerts,
            "criticalViolations": critical_violations,
            "averageResponseTime": round(avg_response_time, 1) if avg_response_time else 0,
            "totalDataPoints": total_sensor_data,
            "period": period
        },
        "timeline": [],
        "sensorBreakdown": [],
        "incidentTypes": [],
        "predictions": {
            "nextWeekRisk": "medium" if critical_violations > 5 else "low",
            "likelyIncidents": [],
            "confidence": 78
        }
    }

@router.get("/incidents")
async def get_incident_report(
    period: str = "week",
    db: AsyncSession = Depends(get_db)
):
    """Get detailed incident report"""
    start_date, end_date = get_date_range(period)
    
    # Get all incidents
    result = await db.execute(
        select(Incident)
        .filter(Incident.timestamp >= start_date)
        .order_by(Incident.timestamp.desc())
    )
    incidents = result.scalars().all()
    
    return [
        {
            "id": inc.id,
            "type": inc.incident_type,
            "severity": inc.severity,
            "description": inc.description,
            "location": inc.location,
            "status": inc.status,
            "timestamp": inc.timestamp.isoformat(),
            "resolved_at": inc.resolved_at.isoformat() if inc.resolved_at else None
        }
        for inc in incidents
    ]

@router.get("/analytics")
async def get_analytics(period: str = "week", db: AsyncSession = Depends(get_db)):
    """Get analytics data for charts"""
    start_date, end_date = get_date_range(period)
    
    # Incident trend by day
    if period == "today":
        # Hourly for today
        interval_hours = [(start_date + timedelta(hours=i), start_date + timedelta(hours=i+1)) 
                         for i in range(24)]
        labels = [f"{i:02d}:00" for i in range(24)]
    elif period == "week":
        # Daily for week
        interval_days = [(start_date + timedelta(days=i), start_date + timedelta(days=i+1)) 
                        for i in range(7)]
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][-len(interval_days):]
    else:
        # Weekly intervals for longer periods
        weeks = 7 if period == "month" else 12
        interval_days = [(start_date + timedelta(days=i*7), start_date + timedelta(days=(i+1)*7)) 
                        for i in range(weeks)]
        labels = [f"Week {i+1}" for i in range(weeks)]
    
    # Get incident counts per interval
    incident_trend = []
    intervals = interval_hours if period == "today" else interval_days
    
    for interval_start, interval_end in intervals:
        count_result = await db.execute(
            select(func.count(CVDetection.id))
            .filter(
                and_(
                    CVDetection.timestamp >= interval_start,
                    CVDetection.timestamp < interval_end
                )
            )
        )
        count = count_result.scalar() or 0
        incident_trend.append(count)
    
    # Severity distribution
    danger_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.severity == "danger"
            )
        )
    )
    danger_count = danger_result.scalar() or 0
    
    warning_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.severity == "warning"
            )
        )
    )
    warning_count = warning_result.scalar() or 0
    
    info_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.severity == "info"
            )
        )
    )
    info_count = info_result.scalar() or 0
    
    # Detection types breakdown
    ppe_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.detection_type == "ppe_violation"
            )
        )
    )
    ppe_count = ppe_result.scalar() or 0
    
    fire_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.detection_type == "fire_smoke"
            )
        )
    )
    fire_count = fire_result.scalar() or 0
    
    hazard_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.detection_type == "hazard_zone"
            )
        )
    )
    hazard_count = hazard_result.scalar() or 0
    
    unsafe_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.detection_type == "unsafe_behavior"
            )
        )
    )
    unsafe_count = unsafe_result.scalar() or 0
    
    return {
        "incidentTrend": {
            "labels": labels,
            "data": incident_trend
        },
        "severityDistribution": {
            "labels": ["Critical", "Warning", "Info"],
            "data": [danger_count, warning_count, info_count]
        },
        "detectionTypes": {
            "labels": ["PPE Violations", "Fire/Smoke", "Hazard Zones", "Unsafe Behavior"],
            "data": [ppe_count, fire_count, hazard_count, unsafe_count]
        }
    }

@router.get("/list")
async def get_reports_list(
    period: str = Query("week"),
    report_type: str = Query("all"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of available reports"""
    start_date, end_date = get_date_range(period)
    
    reports = []
    
    # Safety Report (CV Detections)
    cv_count_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(CVDetection.timestamp >= start_date)
    )
    cv_count = cv_count_result.scalar() or 0
    
    cv_severity_result = await db.execute(
        select(func.count(CVDetection.id))
        .filter(
            and_(
                CVDetection.timestamp >= start_date,
                CVDetection.severity == "danger"
            )
        )
    )
    cv_critical = cv_severity_result.scalar() or 0
    
    if report_type in ["all", "safety"]:
        reports.append({
            "id": 1,
            "type": "safety",
            "title": f"{period.capitalize()} Safety Report",
            "date": datetime.now().isoformat(),
            "status": "completed",
            "incidents": cv_count,
            "severity": "high" if cv_critical > 5 else "medium" if cv_critical > 0 else "low"
        })
    
    # Alert Report
    alert_count_result = await db.execute(
        select(func.count(Alert.id))
        .filter(Alert.timestamp >= start_date)
    )
    alert_count = alert_count_result.scalar() or 0
    
    if report_type in ["all", "alert"]:
        reports.append({
            "id": 2,
            "type": "alert",
            "title": f"{period.capitalize()} Alert Summary",
            "date": datetime.now().isoformat(),
            "status": "completed",
            "incidents": alert_count,
            "severity": "medium"
        })
    
    # Sensor Report
    sensor_count_result = await db.execute(
        select(func.count(SensorData.id))
        .filter(SensorData.timestamp >= start_date)
    )
    sensor_count = sensor_count_result.scalar() or 0
    
    if report_type in ["all", "sensor"]:
        reports.append({
            "id": 3,
            "type": "sensor",
            "title": f"{period.capitalize()} Sensor Performance",
            "date": datetime.now().isoformat(),
            "status": "completed",
            "incidents": 0,
            "severity": "low"
        })
    
    # Compliance Report
    compliance_rate = 100 - (cv_critical / max(cv_count, 1) * 100) if cv_count > 0 else 100
    
    if report_type in ["all", "compliance"]:
        reports.append({
            "id": 4,
            "type": "compliance",
            "title": f"{period.capitalize()} Compliance Report",
            "date": datetime.now().isoformat(),
            "status": "completed",
            "incidents": cv_critical,
            "severity": "low" if compliance_rate > 95 else "medium"
        })
    
    # Camera Performance Report
    camera_count_result = await db.execute(select(func.count(Camera.id)))
    camera_count = camera_count_result.scalar() or 0
    
    if report_type in ["all", "maintenance"]:
        reports.append({
            "id": 5,
            "type": "maintenance",
            "title": f"{period.capitalize()} Camera Maintenance Log",
            "date": datetime.now().isoformat(),
            "status": "completed",
            "incidents": 0,
            "severity": "low"
        })
    
    return reports
