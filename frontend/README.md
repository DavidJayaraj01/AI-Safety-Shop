# 🎨 Frontend - AI-Smarter-Shop Safety Monitoring System

React + TypeScript + Vite frontend application for real-time IoT sensor monitoring and safety management dashboard.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Pages](#pages)
- [Components](#components)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Styling](#styling)
- [Building for Production](#building-for-production)
- [Deployment](#deployment)

---

## 🎯 Overview

The frontend provides a modern, responsive dashboard for:
- **Real-time sensor monitoring** with live Arduino data
- **Computer vision monitoring** with camera feeds and violation tracking
- **Reports and analytics** with interactive charts
- **Alert management** with notifications and acknowledgment
- **Dark/Light mode** with user preference persistence
- **Dual operating modes** (Shop Floor / Heavy Industry)

---

## ✨ Features

### 📊 Dashboard
- **Live Sensor Cards**: Real-time data from Arduino (Gas, Temperature, Distance, RFID)
- **Status Indicators**: Color-coded status (Normal/Warning/Danger)
- **Real-time Charts**: Historical data visualization (last 20 points)
- **Alert Panel**: Active warnings and danger alerts
- **Statistics Overview**: Data points, active alerts, connectivity status
- **Auto-refresh**: Updates every 15 seconds

### 📹 CV Monitoring
- **Camera Grid**: 6 camera feeds with status indicators
- **Recent Violations**: Real-time safety violation list
- **Violation Details**: Detection type, severity, confidence, timestamp
- **Acknowledge Feature**: Mark violations as reviewed
- **Filtering**: By camera, type, severity
- **Statistics**: Total detections, by type, severity distribution

### 📈 Reports & Analytics
- **Summary Statistics**: Total violations, critical alerts, response time
- **Incident Trends**: Daily/weekly/monthly charts
- **Severity Distribution**: Pie chart breakdown
- **Time Period Filters**: Today, Week, Month, Quarter, Year
- **Incident List**: Detailed violation records
- **Auto-refresh**: Updates every 30 seconds

### ⚙️ Settings
- **Threshold Configuration**: Adjust sensor warning/danger levels
- **Alert Preferences**: Email, SMS, sound notifications
- **System Configuration**: Operating mode, dark mode
- **User Preferences**: Saved in local storage

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | React | 19.1.1 |
| **Language** | TypeScript | 5.9.3 |
| **Build Tool** | Vite | 7.1.7 |
| **Styling** | Tailwind CSS | 3.4 |
| **HTTP Client** | Axios | 1.12.2 |
| **Charts** | Recharts | 3.2.1 |
| **Icons** | Lucide React | 0.545.0 |
| **Notifications** | React Hot Toast | 2.6.0 |
| **Routing** | React Router DOM | 7.9.4 |
| **Headless UI** | @headlessui/react | 2.2.9 |

---

## 📁 Project Structure

```
frontend/
├── public/
│   ├── logo.png                # Application logo
│   └── vite.svg                # Vite icon
│
├── src/
│   ├── assets/
│   │   └── react.svg           # React logo
│   │
│   ├── components/             # Reusable UI components
│   │   ├── AlertPanel.tsx      # Active alerts display
│   │   ├── CameraFeed.tsx      # Camera video feed component
│   │   ├── Chart.tsx           # Recharts wrapper
│   │   ├── ModeSwitch.tsx      # Operating mode toggle
│   │   ├── Navbar.tsx          # Top navigation bar
│   │   ├── SensorCard.tsx      # Sensor data card
│   │   ├── Sidebar.tsx         # Side navigation menu
│   │   └── ViolationCard.tsx   # CV violation card
│   │
│   ├── context/                # React Context providers
│   │   ├── AlertContext.tsx    # Alert state management
│   │   └── ModeContext.tsx     # Operating mode state
│   │
│   ├── pages/                  # Main page components
│   │   ├── Dashboard.tsx       # Live sensor dashboard
│   │   ├── CVMonitoring.tsx    # Computer vision monitoring
│   │   ├── Reports.tsx         # Reports & analytics
│   │   └── Settings.tsx        # System settings
│   │
│   ├── services/               # API integration
│   │   └── api.ts              # Axios API client
│   │
│   ├── types/                  # TypeScript type definitions
│   │   └── index.ts            # Shared types and interfaces
│   │
│   ├── App.tsx                 # Main app component
│   ├── App.css                 # App styles
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles + Tailwind
│
├── .env                        # Environment variables (DO NOT COMMIT)
├── .gitignore                  # Git ignore rules
├── index.html                  # HTML template
├── package.json                # Dependencies
├── tailwind.config.js          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
└── README.md                   # This file
```

---

## 🚀 Installation

### Prerequisites

- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (comes with Node.js)

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Environment Setup

```bash
# Create environment file
cp .env.example .env

# Edit with your backend URL
nano .env
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000

# Optional: Custom configurations
VITE_WS_URL=ws://localhost:8000/ws
VITE_REFRESH_INTERVAL=15000
```

### Tailwind Configuration

Edit `tailwind.config.js` for custom colors, fonts, etc.:

```javascript
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          // ... custom colors
        }
      }
    }
  }
}
```

---

## 🏃 Running the Application

### Development Mode

```bash
# Start development server
npm run dev

# Access at: http://localhost:5173
```

The dev server features:
- **Hot Module Replacement (HMR)**: Instant updates
- **Fast Refresh**: Preserves component state
- **TypeScript**: Real-time type checking
- **ESLint**: Code quality checks

### Build for Production

```bash
# Create optimized production build
npm run build

# Output in: dist/
```

### Preview Production Build

```bash
# Preview the production build locally
npm run preview

# Access at: http://localhost:4173
```

---

## 📄 Pages

### 1. Dashboard (`/`)

**Purpose**: Real-time sensor monitoring

**Features**:
- Live sensor data cards (Temperature, Humidity, Gas, Distance, RFID)
- Color-coded status indicators
- Real-time line charts (last 20 data points)
- Active alert panel
- Connection status
- Statistics overview

**API Endpoints Used**:
- `GET /sensors/live/arduino` - Every 15 seconds

**Key Components**:
- `SensorCard` - Individual sensor display
- `Chart` - Line chart for trends
- `AlertPanel` - Active alerts

---

### 2. CV Monitoring (`/cv-monitoring`)

**Purpose**: Computer vision safety monitoring

**Features**:
- Camera grid (6 cameras)
- Camera status indicators (Online/Offline)
- Recent violations list
- Violation details (type, severity, confidence)
- Acknowledge violations
- Filter by camera, type, severity

**API Endpoints Used**:
- `GET /cv/cameras` - Camera list
- `GET /cv/detections?hours=24` - Recent detections
- `PATCH /cv/detections/{id}/acknowledge` - Acknowledge

**Key Components**:
- `CameraFeed` - Camera video display
- `ViolationCard` - Violation information

---

### 3. Reports (`/reports`)

**Purpose**: Analytics and historical data

**Features**:
- Summary statistics
- Incident trend charts
- Severity distribution pie chart
- Time period filters (Today, Week, Month, Quarter, Year)
- Detailed incident list
- Auto-refresh (30 seconds)

**API Endpoints Used**:
- `GET /reports/?period=week` - Summary
- `GET /reports/analytics?period=week` - Charts
- `GET /reports/list?period=week` - Incidents

**Key Components**:
- `Chart` - Line and pie charts
- Custom tables and cards

---

### 4. Settings (`/settings`)

**Purpose**: System configuration

**Features**:
- Sensor threshold adjustments
- Alert preference toggles
- Operating mode selection
- Dark/Light theme toggle
- Save preferences

**API Endpoints Used**:
- `GET /settings` - Current settings
- `PUT /settings` - Update settings

---

## 🧩 Components

### Core Components

#### `Navbar.tsx`
Top navigation bar with:
- Logo and title
- Page breadcrumb
- Connection status
- Alert count badge
- Dark mode toggle
- Settings button

#### `Sidebar.tsx`
Side navigation menu with:
- Operating mode indicator
- Navigation links (Dashboard, CV Monitoring, Reports, Settings)
- Active page highlighting
- Mobile responsive drawer

#### `SensorCard.tsx`
Sensor data display with:
```tsx
interface SensorCardProps {
  name: string;
  value: number | string;
  unit: string;
  status: 'normal' | 'warning' | 'danger';
  icon: ReactNode;
  threshold?: { warning: number; danger: number };
  lastUpdate: string;
  trend?: 'up' | 'down' | 'stable';
}
```

#### `Chart.tsx`
Recharts wrapper for:
- Line charts (trends)
- Pie charts (distribution)
- Bar charts (comparison)
- Responsive sizing
- Custom tooltips

#### `AlertPanel.tsx`
Active alerts with:
- Alert severity badges
- Timestamp display
- Acknowledge button
- Auto-dismissal
- Sound notifications

---

## 🔄 State Management

### Context API

#### ModeContext
```tsx
interface ModeContextType {
  mode: 'shop_floor' | 'heavy_industry';
  isDarkMode: boolean;
  modeConfig: {
    name: string;
    colors: { primary: string; accent: string };
    features: string[];
  };
  setMode: (mode: string) => void;
  toggleDarkMode: () => void;
}
```

**Usage**:
```tsx
import { useModeContext } from '../context/ModeContext';

const { mode, isDarkMode, toggleDarkMode } = useModeContext();
```

#### AlertContext
```tsx
interface AlertContextType {
  activeAlerts: Alert[];
  isConnected: boolean;
  addAlert: (alert: Alert) => void;
  removeAlert: (id: string) => void;
  clearAlerts: () => void;
}
```

**Usage**:
```tsx
import { useAlertContext } from '../context/AlertContext';

const { activeAlerts, isConnected } = useAlertContext();
```

---

## 🌐 API Integration

### API Service (`services/api.ts`)

Axios-based API client with:

```typescript
// Base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
});

// Sensor APIs
export const sensorsApi = {
  getAllSensors: () => api.get('/sensors'),
  getLiveArduinoData: () => api.get('/sensors/live/arduino'),
  getSensorHistory: (type?: string, hours = 24) => 
    api.get(`/sensors/${type}/history?hours=${hours}`)
};

// Arduino APIs
export const arduinoSensorsApi = {
  getLiveSensorData: () => api.get('/sensors/live/arduino'),
  getArduinoStatus: () => api.get('/api/arduino/status')
};

// CV APIs
export const cvApi = {
  getAllCameras: () => api.get('/cv/cameras'),
  getDetections: (params) => api.get('/cv/detections', { params }),
  acknowledgeDetection: (id) => api.patch(`/cv/detections/${id}/acknowledge`)
};

// Reports APIs
export const reportsApi = {
  getReport: (period) => api.get(`/reports?period=${period}`),
  getAnalytics: (period) => api.get(`/reports/analytics?period=${period}`)
};

// Alerts APIs
export const alertsApi = {
  getActiveAlerts: () => api.get('/alerts/active'),
  acknowledgeAlert: (id) => api.put(`/alerts/${id}/acknowledge`)
};
```

### Usage Example

```tsx
import { sensorsApi } from '../services/api';

const fetchSensorData = async () => {
  try {
    const response = await sensorsApi.getLiveArduinoData();
    setSensors(response.data.sensors);
  } catch (error) {
    console.error('Error fetching sensor data:', error);
    toast.error('Failed to fetch sensor data');
  }
};
```

---

## 🎨 Styling

### Tailwind CSS

**Utility-first CSS framework**:

```tsx
<div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
    Sensor Data
  </h2>
  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {/* Cards */}
  </div>
</div>
```

### Dark Mode

Implemented using Tailwind's `dark:` variant:

```tsx
// Toggle dark mode
const toggleDarkMode = () => {
  document.documentElement.classList.toggle('dark');
  localStorage.setItem('darkMode', isDarkMode ? 'false' : 'true');
};

// Check on mount
useEffect(() => {
  const savedMode = localStorage.getItem('darkMode');
  if (savedMode === 'true') {
    document.documentElement.classList.add('dark');
  }
}, []);
```

### Responsive Design

Mobile-first approach:

```tsx
<div className="
  grid 
  grid-cols-1          /* Mobile: 1 column */
  md:grid-cols-2       /* Tablet: 2 columns */
  lg:grid-cols-4       /* Desktop: 4 columns */
  gap-4
">
  {/* Content */}
</div>
```

---

## 📦 Building for Production

### Build Process

```bash
# Create optimized build
npm run build

# Output structure:
dist/
├── index.html          # Entry HTML
├── assets/
│   ├── index-[hash].js     # Main JS bundle
│   ├── index-[hash].css    # Compiled CSS
│   └── logo-[hash].png     # Optimized assets
└── favicon.ico
```

### Build Optimizations

Vite automatically applies:
- **Code splitting**: Lazy-loaded routes
- **Tree shaking**: Removes unused code
- **Minification**: Smaller bundle sizes
- **Asset optimization**: Compressed images
- **Cache busting**: Hash-based filenames

### Build Configuration

Edit `vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
});
```

---

## 🚀 Deployment

### Static Hosting (Vercel, Netlify)

```bash
# Build the project
npm run build

# Deploy dist/ folder to:
# - Vercel: vercel --prod
# - Netlify: netlify deploy --prod
# - GitHub Pages: Copy dist/ to gh-pages branch
```

### Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

`vercel.json`:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "framework": "vite"
}
```

### Netlify Deployment

`netlify.toml`:
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Docker Deployment

```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
# Build and run
docker build -t ai-safety-frontend .
docker run -p 80:80 ai-safety-frontend
```

### Nginx Configuration

```nginx
server {
  listen 80;
  root /usr/share/nginx/html;
  index index.html;

  # SPA routing
  location / {
    try_files $uri $uri/ /index.html;
  }

  # API proxy (optional)
  location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  # Caching
  location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }
}
```

---

## 🧪 Testing

### Linting

```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

### Type Checking

```bash
# Check types without building
tsc --noEmit
```

---

## 🔧 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
```

#### CORS Errors
Add proxy in `vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

#### Environment Variables Not Working
- Prefix with `VITE_`
- Restart dev server after changes
- Access with `import.meta.env.VITE_*`

---

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Recharts Documentation](https://recharts.org/)

---

## 🤝 Contributing

1. Follow React best practices
2. Use TypeScript for type safety
3. Follow component structure conventions
4. Keep components small and focused
5. Add JSDoc comments for complex logic
6. Test on mobile devices

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for safer workplaces**
