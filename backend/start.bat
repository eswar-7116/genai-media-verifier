@echo off
REM Quick deployment script for V.E.R.I.T.A.S Backend (Windows)

echo 🚀 V.E.R.I.T.A.S Backend - Quick Deploy
echo ======================================
echo.

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created. Please edit it with your settings.
    echo.
)

REM Check Python version
echo 🐍 Checking Python version...
python --version
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
echo.

REM Create uploads directory
echo 📁 Creating uploads directory...
if not exist uploads mkdir uploads
echo.

REM Run the server
echo 🎯 Starting server...
echo    Access at: http://localhost:8000
echo    Health check: http://localhost:8000/health
echo    API docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

python main.py
