from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional, Dict
from pydantic import BaseModel
import os
import asyncio

router = APIRouter()

# This will be injected from main.py
subtitle_processor = None

def set_subtitle_processor(processor):
    global subtitle_processor
    subtitle_processor = processor

class TransformRequest(BaseModel):
    subtitle_path: str
    mode: str
    batch_size: Optional[int] = 5

class ExportRequest(BaseModel):
    subtitle_path: str
    mode: str
    output_format: Optional[str] = 'srt'

@router.get("/modes")
async def get_caption_modes():
    """Get available caption transformation modes"""
    if not subtitle_processor:
        raise HTTPException(status_code=500, detail="Subtitle processor not initialized")
    
    modes = subtitle_processor.get_available_modes()
    return {"modes": modes}

@router.post("/transform")
async def transform_captions(request: TransformRequest):
    """Transform subtitles using specified mode"""
    if not subtitle_processor:
        raise HTTPException(status_code=500, detail="Subtitle processor not initialized")
    
    if not os.path.exists(request.subtitle_path):
        raise HTTPException(status_code=404, detail="Subtitle file not found")
    
    try:
        result = await subtitle_processor.transform_subtitles(
            request.subtitle_path, 
            request.mode, 
            request.batch_size
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {"result": result, "status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")

@router.get("/stream/{cache_key}")
async def stream_transformed_captions(cache_key: str, format: str = Query("vtt")):
    """Stream transformed captions by cache key"""
    if not subtitle_processor:
        raise HTTPException(status_code=500, detail="Subtitle processor not initialized")
    
    cache_path = subtitle_processor._get_cache_path(cache_key)
    
    if not cache_path.exists():
        raise HTTPException(status_code=404, detail="Transformed captions not found")
    
    try:
        # Load cached transformation
        import json
        with open(cache_path, 'r') as f:
            cached_data = json.load(f)
        
        # Create temporary subtitle file in requested format
        temp_dir = subtitle_processor.cache_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / f"{cache_key}.{format}"
        
        # Export to temporary file
        if subtitle_processor.export_subtitles(cached_data, str(temp_file), format):
            return FileResponse(
                str(temp_file),
                media_type=f"text/{format}",
                headers={"Content-Disposition": f"inline; filename=captions.{format}"}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to export captions")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming captions: {str(e)}")

@router.post("/export")
async def export_transformed_captions(request: ExportRequest):
    """Export transformed captions to file"""
    if not subtitle_processor:
        raise HTTPException(status_code=500, detail="Subtitle processor not initialized")
    
    if not os.path.exists(request.subtitle_path):
        raise HTTPException(status_code=404, detail="Subtitle file not found")
    
    try:
        # Transform if not already cached
        result = await subtitle_processor.transform_subtitles(request.subtitle_path, request.mode)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Generate output filename
        input_path = os.path.splitext(request.subtitle_path)[0]
        output_path = f"{input_path}_{request.mode}.{request.output_format}"
        
        # Export to file
        if subtitle_processor.export_subtitles(result, output_path, request.output_format):
            return {
                "output_path": output_path,
                "mode": request.mode,
                "format": request.output_format,
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to export captions")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/info/{subtitle_path:path}")
async def get_subtitle_info(subtitle_path: str):
    """Get information about a subtitle file"""
    if not subtitle_processor:
        raise HTTPException(status_code=500, detail="Subtitle processor not initialized")
    
    if not os.path.exists(subtitle_path):
        raise HTTPException(status_code=404, detail="Subtitle file not found")
    
    try:
        info = subtitle_processor.get_subtitle_info(subtitle_path)
        
        if "error" in info:
            raise HTTPException(status_code=400, detail=info["error"])
        
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze subtitle file: {str(e)}")

@router.delete("/cache/{cache_key}")
async def clear_caption_cache(cache_key: str):
    """Clear cached transformation result"""
    if not subtitle_processor:
        raise HTTPException(status_code=500, detail="Subtitle processor not initialized")
    
    cache_path = subtitle_processor._get_cache_path(cache_key)
    
    if cache_path.exists():
        cache_path.unlink()
        return {"message": "Cache cleared", "cache_key": cache_key}
    else:
        raise HTTPException(status_code=404, detail="Cache entry not found")

@router.delete("/cache")
async def clear_all_caption_cache():
    """Clear all cached transformation results"""
    if not subtitle_processor:
        raise HTTPException(status_code=500, detail="Subtitle processor not initialized")
    
    cache_dir = subtitle_processor.cache_dir
    cleared_count = 0
    
    for cache_file in cache_dir.glob("*.json"):
        cache_file.unlink()
        cleared_count += 1
    
    return {"message": f"Cleared {cleared_count} cache entries"}
