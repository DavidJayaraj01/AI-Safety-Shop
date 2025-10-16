import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class AlertNotifier:
    def __init__(self):
        self.twilio_enabled = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
        self.email_enabled = bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
        self.telegram_enabled = bool(settings.TELEGRAM_BOT_TOKEN)
        self.slack_enabled = bool(settings.SLACK_WEBHOOK_URL)
        
        # Parse phone numbers and emails
        self.alert_phones = [p.strip() for p in settings.ALERT_PHONE_NUMBERS.split(',') if p.strip()]
        self.alert_emails = [e.strip() for e in settings.ALERT_EMAILS.split(',') if e.strip()]
        
        logger.info(f"Alert Notifier initialized - SMS: {self.twilio_enabled}, Email: {self.email_enabled}, Telegram: {self.telegram_enabled}, Slack: {self.slack_enabled}")
    
    def send_alert(self, alert: Dict, channels: List[str] = None):
        """
        Send alert through specified channels
        channels: ['sms', 'email', 'telegram', 'slack', 'all']
        """
        if channels is None or 'all' in channels:
            channels = ['sms', 'email', 'telegram', 'slack']
        
        severity = alert.get('severity', 'medium')
        
        # Only send high/critical alerts via SMS (to avoid spam)
        if 'sms' in channels and severity in ['high', 'critical']:
            self.send_sms(alert)
        
        if 'email' in channels:
            self.send_email(alert)
        
        if 'telegram' in channels:
            self.send_telegram(alert)
        
        if 'slack' in channels:
            self.send_slack(alert)
    
    def send_sms(self, alert: Dict):
        """Send SMS alert via Twilio"""
        if not self.twilio_enabled:
            logger.warning("Twilio not configured, skipping SMS")
            return
        
        try:
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message_body = f"🚨 SAFETY ALERT [{alert['severity'].upper()}]\n\n{alert['message']}\n\nLocation: {alert['location']}\nTime: {datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}"
            
            for phone in self.alert_phones:
                try:
                    message = client.messages.create(
                        body=message_body,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=phone
                    )
                    logger.info(f"SMS sent to {phone}: {message.sid}")
                except Exception as e:
                    logger.error(f"Failed to send SMS to {phone}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
    
    def send_email(self, alert: Dict):
        """Send email alert"""
        if not self.email_enabled:
            logger.warning("Email not configured, skipping email")
            return
        
        try:
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{severity_emoji.get(alert['severity'], '⚠️')} Safety Alert: {alert['type'].replace('_', ' ').title()}"
            msg['From'] = settings.SMTP_USER
            msg['To'] = ', '.join(self.alert_emails)
            
            # HTML email body
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; border: 2px solid #{'dc2626' if alert['severity'] in ['critical', 'high'] else 'f59e0b'}; border-radius: 8px; padding: 20px;">
                  <h2 style="color: #{'dc2626' if alert['severity'] in ['critical', 'high'] else 'f59e0b'};">
                    {severity_emoji.get(alert['severity'], '⚠️')} Safety Alert Notification
                  </h2>
                  <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                      <td style="padding: 8px; font-weight: bold;">Alert Type:</td>
                      <td style="padding: 8px;">{alert['type'].replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                      <td style="padding: 8px; font-weight: bold;">Severity:</td>
                      <td style="padding: 8px;"><span style="background-color: #{'dc2626' if alert['severity'] in ['critical', 'high'] else 'f59e0b'}; color: white; padding: 4px 8px; border-radius: 4px;">{alert['severity'].upper()}</span></td>
                    </tr>
                    <tr>
                      <td style="padding: 8px; font-weight: bold;">Message:</td>
                      <td style="padding: 8px;">{alert['message']}</td>
                    </tr>
                    <tr>
                      <td style="padding: 8px; font-weight: bold;">Location:</td>
                      <td style="padding: 8px;">{alert['location']}</td>
                    </tr>
                    <tr>
                      <td style="padding: 8px; font-weight: bold;">Timestamp:</td>
                      <td style="padding: 8px;">{datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                  </table>
                  <div style="margin-top: 20px; padding: 15px; background-color: #f3f4f6; border-radius: 4px;">
                    <p style="margin: 0; font-size: 14px;">
                      <strong>Action Required:</strong> Please review the alert in the dashboard and take appropriate action.
                    </p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {', '.join(self.alert_emails)}")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
    
    def send_telegram(self, alert: Dict):
        """Send alert via Telegram bot"""
        if not self.telegram_enabled:
            logger.warning("Telegram not configured, skipping")
            return
        
        try:
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            
            message = f"{severity_emoji.get(alert['severity'], '⚠️')} *SAFETY ALERT*\n\n"
            message += f"*Type:* {alert['type'].replace('_', ' ').title()}\n"
            message += f"*Severity:* {alert['severity'].upper()}\n"
            message += f"*Message:* {alert['message']}\n"
            message += f"*Location:* {alert['location']}\n"
            message += f"*Time:* {datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}"
            
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': settings.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info("Telegram alert sent successfully")
            else:
                logger.error(f"Failed to send Telegram alert: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
    
    def send_slack(self, alert: Dict):
        """Send alert via Slack webhook"""
        if not self.slack_enabled:
            logger.warning("Slack not configured, skipping")
            return
        
        try:
            severity_colors = {
                'critical': '#dc2626',
                'high': '#ea580c',
                'medium': '#f59e0b',
                'low': '#22c55e'
            }
            
            payload = {
                "attachments": [
                    {
                        "color": severity_colors.get(alert['severity'], '#f59e0b'),
                        "title": f"🚨 Safety Alert: {alert['type'].replace('_', ' ').title()}",
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert['severity'].upper(),
                                "short": True
                            },
                            {
                                "title": "Location",
                                "value": alert['location'],
                                "short": True
                            },
                            {
                                "title": "Message",
                                "value": alert['message'],
                                "short": False
                            },
                            {
                                "title": "Timestamp",
                                "value": datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                                "short": False
                            }
                        ],
                        "footer": "AI Safety Monitoring System",
                        "ts": int(datetime.fromisoformat(alert['timestamp']).timestamp())
                    }
                ]
            }
            
            response = requests.post(settings.SLACK_WEBHOOK_URL, json=payload)
            
            if response.status_code == 200:
                logger.info("Slack alert sent successfully")
            else:
                logger.error(f"Failed to send Slack alert: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
    
    def send_escalation(self, alert: Dict, minutes_elapsed: int):
        """Send escalation alert for unresolved critical alerts"""
        escalation_message = {
            **alert,
            'message': f"⚠️ ESCALATION: Alert unresolved for {minutes_elapsed} minutes - {alert['message']}",
            'severity': 'critical'
        }
        
        # Send through all channels for escalations
        self.send_alert(escalation_message, channels=['all'])
        
        logger.warning(f"Escalation alert sent for alert {alert['id']} after {minutes_elapsed} minutes")
