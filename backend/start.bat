@echo off
REM Quick start script for AI DevOps Agent (Windows)

echo 🚀 Starting AI DevOps Agent...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create workspace directory
if not exist "workspace" mkdir workspace

REM Run the server
echo.
echo ✅ Starting server on http://localhost:8000
echo 📚 API docs available at http://localhost:8000/docs
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
