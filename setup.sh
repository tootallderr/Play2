#!/bin/bash

# LLM Media Player & Library Manager Setup Script

echo "🎬 Setting up LLM Media Player & Library Manager..."

# Check dependencies
echo "📋 Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is required but not installed."
    echo "Install with: sudo apt-get install ffmpeg (Ubuntu/Debian) or brew install ffmpeg (macOS)"
    exit 1
fi

echo "✅ All dependencies found!"

# Setup environment file
echo "🔧 Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file from template. Please edit it with your API keys and settings."
else
    echo "⚠️  .env file already exists, skipping..."
fi

# Install backend dependencies
echo "🐍 Installing Python backend dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "🔧 Activating virtual environment and installing packages..."
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
deactivate

cd ..

# Install frontend dependencies
echo "📦 Installing Node.js frontend dependencies..."
cd frontend
npm install
cd ..

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/cache
mkdir -p data/media

# Set permissions
chmod -R 755 data/

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Edit the .env file with your API keys:"
echo "   - OPENAI_API_KEY (for GPT-4 caption transformations)"
echo "   - TMDB_API_KEY (for movie/TV metadata)"
echo "   - WATCHED_DIRS (comma-separated paths to your media folders)"
echo ""
echo "2. Start the application:"
echo "   ./start.sh"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "🎬 Enjoy your AI-powered media center!"
