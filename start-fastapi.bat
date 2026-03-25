@echo off
echo ================================================
echo Starting Driver AI Co-Pilot with FastAPI
echo ================================================
echo.

cd /d "%~dp0backend"

echo Installing FastAPI dependencies...
python -m pip install -r requirements-fastapi.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Testing backend...
python test_backend.py
echo.

echo ================================================
echo Starting FastAPI Server on http://localhost:5000
echo ================================================
echo.
echo API Documentation: http://localhost:5000/docs
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
