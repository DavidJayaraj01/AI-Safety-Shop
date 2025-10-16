import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
from typing import Callable, Dict
import uuid
from app.core.config import settings

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.broker = settings.MQTT_BROKER
        self.port = settings.MQTT_PORT
        self.username = settings.MQTT_USERNAME
        self.password = settings.MQTT_PASSWORD
        self.topics = settings.MQTT_TOPICS.split(',')
        
        self.client = mqtt.Client(client_id=f"safety_monitor_{uuid.uuid4().hex[:8]}")
        self.connected = False
        
        # Message handlers
        self.handlers: Dict[str, Callable] = {}
        
        # Setup callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set authentication if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
            
            # Subscribe to all topics
            for topic in self.topics:
                self.client.subscribe(topic.strip())
                logger.info(f"Subscribed to topic: {topic.strip()}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker. Return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when a message is received"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            logger.info(f"Received message on topic '{topic}': {payload}")
            
            # Route to appropriate handler
            if topic.startswith("sensors/gas"):
                self._handle_gas_sensor(payload)
            elif topic.startswith("sensors/temperature"):
                self._handle_temperature_sensor(payload)
            elif topic.startswith("sensors/vibration"):
                self._handle_vibration_sensor(payload)
            elif topic.startswith("sensors/ultrasonic"):
                self._handle_ultrasonic_sensor(payload)
            elif topic.startswith("sensors/environment"):
                self._handle_environmental_sensor(payload)
            elif topic.startswith("rfid/"):
                self._handle_rfid_event(payload)
            elif topic.startswith("alerts/"):
                self._handle_alert(payload)
            
            # Call custom handlers if registered
            for pattern, handler in self.handlers.items():
                if topic.startswith(pattern):
                    handler(topic, payload)
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON payload: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _handle_gas_sensor(self, payload: Dict):
        """Handle gas sensor data"""
        sensor_data = {
            'id': str(uuid.uuid4()),
            'sensor_id': payload.get('sensor_id', 'gas_sensor_1'),
            'type': 'gas',
            'value': payload.get('value', 0),
            'unit': 'PPM',
            'location': payload.get('location', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Determine status based on thresholds
        if sensor_data['value'] >= settings.GAS_CRITICAL_THRESHOLD:
            sensor_data['status'] = 'critical'
            self._trigger_alert('gas_leak', 'critical', sensor_data)
        elif sensor_data['value'] >= settings.GAS_WARNING_THRESHOLD:
            sensor_data['status'] = 'warning'
            self._trigger_alert('gas_leak', 'high', sensor_data)
        else:
            sensor_data['status'] = 'normal'
        
        # Broadcast to WebSocket clients
        self._broadcast_sensor_update(sensor_data)
        
        # Store in database (implement database storage)
        logger.info(f"Gas sensor reading: {sensor_data['value']} PPM - Status: {sensor_data['status']}")
    
    def _handle_temperature_sensor(self, payload: Dict):
        """Handle temperature sensor data"""
        sensor_data = {
            'id': str(uuid.uuid4()),
            'sensor_id': payload.get('sensor_id', 'temp_sensor_1'),
            'type': 'temperature',
            'value': payload.get('value', 0),
            'unit': '°C',
            'location': payload.get('location', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if sensor_data['value'] >= settings.TEMP_CRITICAL_THRESHOLD:
            sensor_data['status'] = 'critical'
            self._trigger_alert('high_temperature', 'critical', sensor_data)
        elif sensor_data['value'] >= settings.TEMP_WARNING_THRESHOLD:
            sensor_data['status'] = 'warning'
            self._trigger_alert('high_temperature', 'medium', sensor_data)
        else:
            sensor_data['status'] = 'normal'
        
        self._broadcast_sensor_update(sensor_data)
        logger.info(f"Temperature reading: {sensor_data['value']}°C - Status: {sensor_data['status']}")
    
    def _handle_vibration_sensor(self, payload: Dict):
        """Handle vibration sensor data"""
        sensor_data = {
            'id': str(uuid.uuid4()),
            'sensor_id': payload.get('sensor_id', 'vib_sensor_1'),
            'type': 'vibration',
            'value': payload.get('value', 0),
            'unit': 'm/s²',
            'location': payload.get('location', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if sensor_data['value'] >= settings.VIBRATION_CRITICAL_THRESHOLD:
            sensor_data['status'] = 'critical'
            self._trigger_alert('vibration_anomaly', 'critical', sensor_data)
        elif sensor_data['value'] >= settings.VIBRATION_WARNING_THRESHOLD:
            sensor_data['status'] = 'warning'
            self._trigger_alert('vibration_anomaly', 'high', sensor_data)
        else:
            sensor_data['status'] = 'normal'
        
        self._broadcast_sensor_update(sensor_data)
        logger.info(f"Vibration reading: {sensor_data['value']} m/s² - Status: {sensor_data['status']}")
    
    def _handle_ultrasonic_sensor(self, payload: Dict):
        """Handle ultrasonic proximity sensor data"""
        sensor_data = {
            'id': str(uuid.uuid4()),
            'sensor_id': payload.get('sensor_id', 'ultrasonic_1'),
            'type': 'ultrasonic',
            'value': payload.get('distance', 0),
            'unit': 'cm',
            'location': payload.get('location', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Proximity alert if distance < 100cm
        if sensor_data['value'] < 100 and sensor_data['value'] > 0:
            sensor_data['status'] = 'warning'
            self._trigger_alert('proximity_warning', 'medium', sensor_data)
        else:
            sensor_data['status'] = 'normal'
        
        self._broadcast_sensor_update(sensor_data)
    
    def _handle_environmental_sensor(self, payload: Dict):
        """Handle environmental sensor (humidity, pressure, etc.)"""
        sensor_data = {
            'id': str(uuid.uuid4()),
            'sensor_id': payload.get('sensor_id', 'env_sensor_1'),
            'type': 'environmental',
            'value': payload.get('humidity', 0),
            'unit': '%',
            'location': payload.get('location', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'normal'
        }
        
        self._broadcast_sensor_update(sensor_data)
    
    def _handle_rfid_event(self, payload: Dict):
        """Handle RFID entry/exit events"""
        rfid_event = {
            'id': str(uuid.uuid4()),
            'worker_id': payload.get('worker_id', 'unknown'),
            'worker_name': payload.get('worker_name', 'Unknown Worker'),
            'event_type': payload.get('event_type', 'entry'),
            'location': payload.get('location', 'Main Gate'),
            'access_granted': payload.get('access_granted', True),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"RFID Event: {rfid_event['worker_name']} - {rfid_event['event_type']} at {rfid_event['location']}")
        
        # Broadcast to WebSocket
        self._broadcast_rfid_event(rfid_event)
    
    def _handle_alert(self, payload: Dict):
        """Handle incoming alerts from ESP32"""
        logger.info(f"Received alert from ESP32: {payload}")
    
    def _trigger_alert(self, alert_type: str, severity: str, sensor_data: Dict):
        """Trigger an alert based on sensor data"""
        alert = {
            'id': str(uuid.uuid4()),
            'type': alert_type,
            'severity': severity,
            'message': f"{alert_type.replace('_', ' ').title()}: {sensor_data['value']} {sensor_data['unit']} at {sensor_data['location']}",
            'location': sensor_data['location'],
            'sensor_id': sensor_data['sensor_id'],
            'timestamp': datetime.utcnow().isoformat(),
            'resolved': False,
            'actions': []
        }
        
        logger.warning(f"Alert triggered: {alert['message']}")
        
        # Broadcast alert to WebSocket clients
        self._broadcast_alert(alert)
        
        # Auto-shutdown if enabled and critical
        if settings.AUTO_SHUTDOWN_ENABLED and severity == 'critical':
            self._trigger_auto_shutdown(alert)
    
    def _trigger_auto_shutdown(self, alert: Dict):
        """Trigger auto-shutdown for critical alerts"""
        logger.critical(f"AUTO-SHUTDOWN TRIGGERED: {alert['message']}")
        # Implement GPIO control or relay trigger here
        # Example: GPIO.output(settings.SHUTDOWN_GPIO_PIN, GPIO.HIGH)
        
        # Publish shutdown command to MQTT
        self.publish("control/shutdown", {
            "command": "shutdown",
            "reason": alert['message'],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def _broadcast_sensor_update(self, sensor_data: Dict):
        """Broadcast sensor update to WebSocket clients"""
        # This will be called by the main app's WebSocket manager
        pass
    
    def _broadcast_alert(self, alert: Dict):
        """Broadcast alert to WebSocket clients"""
        pass
    
    def _broadcast_rfid_event(self, event: Dict):
        """Broadcast RFID event to WebSocket clients"""
        pass
    
    def register_handler(self, topic_pattern: str, handler: Callable):
        """Register a custom message handler for a topic pattern"""
        self.handlers[topic_pattern] = handler
        logger.info(f"Registered handler for topic pattern: {topic_pattern}")
    
    def publish(self, topic: str, payload: Dict):
        """Publish a message to an MQTT topic"""
        try:
            message = json.dumps(payload)
            self.client.publish(topic, message)
            logger.info(f"Published to '{topic}': {message}")
        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")
    
    def start(self):
        """Start the MQTT client"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            logger.info("MQTT client started")
        except Exception as e:
            logger.error(f"Failed to start MQTT client: {e}")
    
    def stop(self):
        """Stop the MQTT client"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT client stopped")
    
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self.connected
