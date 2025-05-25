@echo off
setlocal enabledelayedexpansion

echo LLM Media Player ^& Library Manager - Universal Launcher

:: Detect operating system
echo Detecting operating system...

:: Check if we're on Windows
if defined OS (
    if "!OS:Windows=!" neq "%OS%" (
        echo Detected Windows OS
        goto :windows_setup
    )
)

:: Check for macOS or Linux
where bash >nul 2>&1
if %ERRORLEVEL% equ 0 (
    :: Determine if macOS or Linux
    bash -c "uname" > %TEMP%\ostype.txt
    set /p OSTYPE=<%TEMP%\ostype.txt
    del %TEMP%\ostype.txt
    
    if "!OSTYPE!"=="Darwin" (
        echo Detected macOS
        goto :mac_setup
    ) else if "!OSTYPE!"=="Linux" (
        echo Detected Linux
        goto :linux_setup
    )
)

echo Unknown operating system
echo Please run this project on Windows, macOS, or Linux
pause
exit /b 1

:windows_setup
echo Starting on Windows...

:: Check if .env exists, create it if needed
if not exist .env (
    echo .env file not found. Creating one...
    if exist .env.example (
        copy .env.example .env
        echo Created .env from template
    ) else (
        echo OLLAMA_HOST=http://localhost:11434 > .env
        echo OLLAMA_MODEL=llama3.2 >> .env
        echo TMDB_API_KEY= >> .env
        echo CAPTION_MODE_CACHE_DIR=./data/cache >> .env
        echo WATCHED_DIRS= >> .env
        echo DATABASE_URL=sqlite:///./data/media_library.db >> .env
        echo CORS_ORIGINS=http://localhost:3000 >> .env
        echo Created default .env file
    )
    echo Please edit your .env file with your API keys and settings
)

:: Check and install dependencies if needed
echo Checking dependencies...

:: Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is required but not installed
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Node.js is required but not installed
    echo Please install Node.js from https://nodejs.org/
    start https://nodejs.org/
    pause
    exit /b 1
)

:: Check FFmpeg
ffmpeg -version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo FFmpeg is required but not installed
    echo.
    choice /C 123 /M "Options: [1] Download pre-built FFmpeg, [2] Clone and build from source, [3] Skip"
    if %ERRORLEVEL% equ 1 (
        echo Downloading pre-built FFmpeg...
        mkdir temp_ffmpeg 2>nul
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'temp_ffmpeg\ffmpeg.zip'"
        powershell -Command "Expand-Archive -Path 'temp_ffmpeg\ffmpeg.zip' -DestinationPath 'temp_ffmpeg' -Force"
        mkdir tools\ffmpeg 2>nul
        xcopy /E /Y temp_ffmpeg\ffmpeg-master-latest-win64-gpl\bin\*.* tools\ffmpeg\
        echo Adding FFmpeg to PATH for this session...
        set "PATH=%CD%\tools\ffmpeg;%PATH%"
        echo FFmpeg installed successfully
        rmdir /S /Q temp_ffmpeg
    ) else if %ERRORLEVEL% equ 2 (
        echo Cloning FFmpeg source code...
        where git >nul 2>&1
        if %ERRORLEVEL% neq 0 (
            echo Git is required to clone FFmpeg but is not installed
            pause
            exit /b 1
        )
        mkdir tools 2>nul
        cd tools
        git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg-source
        echo.
        echo FFmpeg source code has been cloned to tools\ffmpeg-source
        echo You need to manually build FFmpeg following the instructions at:
        echo https://trac.ffmpeg.org/wiki/CompilationGuide/MSVC
        cd ..
        pause
        exit /b 1
    ) else (
        echo Continuing without FFmpeg. Some features may not work correctly.
    )
)

:: Setup backend if needed
if not exist backend\venv (
    echo Setting up backend...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
    echo Backend setup complete
)

