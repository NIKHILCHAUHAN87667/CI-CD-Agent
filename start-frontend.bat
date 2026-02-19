@echo off
REM Startup script for frontend
cd /d "%~dp0frontend"
npm run dev -- --port 3001
pause
