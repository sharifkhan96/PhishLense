#!/bin/bash

# PhishLense Quick Start Script
# This script helps you set up the project quickly

echo "🛡️  PhishLense Quick Start"
echo "=========================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file..."
    cp backend/env.example backend/.env
    echo "⚠️  IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY"
    echo ""
fi

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "To start the backend server, run:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""

# Frontend setup
cd ../frontend
echo "⚛️  Setting up React frontend..."
echo "Installing Node dependencies..."
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "To start the frontend, run:"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "=========================="
echo "🎉 Setup complete!"
echo ""
echo "Don't forget to:"
echo "  1. Add your OPENAI_API_KEY to backend/.env"
echo "  2. Start the backend: cd backend && source venv/bin/activate && python manage.py runserver"
echo "  3. Start the frontend: cd frontend && npm start"
echo ""


