from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api.library import router as library_router, set_media_scanner
from api.player import router as player_router
from api.captions import router as captions_router, set_subtitle_processor
from media_scanner.scanner import MediaScanner
from subtitle_engine.processor import SubtitleProcessor

load_dotenv()

# Global instances
media_scanner = None
subtitle_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global media_scanner, subtitle_processor
    
    # Initialize media scanner
    watched_dirs = os.getenv("WATCHED_DIRS", "").split(",")
    media_scanner = MediaScanner(watched_dirs)
    await media_scanner.start_monitoring()
    
    # Initialize subtitle processor
    subtitle_processor = SubtitleProcessor()
    
    # Inject dependencies into API routers
    set_media_scanner(media_scanner)
    set_subtitle_processor(subtitle_processor)
    
    print("🎬 LLM Media Player started successfully!")
    
    yield
    
    # Shutdown
    if media_scanner:
        await media_scanner.stop_monitoring()
    print("👋 Media Player shutting down...")

app = FastAPI(
    title="LLM Media Player & Library Manager",
    description="AI-powered media center with intelligent caption transformation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(library_router, prefix="/api/library", tags=["Library"])
app.include_router(player_router, prefix="/api/player", tags=["Player"])
app.include_router(captions_router, prefix="/api/captions", tags=["Captions"])

# Serve static files (media content)
media_dir = os.getenv("WATCHED_DIRS", "./data/media").split(",")[0]
if os.path.exists(media_dir):
    app.mount("/media", StaticFiles(directory=media_dir), name="media")
else:
    # Create media directory if it doesn't exist
    os.makedirs(media_dir, exist_ok=True)
    app.mount("/media", StaticFiles(directory=media_dir), name="media")

@app.get("/")
async def root():
    return {"message": "🎥 LLM Media Player & Library Manager", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "scanner_active": media_scanner is not None}

@app.get("/api/health")  # Separate route definition for frontend compatibility
async def api_health_check():
    return {"status": "healthy", "scanner_active": media_scanner is not None}

# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Keep connection alive and handle real-time updates
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
