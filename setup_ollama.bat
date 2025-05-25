@echo off
setlocal enabledelayedexpansion

echo 🦙 Setting up Ollama for LLM Media Player...

:: Check if Ollama is installed
where ollama > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 📥 Please install Ollama...
    echo Visit: https://ollama.ai
    echo.
    echo After installing, please run this script again.
    pause
    exit /b 1
) else (
    echo ✅ Ollama is already installed
)

:: Start Ollama service
echo 🚀 Starting Ollama server...
start /B ollama serve

:: Wait for server to start
echo ⏳ Waiting for Ollama server to start...
timeout /t 5 /nobreak > nul

:: Check if server is running
curl -s http://localhost:11434/api/tags > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start Ollama server
    exit /b 1
) else (
    echo ✅ Ollama server is running!
)

:: Pull recommended models
echo.
echo 🎯 Recommended models for LLM Media Player:
echo 1. llama3.2 (4.3GB) - Fast and efficient
echo 2. llama3.2:3b (2.0GB) - Smaller, faster
echo 3. phi3 (2.3GB) - Microsoft's efficient model
echo 4. gemma2 (5.4GB) - Google's model
echo.

set /p choice="Which model would you like to pull? (1-4, or 'skip'): "

set MODEL=none
if "%choice%"=="1" set MODEL=llama3.2
if "%choice%"=="2" set MODEL=llama3.2:3b
if "%choice%"=="3" set MODEL=phi3
if "%choice%"=="4" set MODEL=gemma2

if "%MODEL%"=="none" (
    if "%choice%"=="skip" (
        echo ⏭️ Skipping model download
    ) else (
        echo ⚠️ Invalid choice. You can pull models later with: ollama pull ^<model-name^>
    )
) else (
    echo 📥 Pulling model: %MODEL%...
    ollama pull %MODEL%
    if %ERRORLEVEL% equ 0 (
        echo ✅ Successfully pulled %MODEL%
    ) else (
        echo ❌ Failed to pull %MODEL%
    )
)

echo.
echo 🎉 Ollama setup complete!
echo 📋 Available commands:
echo    ollama list          - List installed models
echo    ollama pull ^<model^>  - Download a new model
echo    ollama serve         - Start Ollama server
echo.
echo 🔧 Your LLM Media Player is now configured to use Ollama!
echo    Start the application with: start.bat

pause
