import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.history = {}
        self.contamination = 0.1  # Expected proportion of outliers
        
    def add_reading(self, sensor_id: str, value: float, timestamp: datetime = None):
        """Add a new sensor reading to history"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if sensor_id not in self.history:
            self.history[sensor_id] = []
        
        self.history[sensor_id].append({
            'value': value,
            'timestamp': timestamp
        })
        
        # Keep only last 1000 readings per sensor
        if len(self.history[sensor_id]) > 1000:
            self.history[sensor_id] = self.history[sensor_id][-1000:]
    
    def train_model(self, sensor_id: str):
        """Train anomaly detection model for a specific sensor"""
        if sensor_id not in self.history or len(self.history[sensor_id]) < 50:
            logger.warning(f"Not enough data to train model for sensor {sensor_id}")
            return False
        
        try:
            # Prepare data
            values = np.array([r['value'] for r in self.history[sensor_id]]).reshape(-1, 1)
            
            # Scale data
            scaler = StandardScaler()
            scaled_values = scaler.fit_transform(values)
            
            # Train Isolation Forest
            model = IsolationForest(
                contamination=self.contamination,
                random_state=42
            )
            model.fit(scaled_values)
            
            # Store model and scaler
            self.models[sensor_id] = model
            self.scalers[sensor_id] = scaler
            
            logger.info(f"Anomaly detection model trained for sensor {sensor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error training model for sensor {sensor_id}: {e}")
            return False
    
    def detect_anomaly(self, sensor_id: str, value: float) -> Tuple[bool, float]:
        """
        Detect if a value is anomalous
        Returns: (is_anomaly, anomaly_score)
        """
        if sensor_id not in self.models:
            # Train model if not exists and enough data
            if sensor_id in self.history and len(self.history[sensor_id]) >= 50:
                self.train_model(sensor_id)
            else:
                return False, 0.0
        
        try:
            # Scale value
            scaler = self.scalers[sensor_id]
            scaled_value = scaler.transform([[value]])
            
            # Predict
            prediction = self.models[sensor_id].predict(scaled_value)[0]
            anomaly_score = self.models[sensor_id].score_samples(scaled_value)[0]
            
            is_anomaly = prediction == -1
            
            return is_anomaly, abs(float(anomaly_score))
            
        except Exception as e:
            logger.error(f"Error detecting anomaly for sensor {sensor_id}: {e}")
            return False, 0.0
    
    def predict_trend(self, sensor_id: str, forecast_minutes: int = 15) -> Dict:
        """
        Predict future values using simple moving average and trend analysis
        """
        if sensor_id not in self.history or len(self.history[sensor_id]) < 10:
            return None
        
        try:
            # Get recent readings
            recent_readings = self.history[sensor_id][-100:]
            values = [r['value'] for r in recent_readings]
            timestamps = [r['timestamp'] for r in recent_readings]
            
            # Calculate moving average
            window_size = min(10, len(values) // 2)
            ma = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
            
            # Calculate trend (simple linear regression)
            x = np.arange(len(values))
            coefficients = np.polyfit(x, values, 1)
            trend = coefficients[0]
            
            # Predict next value
            predicted_value = values[-1] + (trend * forecast_minutes / 5)  # Normalize by 5-minute intervals
            
            # Calculate confidence based on variance
            variance = np.var(values)
            confidence = 1.0 / (1.0 + variance)
            
            # Determine anomaly type
            if trend > 0.5:
                anomaly_type = 'spike'
            elif trend < -0.5:
                anomaly_type = 'drop'
            elif variance > np.mean(values) * 0.3:
                anomaly_type = 'pattern_break'
            else:
                anomaly_type = 'trend_change'
            
            return {
                'sensor_id': sensor_id,
                'current_value': values[-1],
                'predicted_value': predicted_value,
                'trend': trend,
                'confidence': min(confidence, 1.0),
                'forecast_minutes': forecast_minutes,
                'anomaly_type': anomaly_type,
                'variance': variance
            }
            
        except Exception as e:
            logger.error(f"Error predicting trend for sensor {sensor_id}: {e}")
            return None
    
    def get_forecast(self, sensor_id: str, minutes: int = 15) -> List[Dict]:
        """
        Get forecast for next N minutes
        """
        prediction = self.predict_trend(sensor_id, minutes)
        
        if not prediction:
            return []
        
        # Generate forecast points
        forecasts = []
        current_value = prediction['current_value']
        trend = prediction['trend']
        
        for i in range(1, minutes + 1):
            forecast_value = current_value + (trend * i / 5)
            forecasts.append({
                'timestamp': (datetime.utcnow() + timedelta(minutes=i)).isoformat(),
                'predicted_value': forecast_value,
                'confidence': prediction['confidence'] * (1 - i / minutes * 0.3)  # Decrease confidence over time
            })
        
        return forecasts
    
    def analyze_behavioral_pattern(self, worker_id: str, recent_actions: List[Dict]) -> Dict:
        """
        Analyze worker behavior patterns for unsafe actions
        """
        if len(recent_actions) < 5:
            return {'is_unsafe': False, 'confidence': 0.0}
        
        # Simple pattern analysis
        unsafe_indicators = 0
        total_checks = 0
        
        for action in recent_actions:
            total_checks += 1
            
            # Check PPE compliance
            if not action.get('ppe_compliance', True):
                unsafe_indicators += 1
            
            # Check proximity to hazards
            if action.get('proximity_alert', False):
                unsafe_indicators += 1
            
            # Check time in restricted zones
            if action.get('restricted_zone', False):
                unsafe_indicators += 1
        
        unsafe_ratio = unsafe_indicators / total_checks if total_checks > 0 else 0
        
        return {
            'worker_id': worker_id,
            'is_unsafe': unsafe_ratio > 0.3,
            'unsafe_ratio': unsafe_ratio,
            'confidence': min(len(recent_actions) / 20, 1.0),
            'recommendation': 'Immediate intervention required' if unsafe_ratio > 0.5 else 'Monitor closely'
        }
    
    def detect_equipment_fault(self, sensor_id: str, sensor_type: str) -> Dict:
        """
        Detect potential equipment faults based on vibration patterns
        """
        if sensor_type != 'vibration':
            return None
        
        if sensor_id not in self.history or len(self.history[sensor_id]) < 20:
            return None
        
        recent_readings = self.history[sensor_id][-50:]
        values = [r['value'] for r in recent_readings]
        
        # Calculate statistics
        mean = np.mean(values)
        std = np.std(values)
        peak = np.max(values)
        
        # Fault detection logic
        fault_detected = False
        fault_type = None
        severity = 'low'
        
        if std > mean * 0.5:
            fault_detected = True
            fault_type = 'irregular_vibration'
            severity = 'high'
        elif peak > mean * 2:
            fault_detected = True
            fault_type = 'vibration_spike'
            severity = 'medium'
        elif std > mean * 0.3:
            fault_detected = True
            fault_type = 'increasing_variation'
            severity = 'low'
        
        if fault_detected:
            return {
                'sensor_id': sensor_id,
                'fault_detected': True,
                'fault_type': fault_type,
                'severity': severity,
                'mean_vibration': mean,
                'std_deviation': std,
                'peak_value': peak,
                'recommendation': f'Schedule maintenance - {fault_type.replace("_", " ")}'
            }
        
        return None
