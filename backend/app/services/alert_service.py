"""
Alert Service - Email and SMS notifications for sensor threshold breaches
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

load_dotenv()
logger = logging.getLogger(__name__)

class AlertService:
    """Service for sending email and SMS alerts"""
    
    def __init__(self):
        # Alert cooldown tracking (sensor_type -> last_alert_time)
        self._last_alert_times = {}
        self._alert_cooldown_seconds = 300  # 5 minutes cooldown between alerts
        
        # Email configuration
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.alert_email_from = os.getenv("ALERT_EMAIL_FROM", self.smtp_user)
        self.alert_email_to = os.getenv("ALERT_EMAIL_TO", "")
        
        # SMS configuration (Twilio)
        self.sms_provider = os.getenv("SMS_PROVIDER", "twilio")
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        self.alert_phone_number = os.getenv("ALERT_PHONE_NUMBER", "")
        
        # Sensor thresholds
        self.thresholds = {
            "gas": {
                "warning": float(os.getenv("GAS_WARNING_THRESHOLD", "50")),
                "danger": float(os.getenv("GAS_DANGER_THRESHOLD", "100"))
            },
            "temperature": {
                "warning": float(os.getenv("TEMP_WARNING_THRESHOLD", "35")),
                "danger": float(os.getenv("TEMP_DANGER_THRESHOLD", "45"))
            },
            "vibration": {
                "warning": float(os.getenv("VIBRATION_WARNING_THRESHOLD", "5")),
                "danger": float(os.getenv("VIBRATION_DANGER_THRESHOLD", "10"))
            },
            "ultrasonic": {
                "warning": float(os.getenv("PROXIMITY_WARNING_THRESHOLD", "50")),
                "danger": float(os.getenv("PROXIMITY_DANGER_THRESHOLD", "20"))
            }
        }
        
        # Initialize Twilio client
        self.twilio_client = None
        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
    
    def check_threshold(self, sensor_type: str, value: float) -> Dict[str, Any]:
        """
        Check if sensor value breaches threshold
        
        Returns:
            dict with keys: breached (bool), level (str), threshold (float)
        """
        if sensor_type not in self.thresholds:
            return {"breached": False, "level": "normal", "threshold": None}
        
        thresholds = self.thresholds[sensor_type]
        
        # Check danger threshold first
        if value >= thresholds["danger"]:
            return {
                "breached": True,
                "level": "danger",
                "threshold": thresholds["danger"],
                "value": value
            }
        
        # Check warning threshold
        if value >= thresholds["warning"]:
            return {
                "breached": True,
                "level": "warning",
                "threshold": thresholds["warning"],
                "value": value
            }
        
        return {"breached": False, "level": "normal", "threshold": None, "value": value}
    
    def send_email_alert(self, sensor_type: str, sensor_data: Dict[str, Any], breach_info: Dict[str, Any]) -> bool:
        """Send email alert for sensor threshold breach"""
        
        if not self.smtp_user or not self.smtp_password or not self.alert_email_to:
            logger.warning("Email configuration incomplete - skipping email alert")
            return False
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"⚠️ {breach_info['level'].upper()} ALERT: {sensor_type.upper()} Sensor Threshold Breached"
            msg['From'] = self.alert_email_from
            msg['To'] = self.alert_email_to
            
            # Get sensor details
            value = sensor_data.get('value', breach_info['value'])
            unit = sensor_data.get('unit', '')
            threshold = breach_info['threshold']
            level = breach_info['level']
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Create email body (plain text)
            text_body = f"""
SENSOR ALERT - {level.upper()}

Sensor Type: {sensor_type.upper()}
Current Value: {value:.2f} {unit}
Threshold: {threshold:.2f} {unit}
Status: {level.upper()}
Timestamp: {timestamp}

This is an automated alert from the AI Safety Monitoring System.
Please check the dashboard immediately: http://localhost:5173

