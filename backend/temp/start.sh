#!/bin/bash
# Quick deployment script for V.E.R.I.T.A.S Backend

echo "🚀 V.E.R.I.T.A.S Backend - Quick Deploy"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your settings."
    echo ""
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo ""

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads
echo ""

# Run the server
echo "🎯 Starting server..."
echo "   Access at: http://localhost:8000"
echo "   Health check: http://localhost:8000/health"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 main.py
