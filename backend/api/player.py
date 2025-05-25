from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import os
import asyncio
from pathlib import Path

router = APIRouter()

@router.get("/stream/{item_id:path}")
async def stream_media(item_id: str, range: Optional[str] = None):
    """Stream media file with range support for video playback"""
    
    # Verify file exists and is accessible
    if not os.path.exists(item_id):
        raise HTTPException(status_code=404, detail="Media file not found")
    
    file_size = os.path.getsize(item_id)
    
    # Handle range requests for video streaming
    if range:
        try:
            # Parse range header (e.g., "bytes=0-1023")
            range_match = range.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1
            
            # Ensure valid range
            start = max(0, start)
            end = min(file_size - 1, end)
            content_length = end - start + 1
            
            def iter_file(file_path: str, start: int, end: int, chunk_size: int = 8192):
                """Generator to stream file in chunks"""
                with open(file_path, 'rb') as f:
                    f.seek(start)
                    remaining = end - start + 1
                    while remaining:
                        chunk_size = min(chunk_size, remaining)
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk
            
            headers = {
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(content_length),
                'Content-Type': 'video/mp4'
            }
            
            return StreamingResponse(
                iter_file(item_id, start, end),
                status_code=206,
                headers=headers
            )
            
        except ValueError:
            # Invalid range, return full file
            pass
    
    # Return full file
    return FileResponse(
        item_id,
        media_type='video/mp4',
        headers={'Accept-Ranges': 'bytes'}
    )

@router.get("/info/{item_id:path}")
async def get_media_info(item_id: str):
    """Get technical information about a media file"""
    
    if not os.path.exists(item_id):
        raise HTTPException(status_code=404, detail="Media file not found")
    
    try:
        import subprocess
        import json
        
        # Use ffprobe to get media information
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', item_id
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Failed to analyze media file")
        
        media_info = json.loads(result.stdout)
        
        # Extract useful information
        format_info = media_info.get('format', {})
        streams = media_info.get('streams', [])
        
        video_streams = [s for s in streams if s.get('codec_type') == 'video']
        audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
        subtitle_streams = [s for s in streams if s.get('codec_type') == 'subtitle']
        
        return {
            "file_path": item_id,
            "file_size": os.path.getsize(item_id),
            "duration": float(format_info.get('duration', 0)),
            "format_name": format_info.get('format_name', ''),
            "bit_rate": int(format_info.get('bit_rate', 0)),
            "video_streams": [{
                "codec": stream.get('codec_name'),
                "width": stream.get('width'),
                "height": stream.get('height'),
                "fps": eval(stream.get('r_frame_rate', '0/1')) if '/' in str(stream.get('r_frame_rate', '')) else 0
            } for stream in video_streams],
            "audio_streams": [{
                "codec": stream.get('codec_name'),
                "channels": stream.get('channels'),
                "sample_rate": stream.get('sample_rate'),
                "language": stream.get('tags', {}).get('language', 'unknown')
            } for stream in audio_streams],
            "subtitle_streams": [{
                "codec": stream.get('codec_name'),
                "language": stream.get('tags', {}).get('language', 'unknown')
            } for stream in subtitle_streams],
            "has_chapters": len(format_info.get('chapters', [])) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing media: {str(e)}")

@router.post("/skip-intro/{item_id:path}")
async def skip_intro(item_id: str):
    """Get intro skip information for a media file"""
    
    # This is a placeholder for intro detection logic
    # In a real implementation, you'd use ML models or crowd-sourced data
    
    return {
        "has_intro": True,
        "intro_start": 0,
        "intro_end": 90,  # 90 seconds
        "confidence": 0.85,
        "skip_message": "Skip intro"
    }

@router.post("/chapters/{item_id:path}")
async def get_chapters(item_id: str):
    """Get chapter information for a media file"""
    
    if not os.path.exists(item_id):
        raise HTTPException(status_code=404, detail="Media file not found")
    
    try:
        import subprocess
        import json
        
        # Use ffprobe to get chapter information
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_chapters', item_id
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            chapter_info = json.loads(result.stdout)
            chapters = chapter_info.get('chapters', [])
            
            formatted_chapters = []
            for i, chapter in enumerate(chapters):
                formatted_chapters.append({
                    "id": i,
                    "title": chapter.get('tags', {}).get('title', f"Chapter {i+1}"),
                    "start_time": float(chapter.get('start_time', 0)),
                    "end_time": float(chapter.get('end_time', 0))
                })
            
            return {
                "chapters": formatted_chapters,
                "count": len(formatted_chapters)
            }
        else:
            # No chapters found or error
            return {
                "chapters": [],
                "count": 0
            }
            
    except Exception as e:
        return {
            "chapters": [],
            "count": 0,
            "error": str(e)
        }

@router.post("/resume/{item_id:path}")
async def get_resume_position(item_id: str):
    """Get the last watched position for resuming playback"""
    
    # This would integrate with the library API to get watch progress
    from .library import media_scanner
    
    if not media_scanner:
        return {"position": 0, "has_progress": False}
    
    library = media_scanner.get_library()
    
    # Find the item across all categories
    for category in ["movies", "tv_shows", "videos"]:
        if item_id in library.get(category, {}):
            item_data = library[category][item_id]
            progress = item_data.get("watch_progress", 0)
            last_watched = item_data.get("last_watched")
            
            return {
                "position": progress,
                "has_progress": progress > 5,  # Only resume if watched more than 5%
                "last_watched": last_watched,
                "resume_message": f"Resume from {int(progress)}%" if progress > 5 else None
            }
    
    return {"position": 0, "has_progress": False}
