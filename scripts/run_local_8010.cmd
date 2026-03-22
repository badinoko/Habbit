@echo off
setlocal

cd /d "%~dp0.."

echo Starting HabitFlow on http://127.0.0.1:8010 with reload...
echo Keep this window open while testing the site.
echo.

".venv\Scripts\python.exe" ".venv\Scripts\uvicorn.exe" src.main:app --host 127.0.0.1 --port 8010 --reload

endlocal
