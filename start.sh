#!/bin/bash

# Quick Start Script for Real-time Computer Vision System
# Run this script to set up and start the project

set -e  # Exit on error

echo "🎬 Real-time Computer Vision System - Quick Start"
echo "=================================================="
echo ""

# Check Python version
echo "✓ Checking Python installation..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.8+"; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "✓ Installing dependencies (this may take 2-3 minutes)..."
pip install -r requirements.txt > /dev/null 2>&1

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🚀 Starting the application..."
echo "📍 Open your browser to: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python app.py