---
AI Safety Monitoring System
Smart Shop Floor Safety
            """
            
            # Create email body (HTML)
            html_body = f"""
            <html>
              <head>
                <style>
                  body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                  .alert-container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background-color: #f9f9f9; 
                    border-radius: 10px; 
                    padding: 20px;
                  }}
                  .alert-header {{ 
                    background: {'#dc2626' if level == 'danger' else '#f59e0b'}; 
                    color: white; 
                    padding: 20px; 
                    border-radius: 10px 10px 0 0; 
                    text-align: center;
                  }}
                  .alert-body {{ 
                    background: white; 
                    padding: 30px; 
                    border-radius: 0 0 10px 10px;
                  }}
                  .sensor-info {{ 
                    background: #f3f4f6; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 15px 0;
                  }}
                  .info-row {{ 
                    display: flex; 
                    justify-content: space-between; 
                    padding: 8px 0; 
                    border-bottom: 1px solid #e5e7eb;
                  }}
                  .info-label {{ font-weight: bold; color: #374151; }}
                  .info-value {{ color: #1f2937; }}
                  .danger-value {{ color: #dc2626; font-weight: bold; }}
                  .warning-value {{ color: #f59e0b; font-weight: bold; }}
                  .action-button {{
                    display: inline-block;
                    background: #2563eb;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                  }}
                  .footer {{ 
                    text-align: center; 
                    color: #6b7280; 
                    font-size: 12px; 
                    margin-top: 20px;
                  }}
                </style>
              </head>
              <body>
                <div class="alert-container">
                  <div class="alert-header">
                    <h1 style="margin: 0;">⚠️ SENSOR ALERT</h1>
                    <h2 style="margin: 10px 0 0 0;">{level.upper()} LEVEL</h2>
                  </div>
                  
                  <div class="alert-body">
                    <h3>Sensor Threshold Breach Detected</h3>
                    <p>The {sensor_type.upper()} sensor has exceeded its threshold limit.</p>
                    
                    <div class="sensor-info">
                      <div class="info-row">
                        <span class="info-label">Sensor Type:</span>
                        <span class="info-value">{sensor_type.upper()}</span>
                      </div>
                      <div class="info-row">
                        <span class="info-label">Current Value:</span>
                        <span class="{'danger-value' if level == 'danger' else 'warning-value'}">
                          {value:.2f} {unit}
                        </span>
                      </div>
                      <div class="info-row">
                        <span class="info-label">Threshold Limit:</span>
                        <span class="info-value">{threshold:.2f} {unit}</span>
                      </div>
                      <div class="info-row">
                        <span class="info-label">Status:</span>
                        <span class="{'danger-value' if level == 'danger' else 'warning-value'}">
                          {level.upper()}
                        </span>
                      </div>
                      <div class="info-row">
                        <span class="info-label">Timestamp:</span>
                        <span class="info-value">{timestamp}</span>
                      </div>
                    </div>
                    
                    <p style="margin-top: 20px;">
                      <strong>Recommended Action:</strong><br>
                      {'Immediate evacuation and emergency response required!' if level == 'danger' else 'Please investigate and monitor the situation.'}
                    </p>
                    
                    <div style="text-align: center;">
                      <a href="http://localhost:5173" class="action-button">
                        View Dashboard
                      </a>
                    </div>
                    
                    <div class="footer">
                      <p>This is an automated alert from the AI Safety Monitoring System.</p>
                      <p>Smart Shop Floor Safety | © 2025</p>
                    </div>
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent successfully for {sensor_type} sensor")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_sms_alert(self, sensor_type: str, sensor_data: Dict[str, Any], breach_info: Dict[str, Any]) -> bool:
        """Send SMS alert for sensor threshold breach"""
        
        if not self.twilio_client or not self.twilio_phone_number or not self.alert_phone_number:
            logger.warning("SMS configuration incomplete - skipping SMS alert")
            return False
        
        try:
            # Get sensor details
            value = sensor_data.get('value', breach_info['value'])
            unit = sensor_data.get('unit', '')
            threshold = breach_info['threshold']
            level = breach_info['level']
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Create SMS message
            sms_body = f"""
🚨 {level.upper()} ALERT

{sensor_type.upper()}: {value:.1f}{unit}
Threshold: {threshold:.1f}{unit}

Time: {timestamp}

Check dashboard: http://localhost:5173

AI Safety Monitoring
            """.strip()
            
            # Send SMS via Twilio
            message = self.twilio_client.messages.create(
                body=sms_body,
                from_=self.twilio_phone_number,
                to=f"+91{self.alert_phone_number}"  # India country code
            )
            
            logger.info(f"SMS alert sent successfully for {sensor_type} sensor. SID: {message.sid}")
            return True
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
            return False
    
    def send_alert(self, sensor_type: str, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check sensor threshold and send alerts if breached
        
        Args:
            sensor_type: Type of sensor (gas, temperature, vibration, ultrasonic)
            sensor_data: Sensor data dict with 'value' and 'unit' keys
        
        Returns:
            dict with alert status and results
        """
        # Check threshold
        breach_info = self.check_threshold(sensor_type, sensor_data.get('value', 0))
        
        if not breach_info['breached']:
            return {
                "alert_sent": False,
                "level": "normal",
                "message": "No threshold breach detected"
            }
        
        # Check cooldown - prevent alert spam
        current_time = datetime.utcnow().timestamp()
        last_alert_time = self._last_alert_times.get(sensor_type, 0)
        
        if current_time - last_alert_time < self._alert_cooldown_seconds:
            time_remaining = int(self._alert_cooldown_seconds - (current_time - last_alert_time))
            logger.info(f"Alert cooldown active for {sensor_type}. {time_remaining}s remaining")
            return {
                "alert_sent": False,
                "level": breach_info['level'],
                "threshold": breach_info['threshold'],
                "value": breach_info['value'],
                "email_sent": False,
                "sms_sent": False,
                "message": f"Alert suppressed - cooldown active ({time_remaining}s remaining)"
            }
        
        # Threshold breached - send alerts
        logger.warning(f"Threshold breach detected for {sensor_type}: {breach_info}")
        
        # Send email alert
        email_sent = self.send_email_alert(sensor_type, sensor_data, breach_info)
        
        # Send SMS alert
        sms_sent = self.send_sms_alert(sensor_type, sensor_data, breach_info)
        
        # Update last alert time only if at least one alert was sent
        if email_sent or sms_sent:
            self._last_alert_times[sensor_type] = current_time
        
        return {
            "alert_sent": True,
            "level": breach_info['level'],
            "threshold": breach_info['threshold'],
            "value": breach_info['value'],
            "email_sent": email_sent,
            "sms_sent": sms_sent,
            "message": f"{breach_info['level'].upper()} threshold breached"
        }
    
    def test_email(self) -> bool:
        """Test email configuration"""
        try:
            test_data = {
                "value": 55.0,
                "unit": "°C"
            }
            breach_info = {
                "level": "warning",
                "threshold": 35.0,
                "value": 55.0
            }
            return self.send_email_alert("temperature", test_data, breach_info)
        except Exception as e:
            logger.error(f"Email test failed: {e}")
            return False
    
    def test_sms(self) -> bool:
        """Test SMS configuration"""
        try:
            test_data = {
                "value": 55.0,
                "unit": "°C"
            }
            breach_info = {
                "level": "warning",
                "threshold": 35.0,
                "value": 55.0
            }
            return self.send_sms_alert("temperature", test_data, breach_info)
        except Exception as e:
            logger.error(f"SMS test failed: {e}")
            return False


# Singleton instance
alert_service = AlertService()
