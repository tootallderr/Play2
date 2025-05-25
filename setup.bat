@echo off

echo 🎬 Setting up LLM Media Player ^& Library Manager...

:: Check dependencies
echo 📋 Checking dependencies...

:: Check Python
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is required but not installed.
    echo Download and install from https://www.python.org/downloads/
    exit /b 1
)

:: Check Node.js
node --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Node.js is required but not installed.
    echo Download and install from https://nodejs.org/
    exit /b 1
)

:: Check ffmpeg
ffmpeg -version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ ffmpeg is required but not installed.
    echo Download and install from https://ffmpeg.org/download.html
    echo or install with: choco install ffmpeg (if using Chocolatey)
    exit /b 1
)

echo ✅ All dependencies found!

:: Setup environment file
echo 🔧 Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo 📝 Created .env file from template. Please edit it with your API keys and settings.
) else (
    echo ⚠️ .env file already exists, skipping...
)

:: Install backend dependencies
echo 🐍 Installing Python backend dependencies...
cd backend

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
echo 🔧 Activating virtual environment and installing packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
call deactivate.bat

cd ..

:: Install frontend dependencies
echo 📦 Installing Node.js frontend dependencies...
cd frontend
call npm install
cd ..

:: Create data directories
echo 📁 Creating data directories...
if not exist "data\cache" mkdir "data\cache"
if not exist "data\media" mkdir "data\media"

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📝 Next steps:
echo 1. Edit the .env file with your API keys:
echo    - OPENAI_API_KEY (for GPT-4 caption transformations)
echo    - TMDB_API_KEY (for movie/TV metadata)
echo    - WATCHED_DIRS (comma-separated paths to your media folders)
echo.
echo 2. Start the application:
echo    start.bat
echo.
echo 3. Open http://localhost:3000 in your browser
echo.
echo 🎬 Enjoy your AI-powered media center!

pause
