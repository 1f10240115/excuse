@echo off
echo Starting FastAPI Backend...
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001
pause 