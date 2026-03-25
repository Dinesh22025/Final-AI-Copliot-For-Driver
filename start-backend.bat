@echo off
echo ================================================
echo Starting Driver AI Co-Pilot Backend
echo ================================================
echo.

cd /d "%~dp0backend"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo Checking dependencies...
python -c "import flask, flask_cors, cv2, jwt, sqlite3" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
echo Dependencies OK
echo.

echo Testing backend components...
python test_backend.py
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed, but continuing...
    echo.
)

echo.
echo ================================================
echo Starting Flask Server on http://localhost:5000
echo ================================================
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py

pause
