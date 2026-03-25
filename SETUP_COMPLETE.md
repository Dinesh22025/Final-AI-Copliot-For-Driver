# 🚗 Driver AI Co-Pilot - FINAL SETUP

## ✅ SYSTEM STATUS
- ✓ Backend: FastAPI on port 8000
- ✓ Frontend: Vite/React on port 5173
- ✓ Database: SQLite (Fresh)
- ✓ Cascade Files: Downloaded to backend/cascades/
- ✓ Face Detection: OpenCV Ready
- ✓ All Dependencies: Installed

---

## 🚀 QUICK START (EASIEST WAY)

### Double-click: `START.bat`

This will:
1. Start backend server
2. Start frontend server
3. Open browser automatically

---

## 🔧 MANUAL START (If needed)

### Terminal 1 - Backend:
```bash
cd backend
python main.py
```
**Wait for:** `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2 - Frontend:
```bash
npm run dev
```
**Wait for:** `Local: http://localhost:5173/`

---

## 📱 ACCESS THE APP

**URL:** http://localhost:5173

### First Time Setup:
1. Click "Sign up"
2. Enter:
   - Name: Your Name
   - Email: test@test.com
   - Password: test123
3. Click "Create account"
4. **Allow camera access** when browser asks

---

## 🎯 HOW TO TEST

### 1. Normal State (Focused)
- Look straight at camera
- Status: **focused** (Green)
- No alerts

### 2. Tired
- Close eyes for 1-2 seconds
- Status: **tired** (Light Red)
- Beep: 800ms interval
- Voice: "You look tired! Take a break soon!"

### 3. Drowsy
- Close eyes for 3-4 seconds
- Status: **drowsy** (Red)
- Beep: 500ms interval
- Voice: "Wake up! You are getting drowsy!"

### 4. Sleeping
- Close eyes for 5+ seconds
- Status: **sleeping** (Dark Red)
- Beep: 300ms interval (VERY FAST)
- Voice: "Wake up immediately! Pull over now!"

### 5. Distracted
- Turn head left/right
- Move face off-center
- Status: **distracted** (Yellow)
- Beep: 600ms interval
- Voice: "Look at the camera! Do not get distracted!"

### 6. Yawning
- Open mouth wide
- Status: **yawning** (Orange)
- Beep: 600ms interval
- Voice: "You are tired! Take a break!"

---

## 📊 CHECK IF WORKING

### Backend Terminal Should Show:
```
Initializing DriverMonitor...
Loading cascades from: ...
Face file exists: True
Eye file exists: True
✓ OpenCV cascades loaded successfully
✓ DriverMonitor ready!
Uvicorn running on http://0.0.0.0:8000

=== ANALYZE CALLED ===
Frame shape: (720, 1280, 3)
DEBUG: Detected 1 faces, 2 eyes
DEBUG: FINAL STATUS = focused
```

### Browser Console Should Show:
```
Status: focused Faces: 1 Alert: false
```

### Dashboard Should Show:
```
Status: focused
Confidence: 70.0%
Head Tilt: 0-5°
Gaze Offset: 0-10%
Faces: 1
EAR: 0.3
MAR: 0.05
```

---

## 🔍 TROUBLESHOOTING

### Problem: "Faces: 0"
**Solution:**
1. Improve lighting (turn on lights)
2. Move closer to camera
3. Center your face in video
4. Refresh browser (F5)

### Problem: No beep sound
**Solution:**
1. Check browser volume
2. Check system volume
3. Try clicking on the page first (browser audio policy)
4. Check browser console for errors

### Problem: Backend won't start
**Solution:**
1. Check if port 8000 is free: `netstat -ano | findstr :8000`
2. Kill Python processes: `taskkill /F /IM python.exe`
3. Restart backend

### Problem: Frontend won't start
**Solution:**
1. Check if port 5173 is free
2. Run: `npm install`
3. Restart frontend

### Problem: Database error
**Solution:**
```bash
cd backend
del instance\driver_monitor.db
python main.py
```
(Creates fresh database)

---

## 📁 PROJECT STRUCTURE

```
driver-ai-copilot/
├── backend/
│   ├── cascades/              # OpenCV cascade files
│   ├── app/
│   │   ├── vision.py          # Face detection logic
│   │   ├── database.py        # SQLite database
│   │   ├── auth_fastapi.py    # JWT authentication
│   │   └── __init__.py
│   ├── instance/
│   │   └── driver_monitor.db  # SQLite database file
│   ├── main.py                # FastAPI server
│   └── requirements-fastapi.txt
├── frontend/
│   ├── src/
│   │   └── pages/
│   │       ├── dashboard.jsx  # Main monitoring page
│   │       ├── api.js         # API client
│   │       └── ...
│   ├── package.json
│   └── vite.config.js
├── START.bat                  # Quick start script
└── SETUP_COMPLETE.md          # This file
```

---

## 🎉 FEATURES

✅ Real-time face detection  
✅ Eye tracking (EAR - Eye Aspect Ratio)  
✅ Mouth tracking (MAR - Mouth Aspect Ratio)  
✅ Head tilt detection  
✅ Gaze offset tracking  
✅ 6 states: Focused, Tired, Drowsy, Sleeping, Distracted, Yawning  
✅ Continuous beep alerts (different speeds)  
✅ Voice alerts (Text-to-Speech)  
✅ Alert history with timestamps  
✅ User authentication (JWT)  
✅ SQLite database  
✅ Responsive UI  

---

## 🔐 DEMO ACCOUNTS

After creating fresh database, no demo accounts exist.
**Create your own account** on first run.

---

## 💡 TIPS

1. **Good Lighting**: Face detection works best with good lighting
2. **Camera Position**: Keep camera at eye level
3. **Distance**: Sit 50-100cm from camera
4. **Background**: Plain background works best
5. **Glasses**: Detection works with glasses
6. **Multiple Faces**: System tracks only the first detected face

---

## 🛠️ TECH STACK

- **Backend**: FastAPI, OpenCV, SQLite
- **Frontend**: React, Vite, Axios
- **Detection**: OpenCV Haar Cascades
- **Audio**: Web Audio API
- **Voice**: Web Speech API
- **Auth**: JWT tokens

---

## ✅ SYSTEM IS READY!

**Just run:** `START.bat`

**Or manually start both servers and access:** http://localhost:5173

**Enjoy your Driver AI Co-Pilot!** 🚗💨
