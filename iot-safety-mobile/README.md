# IoT Safety Monitoring - Mobile App

A React Native mobile application built with Expo for real-time IoT safety monitoring with Arduino sensors and computer vision.

## Features

### 🎯 Core Functionality
- **Real-time Sensor Monitoring**: Temperature, Humidity, Gas (MQ-135), Distance (HC-SR04), RFID
- **Computer Vision Monitoring**: 6 camera feeds with violation detection
- **Analytics & Reports**: Incident statistics, severity distribution, trend analysis
- **Push Notifications**: Critical alerts with deep linking
- **Offline Support**: Local caching with AsyncStorage
- **Dark/Light Theme**: Automatic theme switching

### 📱 Screens
1. **Dashboard**: Live sensor data with historical charts
2. **CV Monitoring**: Camera feeds and violation detections
3. **Reports**: Analytics with customizable time periods
4. **Settings**: Theme, thresholds, and notification preferences

## Tech Stack

- **Framework**: React Native + Expo
- **Language**: TypeScript
- **Navigation**: Expo Router (file-based routing)
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Charts**: react-native-chart-kit
- **Notifications**: expo-notifications
- **Storage**: AsyncStorage

## Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI
- iOS Simulator (Mac) or Android Emulator
- Backend FastAPI server running

## Installation

1. **Install Dependencies**
   ```bash
   cd iot-safety-mobile
   npm install
   ```

2. **Configure Backend URL**
   
   Edit `constants/theme.ts` and update the API_BASE_URL:
   ```typescript
   export const API_BASE_URL = 'http://YOUR_LOCAL_IP:8000';
   ```
   
   **Finding your local IP:**
   - **Linux/Mac**: `ifconfig` or `ip addr`
   - **Windows**: `ipconfig`
   - Look for your local network IP (e.g., 192.168.1.100)

3. **Update App Configuration**
   
   The `app.json` is already configured. If needed, update:
   - App name
   - Bundle identifier (iOS)
   - Package name (Android)

## Running the App

### Development Mode

```bash
npm start
```

This opens the Expo Dev Tools. Choose your platform:

### iOS (Mac only)
```bash
npm run ios
```

### Android
```bash
npm run android
```

### Web
```bash
npm run web
```

## Project Structure

```
iot-safety-mobile/
├── app/
│   ├── (tabs)/
│   │   ├── _layout.tsx       # Tab navigator
│   │   ├── index.tsx          # Dashboard screen
│   │   ├── monitoring.tsx     # CV Monitoring screen
│   │   ├── reports.tsx        # Reports screen
│   │   └── settings.tsx       # Settings screen
│   └── _layout.tsx            # Root layout
├── components/
│   ├── AlertBanner.tsx        # Alert notifications
│   ├── CameraCard.tsx         # Camera display card
│   ├── LiveChart.tsx          # Real-time charts
│   ├── SensorCard.tsx         # Sensor data card
│   ├── StatsCard.tsx          # Statistics card
│   ├── ThemeToggle.tsx        # Theme switcher
│   └── ViolationCard.tsx      # Violation detection card
├── services/
│   ├── api.ts                 # API service layer
│   └── notifications.ts       # Push notifications
├── store/
│   ├── sensorStore.ts         # Sensor state management
│   ├── cameraStore.ts         # Camera state management
│   └── settingsStore.ts       # Settings state management
├── types/
│   └── api.ts                 # TypeScript interfaces
├── constants/
│   └── theme.ts               # Theme & configuration
├── app.json                   # Expo configuration
├── package.json               # Dependencies
└── tsconfig.json              # TypeScript config
```

## API Endpoints

The app expects the following backend endpoints:

### Sensors
- `GET /sensors/live/arduino` - Live sensor data
  ```json
  {
    "sensors": {
      "temperature": { "value": 28.5, "unit": "°C", "status": "normal" },
      "humidity": { "value": 65, "unit": "%", "status": "normal" },
      "gas": { "value": 219, "unit": "ppm", "status": "normal" },
      "ultrasonic": { "value": 150, "unit": "cm", "status": "normal" },
      "rfid": { "value": "A1:B2:C3:D4", "status": "scanned" }
    },
    "timestamp": "2025-01-08T10:30:45.123Z"
  }
  ```

### Computer Vision
- `GET /cv/cameras` - Camera list
- `GET /cv/detections` - Recent violations
- `POST /cv/detections/:id/acknowledge` - Acknowledge violation

### Reports
- `GET /reports?period=week` - Analytics data

### Settings
- `GET /settings` - Get configuration
- `PUT /settings` - Update configuration

### Notifications
- `POST /notifications/register` - Register device token

## Features in Detail

### Auto-Refresh
- Dashboard and CV monitoring refresh every 15 seconds
- Pull-to-refresh gesture on all screens
- Configurable refresh interval in settings

### Notifications
- Critical sensor alerts
- CV violation detections
- Deep linking to relevant screens
- Foreground and background handling

### Offline Mode
- Detects network connectivity
- Shows offline banner
- Caches settings locally
- Graceful error handling

### Theme System
- Light mode
- Dark mode
- Auto (system default)
- Persistent theme preference

### Charts
- Live sensor trends (last 20 data points)
- Historical incident data
- Severity distribution (pie chart)
- Incidents by day (bar chart)

## Troubleshooting

### Cannot connect to backend
1. Verify backend is running on the correct port
2. Check firewall settings
3. Ensure mobile device and backend are on the same network
4. Update API_BASE_URL in `constants/theme.ts`

### Build errors
```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
npx expo start -c
```

### Type errors
```bash
# Regenerate TypeScript types
npx expo customize tsconfig.json
```

### Push notifications not working
1. Test on physical device (not simulator)
2. Grant notification permissions
3. Check backend notification endpoint
4. Verify Expo push token registration

## Performance Optimization

- **Memoization**: Charts and expensive components are memoized
- **Debouncing**: API calls are debounced
- **Lazy Loading**: Images load on demand
- **Optimized Re-renders**: Zustand selectors prevent unnecessary renders

## Configuration

### Changing Refresh Interval
Edit `constants/theme.ts`:
```typescript
export const REFRESH_INTERVAL = 15000; // milliseconds
```

### Customizing Colors
Edit `constants/theme.ts`:
```typescript
export const Colors = {
  light: {
    primary: '#3b82f6',  // Change primary color
    // ... other colors
  }
}
```

### Adjusting Thresholds
Use the Settings screen in the app or edit default values in `store/settingsStore.ts`

## Building for Production

### iOS
```bash
eas build --platform ios
```

### Android
```bash
eas build --platform android
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using React Native and Expo**
