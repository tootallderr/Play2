#!/bin/bash

# Ollama Setup Script for LLM Media Player

echo "🦙 Setting up Ollama for LLM Media Player..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama installed successfully!"
    else
        echo "❌ Failed to install Ollama. Please install manually."
        exit 1
    fi
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service
echo "🚀 Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for server to start
echo "⏳ Waiting for Ollama server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama server is running!"
else
    echo "❌ Failed to start Ollama server"
    exit 1
fi

# Function to pull a model
pull_model() {
    local model=$1
    echo "📥 Pulling model: $model..."
    ollama pull $model
    if [ $? -eq 0 ]; then
        echo "✅ Successfully pulled $model"
        return 0
    else
        echo "❌ Failed to pull $model"
        return 1
    fi
}

# Pull recommended models
echo ""
echo "🎯 Recommended models for LLM Media Player:"
echo "1. llama3.2 (4.3GB) - Fast and efficient"
echo "2. llama3.2:3b (2.0GB) - Smaller, faster"
echo "3. phi3 (2.3GB) - Microsoft's efficient model"
echo "4. gemma2 (5.4GB) - Google's model"
echo ""

read -p "Which model would you like to pull? (1-4, or 'skip'): " choice

case $choice in
    1)
        pull_model "llama3.2"
        ;;
    2)
        pull_model "llama3.2:3b"
        ;;
    3)
        pull_model "phi3"
        ;;
    4)
        pull_model "gemma2"
        ;;
    skip)
        echo "⏭️ Skipping model download"
        ;;
    *)
        echo "⚠️ Invalid choice. You can pull models later with: ollama pull <model-name>"
        ;;
esac

echo ""
echo "🎉 Ollama setup complete!"
echo "📋 Available commands:"
echo "   ollama list          - List installed models"
echo "   ollama pull <model>  - Download a new model"
echo "   ollama serve         - Start Ollama server"
echo ""
echo "🔧 Your LLM Media Player is now configured to use Ollama!"
echo "   Start the application with: ./start.sh"
