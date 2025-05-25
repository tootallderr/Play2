#!/bin/bash

# LLM Media Player & Library Manager Start Script

echo "🎬 Starting LLM Media Player & Library Manager..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./setup.sh first."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Kill existing processes on our ports
echo "🧹 Cleaning up existing processes..."
if check_port 8000; then
    echo "Stopping existing backend server on port 8000..."
    pkill -f "uvicorn main:app" || true
fi

if check_port 3000; then
    echo "Stopping existing frontend server on port 3000..."
    pkill -f "next dev" || true
fi

# Wait a moment for processes to fully stop
sleep 2

# Start backend
echo "🐍 Starting FastAPI backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment and start server
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend started successfully
if ! check_port 8000; then
    echo "❌ Backend failed to start on port 8000"
    exit 1
fi

echo "✅ Backend server running on http://localhost:8000"

# Start frontend
echo "🌐 Starting Next.js frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 10

# Check if frontend started successfully
if ! check_port 3000; then
    echo "❌ Frontend failed to start on port 3000"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Frontend server running on http://localhost:3000"
echo ""
echo "🎉 LLM Media Player is now running!"
echo ""
echo "📝 Access points:"
echo "   🌐 Web Interface: http://localhost:3000"
echo "   🔧 API Docs: http://localhost:8000/docs"
echo "   ❤️  Health Check: http://localhost:8000/health"
echo ""
echo "🛑 To stop the servers, press Ctrl+C"
echo ""

# Wait for user interrupt
trap 'echo ""; echo "🛑 Shutting down servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; echo "👋 Goodbye!"; exit 0' INT

# Keep script running
wait
