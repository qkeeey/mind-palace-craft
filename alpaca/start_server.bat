@echo off
REM Quick start script for MindPalace backend server

echo ============================================================
echo Starting MindPalace Backend Server
echo ============================================================
echo.

cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo Python found!
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo ============================================================
echo Starting API Server on http://localhost:8081
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python api_server.py

pause
