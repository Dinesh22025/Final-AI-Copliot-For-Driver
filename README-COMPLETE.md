# 🚗 Driver AI Co-Pilot - Complete Setup Guide

A real-time driver monitoring system with facial expression analysis, drowsiness detection, and intelligent alerting.

## 🎯 Features

✅ **Real-time Face Detection** - Detects driver's face and facial landmarks
✅ **Drowsiness Detection** - Monitors eye closure (EAR < 0.28)
✅ **Yawning Detection** - Detects yawning with jaw movement analysis
✅ **Distraction Detection** - Tracks head pose and gaze direction
✅ **Continuous Alerts** - Loud beeping until driver returns to focused state
✅ **History Tracking** - Persistent SQLite database with event history
✅ **User Authentication** - Secure JWT-based login system
✅ **Responsive UI** - Modern React interface with real-time updates

## 🚀 Quick Start (3 Steps)

### Step 1: Install Requirements
- Python 3.11+
- Node.js 16+
- Webcam

### Step 2: Start the Application
Double-click: **`START-APP.bat`**

### Step 3: Open Browser
1. Go to: http://localhost:5173
2. Login: `demo@example.com` / `demo123`
3. Allow camera permission
4. Start monitoring!

## 📁 Project Structure

```
driver-ai-copilot/
├── backend/                    # Flask API Server
│   ├── app/
│   │   ├── __init__.py        # Flask app initialization
│   │   ├── auth.py            # JWT authentication
│   │   ├── database.py        # SQLite database operations
│   │   ├── routes.py          # API endpoints
│   │   └── vision.py          # Face detection & analysis
│   ├── instance/
│   │   └── driver_monitor.db  # SQLite database
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                 # Server entry point
│   ├── test_backend.py        # Backend tests
│   └── test_mediapipe.py      # MediaPipe tests
├── frontend/                   # React/Vite Application
│   ├── src/
│   │   └── pages/
│   │       ├── App.jsx        # Main app component
│   │       ├── dashboard.jsx  # Live monitoring dashboard
│   │       ├── historypage.jsx # Event history
│   │       ├── authpage.jsx   # Login/signup
│   │       └── api.js         # API client
│   ├── package.json
│   └── vite.config.js
├── START-APP.bat              # Start everything
├── start-backend.bat          # Start backend only
├── start-frontend.bat         # Start frontend only
├── TROUBLESHOOTING.md         # Detailed troubleshooting
└── README.md                  # This file
```

## 🔧 Manual Setup

### Backend Setup:
```bash
cd backend
python -m pip install -r requirements.txt
python test_backend.py  # Verify installation
python run.py           # Start server
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

## 🎮 How to Use

### 1. Login
- Use demo account: `demo@example.com` / `demo123`
- Or create new account via signup

### 2. Dashboard
- Allow camera permission when prompted
- Video feed will appear
- Real-time analysis starts automatically

### 3. Understanding Status

**🟢 Focused** - Normal driving, no alerts
- Eyes open
- Looking forward
- No yawning

**🔴 Drowsy** - Eyes closing detected
- EAR (Eye Aspect Ratio) < 0.28
- Continuous loud beeping
- Alert: "DROWSINESS ALERT! Eyes are closing. Please pull over and rest."

**🟠 Distracted** - Not looking at road
- Gaze offset > 8% or Head tilt > 7°
- Continuous beeping
- Alert: "ATTENTION! Keep your eyes on the road ahead."

**🔴 Yawning** - Fatigue detected
- MAR (Mouth Aspect Ratio) > 0.10 + Jaw movement
- Continuous beeping
- Alert: "FATIGUE DETECTED! Frequent yawning indicates tiredness. Take a break."

### 4. Alerts
- **Continuous beeping** starts when drowsy/distracted/yawning
- **Beeping stops** only when you return to focused state
- **Different durations:**
  - Drowsiness: 30 seconds
  - Distraction: 15 seconds
  - Yawning: 10 seconds

### 5. History
- Click "history" in sidebar
- View all detection events
- See detailed metrics (EAR, MAR, head tilt, gaze offset)
- Clear history with "Clear All History" button
- Auto-refreshes every 10 seconds

## 🔬 Technical Details

### Backend Technology
- **Framework:** Flask 3.0.3
- **Database:** SQLite (persistent storage)
- **Authentication:** JWT tokens (7-day expiration)
- **Computer Vision:**
  - MediaPipe 0.10.14 (facial landmarks)
  - OpenCV 4.10.0.84 (face/eye detection)
- **Password Security:** Werkzeug hashing

### Frontend Technology
- **Framework:** React 18 + Vite
- **API Client:** Axios
- **Audio:** Web Audio API (continuous beeping)
- **Video:** MediaDevices API (webcam access)

### Detection Algorithms

**Eye Aspect Ratio (EAR):**
```
EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
Drowsy if EAR < 0.28
```

**Mouth Aspect Ratio (MAR):**
```
MAR = vertical_distance / horizontal_distance
Yawning if MAR > 0.10 AND jaw_ratio > 0.45
```

**Head Pose:**
```
head_tilt = |left_eye.y - right_eye.y|
gaze_offset = |eye_center.x - nose.x|
Distracted if gaze > 8% OR tilt > 7%
```

### State Tracking
- **Sustained Detection:** Requires multiple consecutive frames
  - Drowsiness: 2+ frames
  - Yawning: 3+ frames
  - Distraction: 4+ frames
- **Priority System:** Drowsy > Distracted > Yawning > Focused
- **Auto-reset:** Counters reset after 3+ focused frames

## 📊 API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/me` - Get current user

