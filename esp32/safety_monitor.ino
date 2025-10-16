#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker
const char* mqtt_server = "YOUR_MQTT_BROKER_IP";
const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_password = "";

// Sensor Pins
#define GAS_SENSOR_PIN 34
#define TEMP_SENSOR_PIN 27
#define DHT_TYPE DHT22
#define VIBRATION_SENSOR_PIN 35
#define ULTRASONIC_TRIG_PIN 5
#define ULTRASONIC_ECHO_PIN 18
#define BUZZER_PIN 25
#define LED_PIN 2
#define RELAY_PIN 26

// RFID (Simulated with button for demo)
#define RFID_BUTTON_PIN 4

// Sensor objects
DHT dht(TEMP_SENSOR_PIN, DHT_TYPE);

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);

// Variables
unsigned long lastSensorRead = 0;
const long sensorInterval = 5000; // Read sensors every 5 seconds
bool systemShutdown = false;

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(GAS_SENSOR_PIN, INPUT);
  pinMode(VIBRATION_SENSOR_PIN, INPUT);
  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(RFID_BUTTON_PIN, INPUT_PULLUP);
  
  // Initialize sensors
  dht.begin();
  
  // Connect to WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);
  
  Serial.println("ESP32 Safety Monitor Initialized");
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Blink LED while connecting
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(LED_PIN, HIGH);
}

void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    String clientId = "ESP32-Safety-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      
      // Subscribe to control topics
      client.subscribe("control/#");
      
      digitalWrite(LED_PIN, HIGH);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      
      digitalWrite(LED_PIN, LOW);
      delay(5000);
    }
  }
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Parse JSON
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.print("JSON parsing failed: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Handle shutdown command
  if (String(topic) == "control/shutdown") {
    String command = doc["command"];
    if (command == "shutdown") {
      trigger_shutdown();
    }
  }
}

void loop() {
  // Maintain WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }
  
  // Maintain MQTT connection
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();
  
  // Read sensors periodically
  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorRead >= sensorInterval) {
    lastSensorRead = currentMillis;
    
    if (!systemShutdown) {
      read_and_publish_sensors();
    }
  }
  
  // Check RFID button (simulated)
  static bool lastButtonState = HIGH;
  bool buttonState = digitalRead(RFID_BUTTON_PIN);
  if (buttonState == LOW && lastButtonState == HIGH) {
    publish_rfid_event();
    delay(500); // Debounce
  }
  lastButtonState = buttonState;
}

void read_and_publish_sensors() {
  // Gas Sensor (MQ series - analog)
  int gasValue = analogRead(GAS_SENSOR_PIN);
  float gasPPM = map(gasValue, 0, 4095, 0, 1000); // Map to PPM
  publish_gas_sensor(gasPPM);
  
  // Temperature & Humidity
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  if (!isnan(temperature) && !isnan(humidity)) {
    publish_temperature_sensor(temperature);
    publish_environmental_sensor(humidity);
  }
  
  // Vibration Sensor
  int vibrationValue = analogRead(VIBRATION_SENSOR_PIN);
  float vibration = map(vibrationValue, 0, 4095, 0, 20) / 10.0; // Map to m/s²
  publish_vibration_sensor(vibration);
  
  // Ultrasonic Distance
  long distance = read_ultrasonic();
  publish_ultrasonic_sensor(distance);
  
  Serial.println("Sensors read and published");
}

long read_ultrasonic() {
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  
  long duration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH);
  long distance = duration * 0.034 / 2; // Convert to cm
  
  return distance;
}

void publish_gas_sensor(float value) {
  StaticJsonDocument<256> doc;
  doc["sensor_id"] = "gas_sensor_1";
  doc["value"] = value;
  doc["location"] = "Production Floor";
  
  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("sensors/gas", buffer);
  
  // Trigger local buzzer if critical
  if (value > 500) {
    tone(BUZZER_PIN, 2000, 500);
  }
}

void publish_temperature_sensor(float value) {
  StaticJsonDocument<256> doc;
  doc["sensor_id"] = "temp_sensor_1";
  doc["value"] = value;
  doc["location"] = "Production Floor";
  
  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("sensors/temperature", buffer);
}

void publish_vibration_sensor(float value) {
  StaticJsonDocument<256> doc;
  doc["sensor_id"] = "vib_sensor_1";
  doc["value"] = value;
  doc["location"] = "Machine Bay";
  
  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("sensors/vibration", buffer);
}

void publish_ultrasonic_sensor(long distance) {
  StaticJsonDocument<256> doc;
  doc["sensor_id"] = "ultrasonic_1";
  doc["distance"] = distance;
  doc["location"] = "Entry Gate";
  
  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("sensors/ultrasonic", buffer);
}

void publish_environmental_sensor(float humidity) {
  StaticJsonDocument<256> doc;
  doc["sensor_id"] = "env_sensor_1";
  doc["humidity"] = humidity;
  doc["location"] = "Production Floor";
  
  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("sensors/environment", buffer);
}

void publish_rfid_event() {
  StaticJsonDocument<256> doc;
  doc["worker_id"] = "worker_001";
  doc["worker_name"] = "John Doe";
  doc["event_type"] = "entry";
  doc["location"] = "Main Gate";
  doc["access_granted"] = true;
  
  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("rfid/entry", buffer);
  
  Serial.println("RFID event published");
  
  // Beep twice
  tone(BUZZER_PIN, 1000, 200);
  delay(300);
  tone(BUZZER_PIN, 1000, 200);
}

void trigger_shutdown() {
  Serial.println("EMERGENCY SHUTDOWN TRIGGERED!");
  systemShutdown = true;
  
  // Activate relay to cut power
  digitalWrite(RELAY_PIN, HIGH);
  
  // Sound alarm
  for (int i = 0; i < 5; i++) {
    tone(BUZZER_PIN, 3000, 500);
    digitalWrite(LED_PIN, HIGH);
    delay(500);
    digitalWrite(LED_PIN, LOW);
    delay(500);
  }
}
