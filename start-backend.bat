@echo off
REM Startup script for backend with workspace exclusion
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --reload --port 8000 --reload-dir app
pause
