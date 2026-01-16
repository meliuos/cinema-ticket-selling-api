@echo off
echo 🚀 Setting up FastAPI backend...

REM --- Create database ---
echo 📦 Creating database...
echo Please enter your PostgreSQL password when prompted:
psql -U postgres -c "CREATE DATABASE fastapi_db;" 2>nul || echo Database may already exist

REM --- Optional: seed database ---
if "%1" == "--seed" (
    echo 🌱 Seeding database...
    venv\Scripts\python.exe seed.py
)

REM --- Start FastAPI server ---
echo 🎯 Starting FastAPI server...
venv\Scripts\uvicorn.exe app.main:app --reload
