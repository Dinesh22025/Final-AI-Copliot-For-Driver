@echo off
echo ============================================================
echo DRIVER AI CO-PILOT - STARTING APPLICATION
echo ============================================================
echo.

REM Kill any existing Python and Node processes
echo [1/4] Stopping existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start backend in new window
echo [2/4] Starting backend server (FastAPI on port 8000)...
start "Driver AI Backend" cmd /k "cd backend && python main.py"
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo [3/4] Starting frontend server (Vite on port 5173)...
start "Driver AI Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 5 /nobreak >nul

REM Open browser
echo [4/4] Opening browser...
start http://localhost:5173

echo.
echo ============================================================
echo APPLICATION STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop all servers...
pause >nul

REM Stop servers when user presses a key
echo.
echo Stopping servers...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
echo Done!
