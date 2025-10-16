from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Any

router = APIRouter()

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@router.get("/settings", response_model=ApiResponse)
async def get_settings():
    """Get system settings"""
    try:
        from app.core.config import settings as app_settings
        
        system_settings = {
            "notifications": {
                "email": bool(app_settings.SMTP_USER),
                "sms": bool(app_settings.TWILIO_ACCOUNT_SID),
                "telegram": bool(app_settings.TELEGRAM_BOT_TOKEN),
                "slack": bool(app_settings.SLACK_WEBHOOK_URL),
                "inApp": True
            },
            "thresholds": {
                "gas": {
                    "warning": app_settings.GAS_WARNING_THRESHOLD,
                    "critical": app_settings.GAS_CRITICAL_THRESHOLD
                },
                "temperature": {
                    "warning": app_settings.TEMP_WARNING_THRESHOLD,
                    "critical": app_settings.TEMP_CRITICAL_THRESHOLD
                },
                "vibration": {
                    "warning": app_settings.VIBRATION_WARNING_THRESHOLD,
                    "critical": app_settings.VIBRATION_CRITICAL_THRESHOLD
                }
            },
            "autoShutdown": app_settings.AUTO_SHUTDOWN_ENABLED,
            "alertCooldown": 5,
            "ppeConfidenceThreshold": app_settings.PPE_CONFIDENCE_THRESHOLD,
            "cameraSettings": {
                "enabled": True,
                "fps": app_settings.CAMERA_FPS,
                "resolution": f"{app_settings.CAMERA_WIDTH}x{app_settings.CAMERA_HEIGHT}"
            }
        }
        
        return ApiResponse(success=True, data=system_settings)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.put("/settings", response_model=ApiResponse)
async def update_settings(settings: dict):
    """Update system settings"""
    try:
        # In production, implement proper settings persistence
        return ApiResponse(success=True, data=settings, message="Settings updated")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))