:: Setup frontend if needed
if not exist frontend\node_modules (
    echo Setting up frontend...
    cd frontend
    npm install
    cd ..
    echo Frontend setup complete
)

:: Create data directories
if not exist data\cache mkdir data\cache
if not exist data\media mkdir data\media

goto :start_app

:mac_setup
echo Starting on macOS...
bash -c "chmod +x ./start.sh && ./start.sh"
exit /b %ERRORLEVEL%

:linux_setup
echo Starting on Linux...
bash -c "chmod +x ./start.sh && ./start.sh"
exit /b %ERRORLEVEL%

:start_app
:: Check if Ollama is running
echo Checking Ollama server...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Ollama server is not running!
    
    where ollama >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Ollama does not appear to be installed
        echo Would you like to download and install Ollama?
        choice /C YN /M "Download Ollama now?"
        if %ERRORLEVEL% equ 1 (
            echo Opening Ollama website...
            start https://ollama.ai
            echo Please run the installer, then restart this script
            pause
            exit /b 1
        ) else (
            echo Continuing without Ollama (you can install it later)...
        )
    ) else (
        echo Starting Ollama server...
        start /B ollama serve
        timeout /t 5 /nobreak >nul
    )
) else (
    echo Ollama server is running
    :: Check if we have any models
    ollama list | findstr "NAME" >nul
    if %ERRORLEVEL% equ 0 (
        echo Ollama models available
    ) else (
        echo No Ollama models found. 
        choice /C YN /M "Pull recommended model (llama3.2) now?"
        if %ERRORLEVEL% equ 1 (
            echo Pulling llama3.2 model...
            ollama pull llama3.2
            if %ERRORLEVEL% equ 0 (
                echo Successfully pulled llama3.2
            ) else (
                echo Failed to pull llama3.2
            )
        )
    )
)

:: Function to check if port is in use and kill processes
set PORT_IN_USE=0
netstat -ano | findstr ":8000" >nul
if %ERRORLEVEL% equ 0 (
    set PORT_IN_USE=1
)

:: Kill existing processes on our ports
echo Cleaning up existing processes...
if !PORT_IN_USE! equ 1 (
    echo Stopping existing backend server on port 8000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)

set PORT_IN_USE=0
netstat -ano | findstr ":3000" >nul
if %ERRORLEVEL% equ 0 (
    set PORT_IN_USE=1
)

if !PORT_IN_USE! equ 1 (
    echo Stopping existing frontend server on port 3000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: Wait a moment for processes to fully stop
timeout /t 2 /nobreak >nul

:: Start backend
echo Starting FastAPI backend server...
cd backend

:: Activate virtual environment and start server
call venv\Scripts\activate.bat
start /B cmd /c "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
cd ..

:: Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Check if backend started successfully
netstat -ano | findstr ":8000" >nul
if %ERRORLEVEL% neq 0 (
    echo Backend failed to start on port 8000
    echo Check backend\venv and try running setup.bat
    pause
    exit /b 1
)

echo Backend server running on http://localhost:8000

:: Start frontend
echo Starting Next.js frontend server...
cd frontend
start /B cmd /c "npm run dev"
cd ..

:: Wait for frontend to start
echo Waiting for frontend to initialize...
timeout /t 10 /nobreak >nul

:: Check if frontend started successfully
netstat -ano | findstr ":3000" >nul
if %ERRORLEVEL% neq 0 (
    echo Frontend failed to start on port 3000
    echo Check frontend\node_modules and try running setup.bat
    pause
    exit /b 1
)

echo Frontend server running on http://localhost:3000
echo.
echo LLM Media Player is now running!
echo.
echo Access points:
echo    Web Interface: http://localhost:3000
echo    API Docs: http://localhost:8000/docs
echo    Health Check: http://localhost:8000/health
echo.
echo To stop the servers, close this window or press Ctrl+C

:: Open browser automatically
start http://localhost:3000

:: Keep script running
pause >nul
