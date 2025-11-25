#!/bin/bash

echo "🚀 Setting up FastAPI backend..."

# Create database (adjust credentials as needed)
echo "📦 Creating database..."
echo "Please enter your PostgreSQL password when prompted:"
psql -U postgres -c "CREATE DATABASE fastapi_db;" 2>/dev/null || echo "Database may already exist"

# Optional: Seed database
if [ "$1" = "--seed" ]; then
    echo "🌱 Seeding database..."
    venv/bin/python seed.py
fi

# Start the application
echo "🎯 Starting FastAPI server..."
venv/bin/uvicorn app.main:app --reload
