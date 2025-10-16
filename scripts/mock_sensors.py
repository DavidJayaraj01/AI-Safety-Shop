#!/usr/bin/env python3
"""
Mock Sensor Data Publisher
Simulates ESP32 sensor data for testing without hardware
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Sensor simulation parameters
SENSORS = {
    "gas": {
        "topic": "sensors/gas",
        "min": 50,
        "max": 600,
        "unit": "PPM",
        "critical_threshold": 500
    },
    "temperature": {
        "topic": "sensors/temperature",
        "min": 20,
        "max": 70,
        "unit": "°C",
        "critical_threshold": 60
    },
    "vibration": {
        "topic": "sensors/vibration",
        "min": 0,
        "max": 20,
        "unit": "m/s²",
        "critical_threshold": 15
    },
    "ultrasonic": {
        "topic": "sensors/ultrasonic",
        "min": 10,
        "max": 400,
        "unit": "cm",
        "warning_threshold": 100
    },
    "environmental": {
        "topic": "sensors/environment",
        "min": 30,
        "max": 80,
        "unit": "%",
        "key": "humidity"
    }
}

WORKERS = [
    {"id": "worker_001", "name": "John Doe"},
    {"id": "worker_002", "name": "Jane Smith"},
    {"id": "worker_003", "name": "Bob Johnson"},
]

LOCATIONS = ["Production Floor", "Machine Bay", "Assembly Line", "Warehouse", "Entry Gate"]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    print(f"⚠️  Disconnected from MQTT Broker")

def generate_sensor_value(sensor_type, trend="normal"):
    """Generate realistic sensor values with trends"""
    config = SENSORS[sensor_type]
    
    if trend == "normal":
        # Normal operation - stay below warning threshold
        if sensor_type == "ultrasonic":
            return random.randint(150, config["max"])
        else:
            warning = config.get("critical_threshold", config["max"]) * 0.6
            return random.uniform(config["min"], warning)
    
    elif trend == "warning":
        # Warning level
        warning = config.get("critical_threshold", config["max"]) * 0.7
        critical = config.get("critical_threshold", config["max"]) * 0.9
        return random.uniform(warning, critical)
    
    elif trend == "critical":
        # Critical level
        critical = config.get("critical_threshold", config["max"])
        return random.uniform(critical, config["max"])
    
    elif trend == "spike":
        # Sudden spike
        return random.uniform(config["max"] * 0.9, config["max"])

def publish_sensor_data(client, sensor_type, trend="normal"):
    """Publish sensor data to MQTT"""
    config = SENSORS[sensor_type]
    value = generate_sensor_value(sensor_type, trend)
    location = random.choice(LOCATIONS)
    
    if sensor_type == "environmental":
        payload = {
            "sensor_id": f"{sensor_type}_sensor_1",
            config["key"]: round(value, 2),
            "location": location
        }
    else:
        payload = {
            "sensor_id": f"{sensor_type}_sensor_1",
            "value": round(value, 2),
            "location": location
        }
    
    message = json.dumps(payload)
    client.publish(config["topic"], message)
    
    # Color-coded output
    if value > config.get("critical_threshold", float('inf')):
        status = "🔴 CRITICAL"
    elif value > config.get("warning_threshold", config.get("critical_threshold", float('inf')) * 0.6):
        status = "🟡 WARNING"
    else:
        status = "🟢 NORMAL"
    
    print(f"{status} [{sensor_type.upper()}] {value:.2f} {config['unit']} at {location}")

def publish_rfid_event(client):
    """Simulate RFID entry/exit event"""
    worker = random.choice(WORKERS)
    event_type = random.choice(["entry", "exit"])
    location = "Main Gate" if random.random() > 0.3 else random.choice(["Side Gate", "Emergency Exit"])
    
    payload = {
        "worker_id": worker["id"],
        "worker_name": worker["name"],
        "event_type": event_type,
        "location": location,
        "access_granted": True
    }
    
    message = json.dumps(payload)
    client.publish(f"rfid/{event_type}", message)
    
    print(f"🔑 RFID: {worker['name']} - {event_type.upper()} at {location}")

def main():
    print("🚀 Mock Sensor Data Publisher")
    print("=" * 50)
    print(f"📡 Connecting to MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print()
    
    # Create MQTT client
    client = mqtt.Client(client_id="mock_esp32_sensors")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        print("✨ Publishing sensor data every 5 seconds...")
        print("📊 Simulating realistic scenarios:")
        print("   - Normal operation (70%)")
        print("   - Warning levels (20%)")
        print("   - Critical alerts (10%)")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 50)
        print()
        
        cycle = 0
        while True:
            cycle += 1
            
            # Determine trend for this cycle
            rand = random.random()
            if rand < 0.70:
                trend = "normal"
            elif rand < 0.90:
                trend = "warning"
            else:
                trend = "critical"
            
            # Publish all sensor data
            for sensor_type in SENSORS.keys():
                publish_sensor_data(client, sensor_type, trend)
                time.sleep(0.5)  # Stagger publications
            
            # Occasionally publish RFID events
            if cycle % 4 == 0:  # Every 4th cycle
                publish_rfid_event(client)
            
            print(f"\n--- Cycle {cycle} complete at {datetime.now().strftime('%H:%M:%S')} ---\n")
            time.sleep(5)  # Wait 5 seconds before next cycle
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopping mock sensor publisher...")
        client.loop_stop()
        client.disconnect()
        print("✅ Disconnected from MQTT Broker")
        print("Goodbye!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
