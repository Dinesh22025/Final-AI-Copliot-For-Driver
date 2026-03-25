@echo off
echo ================================================
echo Driver AI Co-Pilot - Complete Startup
echo ================================================
echo.
echo This will start both Backend and Frontend servers
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Starting Backend Server...
start "Backend Server" cmd /k "%~dp0start-backend.bat"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server...
start "Frontend Server" cmd /k "%~dp0start-frontend.bat"

echo.
echo ================================================
echo Both servers are starting!
echo ================================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Login with:
echo   Email: demo@example.com
echo   Password: demo123
echo.
echo Close this window or press any key to exit...
pause >nul
