@echo off
echo ================================================
echo Starting Driver AI Co-Pilot Frontend
echo ================================================
echo.

cd /d "%~dp0frontend"

echo Checking Node.js installation...
node --version
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo Checking npm installation...
npm --version
if errorlevel 1 (
    echo ERROR: npm is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
echo Dependencies OK
echo.

echo ================================================
echo Starting Vite Dev Server on http://localhost:5173
echo ================================================
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause
