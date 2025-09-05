@echo off
setlocal

echo Starting Remorph API...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Create necessary directories
if not exist "data" mkdir data
if not exist "weights" mkdir weights
if not exist "outputs" mkdir outputs

REM Start the API server
echo Starting Remorph API server...
echo Server will be available at: http://127.0.0.1:8080/docs
echo Press Ctrl+C to stop the server
echo.

uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload

pause