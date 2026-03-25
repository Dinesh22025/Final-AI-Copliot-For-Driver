@echo off
echo ========================================
echo   DRIVER AI CO-PILOT - STARTING
echo ========================================
echo.

echo [1/2] Starting Backend on port 8000...
start "Backend Server" cmd /k "cd backend && python main.py"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend on port 5173...
start "Frontend Server" cmd /k "npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   SERVERS STARTED!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to open browser...
pause >nul
start http://localhost:5173
