from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Safety Monitoring System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/safety_monitor"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # MQTT
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_TOPICS: str = "sensors/#,alerts/#,ppe/#"
    
    # Camera
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 1920
    CAMERA_HEIGHT: int = 1080
    CAMERA_FPS: int = 30
    
    # YOLOv8
    YOLO_MODEL_PATH: str = "models/yolov8n-ppe.pt"
    PPE_CONFIDENCE_THRESHOLD: float = 0.6
    PPE_CLASSES: str = "helmet,vest,gloves,goggles,safety_shoes"
    
    # Alerts
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    ALERT_PHONE_NUMBERS: str = ""
    
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAILS: str = ""
    
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    SLACK_WEBHOOK_URL: str = ""
    
    # Thresholds
    GAS_WARNING_THRESHOLD: float = 300
    GAS_CRITICAL_THRESHOLD: float = 500
    TEMP_WARNING_THRESHOLD: float = 40
    TEMP_CRITICAL_THRESHOLD: float = 60
    VIBRATION_WARNING_THRESHOLD: float = 8
    VIBRATION_CRITICAL_THRESHOLD: float = 15
    
    # Auto Shutdown
    AUTO_SHUTDOWN_ENABLED: bool = False
    SHUTDOWN_GPIO_PIN: int = 18
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
