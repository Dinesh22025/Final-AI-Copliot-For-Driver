# 🚀 Quick Start Guide - Driver AI Co-Pilot

## ✅ Easy Startup (Recommended)

### Option 1: Start Everything at Once
1. Double-click `START-APP.bat`
2. Wait for both servers to start
3. Open browser: http://localhost:5173
4. Login: demo@example.com / demo123

### Option 2: Start Separately
1. Double-click `start-backend.bat` (starts backend)
2. Double-click `start-frontend.bat` (starts frontend)
3. Open browser: http://localhost:5173
4. Login: demo@example.com / demo123

## 📋 Manual Startup

### Backend:
```bash
cd backend
python run.py
```

### Frontend:
```bash
cd frontend
npm run dev
```

## 🔧 Troubleshooting

### Issue: "Initializing..." stuck on dashboard

**Solution 1: Check Browser Console**
1. Press F12 to open Developer Tools
2. Go to Console tab
3. Look for error messages
4. Common errors:
   - "Camera access denied" → Allow camera permission
   - "Network error" → Backend not running
   - "401 Unauthorized" → Login again

**Solution 2: Check Camera Permission**
1. Click the camera icon in browser address bar
2. Select "Always allow"
3. Refresh the page

**Solution 3: Verify Backend is Running**
1. Open http://localhost:5000/health
2. Should see: `{"status": "ok", "database": "sqlite"}`
3. If not, restart backend

**Solution 4: Check Network Tab**
1. Press F12 → Network tab
2. Look for `/api/monitor/analyze` requests
3. Check if they're returning 200 OK
4. If 401: Login again
5. If 500: Check backend console for errors

### Issue: Backend won't start

**Solution 1: Check Python**
```bash
python --version
# Should show Python 3.11 or higher
```

**Solution 2: Reinstall Dependencies**
```bash
cd backend
python -m pip install -r requirements.txt
```

**Solution 3: Check Port 5000**
```bash
# Kill any process using port 5000
netstat -ano | findstr :5000
# Note the PID and kill it
taskkill /PID <PID> /F
```

### Issue: Frontend won't start

**Solution 1: Check Node.js**
```bash
node --version
npm --version
```

**Solution 2: Reinstall Dependencies**
```bash
cd frontend
rm -rf node_modules
npm install
```

**Solution 3: Check Port 5173**
```bash
# Kill any process using port 5173
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Issue: Camera not working

**Checklist:**
- [ ] Camera permission allowed in browser
- [ ] No other app using camera (Zoom, Teams, etc.)
- [ ] Camera drivers installed
- [ ] Try different browser (Chrome recommended)
- [ ] Check browser console for specific error

**Test Camera:**
1. Go to https://webcamtests.com/
2. If camera works there, issue is with the app
3. If camera doesn't work, issue is with system/browser

### Issue: No face detected

**Solutions:**
- Ensure good lighting
- Face the camera directly
- Move closer to camera
- Remove glasses if detection fails
- Check if video feed is showing

### Issue: Alerts not working

**Checklist:**
- [ ] Browser sound not muted
- [ ] System volume not muted
- [ ] Check browser console for audio errors
- [ ] Try clicking on page first (browsers block audio until user interaction)

## 🧪 Testing

### Test Backend:
```bash
cd backend
python test_backend.py
```

Should show:
```
[PASS] Imports
[PASS] Database File
[PASS] Database Operations
[PASS] Authentication
[PASS] Vision System
[PASS] Routes
```

### Test MediaPipe:
```bash
cd backend
python test_mediapipe.py
```

Should show:
```
[OK] MediaPipe imported successfully
[OK] FaceMesh initialized successfully
[OK] OpenCV imported successfully
[OK] Face cascade loaded successfully
```

## 📊 Verify Everything is Working

### 1. Backend Health Check
Open: http://localhost:5000/health
Expected: `{"status": "ok", "database": "sqlite"}`

### 2. Frontend Loading
Open: http://localhost:5173
Expected: Login page appears

### 3. Login Test
- Email: demo@example.com
- Password: demo123
Expected: Dashboard loads

### 4. Camera Test
- Allow camera permission
- Video feed should appear
- Status should change from "Initializing..."

### 5. Detection Test
- Look at camera normally → Status: "focused"
- Close eyes → Status: "drowsy" + beeping
- Look away → Status: "distracted" + beeping
- Open mouth wide → Status: "yawning" + beeping

### 6. History Test
- Click "history" in sidebar
- Should see recorded events
- Click "Clear All History" to test deletion

## 🔍 Debug Mode

### Enable Detailed Logging:

**Backend:**
Edit `backend/run.py`:
```python
app.run(host="0.0.0.0", port=5000, debug=True)
```

**Frontend:**
Open browser console (F12) to see:
- Camera access logs
- Frame analysis logs
- API request/response logs

## 📞 Common Error Messages

### "Token is missing"
- **Cause:** Not logged in
- **Fix:** Go to login page and login again

### "Camera access denied"
- **Cause:** Browser blocked camera
- **Fix:** Click camera icon in address bar → Allow

### "Network Error"
- **Cause:** Backend not running
- **Fix:** Start backend with `start-backend.bat`

### "FileNotFoundError: mediapipe"
- **Cause:** MediaPipe installation corrupted
- **Fix:** `pip uninstall mediapipe && pip install mediapipe==0.10.14`

### "Port already in use"
- **Cause:** Another process using the port
- **Fix:** Kill the process or use different port

## 🎯 Performance Tips

1. **Better Detection:**
   - Use good lighting
   - Face camera directly
   - Keep face 1-2 feet from camera

2. **Faster Analysis:**
   - Close other browser tabs
   - Close other camera apps
   - Use Chrome for best performance

3. **Reduce False Alerts:**
   - Adjust lighting
   - Position camera at eye level
   - Avoid sudden movements

## 📱 Browser Compatibility

✅ **Recommended:**
- Chrome 90+
- Edge 90+

⚠️ **Limited Support:**
- Firefox 88+ (may have camera issues)
- Safari 14+ (may have audio issues)

❌ **Not Supported:**
- Internet Explorer
- Old browser versions

## 🆘 Still Having Issues?

1. **Check all logs:**
   - Backend console
   - Frontend console (F12)
   - Browser console

2. **Restart everything:**
   - Close all terminals
   - Close browser
   - Run `START-APP.bat` again

3. **Clean restart:**
   ```bash
   # Backend
   cd backend
   rm -rf instance/driver_monitor.db
   python run.py
   
   # Frontend
   cd frontend
   rm -rf node_modules
   npm install
   npm run dev
   ```

4. **Check system requirements:**
   - Python 3.11+
   - Node.js 16+
   - Webcam connected
   - 4GB+ RAM
   - Windows 10/11

---

**Last Updated:** 2026-03-12
**Version:** 1.0.0
**Status:** Production Ready ✅