### Monitoring
- `POST /api/monitor/analyze` - Analyze video frame
  ```json
  Request: { "frame": "data:image/jpeg;base64,..." }
  Response: {
    "analysis": {
      "status": "focused|drowsy|distracted|yawning",
      "confidence": 0.85,
      "head_tilt": 2.5,
      "gaze_offset": 3.2,
      "faces": 1,
      "ear": 0.25,
      "mar": 0.05
    },
    "alert": {
      "active": true,
      "durationSeconds": 30,
      "message": "Alert message"
    }
  }
  ```

### History
- `GET /api/history` - Get detection events
- `DELETE /api/history/clear` - Clear history

### Settings
- `PUT /api/settings` - Update user settings

### Health
- `GET /health` - Server status check

## 🧪 Testing

### Run All Tests:
```bash
cd backend
python test_backend.py
```

Expected output:
```
[PASS] Imports
[PASS] Database File
[PASS] Database Operations
[PASS] Authentication
[PASS] Vision System
[PASS] Routes

[SUCCESS] All tests passed! Backend is ready.
```

### Test MediaPipe:
```bash
cd backend
python test_mediapipe.py
```

### Test Frontend:
1. Open http://localhost:5173
2. Open browser console (F12)
3. Check for logs:
   - "Camera access granted"
   - "Video playing"
   - "Analyzing frame: 1280x720"
   - "Analysis result: focused"

## 🐛 Troubleshooting

See **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for detailed solutions.

### Quick Fixes:

**Dashboard stuck on "Initializing..."**
1. Check browser console (F12) for errors
2. Verify backend is running (http://localhost:5000/health)
3. Allow camera permission
4. Refresh page

**No alerts/beeping**
1. Unmute browser/system
2. Click on page first (browsers block audio until interaction)
3. Check browser console for audio errors

**Backend won't start**
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```

**Frontend won't start**
```bash
cd frontend
npm install
npm run dev
```

## 📈 Performance Tips

1. **Better Detection:**
   - Good lighting (avoid backlighting)
   - Face camera directly
   - Distance: 1-2 feet from camera
   - Camera at eye level

2. **Faster Processing:**
   - Close other browser tabs
   - Close other camera apps
   - Use Chrome for best performance

3. **Reduce False Alerts:**
   - Stable camera position
   - Avoid sudden movements
   - Consistent lighting

## 🔒 Security

- ✅ Passwords hashed with Werkzeug
- ✅ JWT tokens with 7-day expiration
- ✅ Protected API endpoints
- ✅ CORS enabled for development
- ✅ No sensitive data in logs

## 📝 Database Schema

### Users Table:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    driver_id TEXT UNIQUE NOT NULL,
    language TEXT DEFAULT 'en',
    alert_volume INTEGER DEFAULT 80,
    theme TEXT DEFAULT 'dark',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Detection Events Table:
```sql
CREATE TABLE detection_events (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    event_type TEXT NOT NULL,
    confidence REAL NOT NULL,
    head_tilt REAL DEFAULT 0,
    gaze_offset REAL DEFAULT 0,
    faces INTEGER DEFAULT 0,
    ear REAL DEFAULT 0,
    mar REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

## 🌐 Browser Support

✅ **Recommended:**
- Chrome 90+
- Edge 90+

⚠️ **Limited:**
- Firefox 88+
- Safari 14+

❌ **Not Supported:**
- Internet Explorer

## 📦 Dependencies

### Backend (Python):
```
Flask==3.0.3
Flask-Cors==4.0.1
PyJWT==2.8.0
Werkzeug==3.0.3
opencv-python==4.10.0.84
mediapipe==0.10.14
numpy==1.26.4
```

### Frontend (Node.js):
```
react: ^18.2.0
vite: ^5.0.0
axios: ^1.6.0
```

## 🎓 How It Works

1. **Video Capture:** Webcam streams video to browser
2. **Frame Extraction:** Canvas captures frames every 1 second
3. **API Call:** Frame sent to backend as base64 JPEG
4. **Face Detection:** MediaPipe detects 468 facial landmarks
5. **Analysis:** Calculate EAR, MAR, head pose, gaze direction
6. **State Detection:** Determine if drowsy/distracted/yawning
7. **Alert System:** Trigger continuous beeping if needed
8. **Database:** Save event to SQLite with full metrics
9. **UI Update:** Display status and metrics in real-time

## 📄 License

This project is for educational purposes.

## 👥 Demo Account

- **Email:** demo@example.com
- **Password:** demo123
- **Driver ID:** DEMO001

## 🆘 Support

If you encounter issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Check browser console (F12)
3. Check backend console
4. Run `python test_backend.py`

---

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Last Updated:** 2026-03-12
