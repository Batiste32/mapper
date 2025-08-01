@echo off
echo Activating virtual environment...
call .venv\Scripts\activate

echo Setting working directory...
cd /d %~dp0

echo Setting PYTHONPATH...
set PYTHONPATH=%cd%

echo Running backend.ngrok_tunneler...
python backend/ngrok_tunneler.py

pause
