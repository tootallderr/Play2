from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from pathlib import Path
import os
import asyncio

router = APIRouter()

# This will be injected from main.py
media_scanner = None

def set_media_scanner(scanner):
    global media_scanner
    media_scanner = scanner

@router.get("/")
async def get_library():
    """Get the complete media library"""
    if not media_scanner:
        raise HTTPException(status_code=500, detail="Media scanner not initialized")
    
    library = media_scanner.get_library()
    
    # Add statistics
    stats = {
        "total_movies": len(library.get("movies", {})),
        "total_tv_shows": len(library.get("tv_shows", {})),
        "total_videos": len(library.get("videos", {})),
        "last_scan": library.get("last_scan")
    }
    
    return {
        "library": library,
        "statistics": stats
    }

@router.get("/search")
async def search_library(q: str = Query(..., description="Search query")):
    """Search the media library"""
    if not media_scanner:
        raise HTTPException(status_code=500, detail="Media scanner not initialized")
    
    results = media_scanner.search_library(q)
    
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }

@router.get("/movies")
async def get_movies():
    """Get all movies in the library"""
    if not media_scanner:
        raise HTTPException(status_code=500, detail="Media scanner not initialized")
    
    library = media_scanner.get_library()
    movies = library.get("movies", {})
    
    # Convert to list format with additional info
    movie_list = []
    for filepath, movie_data in movies.items():
        movie_info = {
            "id": filepath,
            "filepath": filepath,
            "title": movie_data.get("metadata", {}).get("title", 
                     movie_data.get("basic_info", {}).get("title", "Unknown")),
            "overview": movie_data.get("metadata", {}).get("overview", ""),
            "release_date": movie_data.get("metadata", {}).get("release_date", ""),
            "poster_path": movie_data.get("metadata", {}).get("poster_path", ""),
            "vote_average": movie_data.get("metadata", {}).get("vote_average", 0),
            "subtitles": movie_data.get("subtitles", []),
            "watch_progress": movie_data.get("watch_progress", 0),
            "last_watched": movie_data.get("last_watched")
        }
        movie_list.append(movie_info)
    
    return {
        "movies": movie_list,
        "count": len(movie_list)
    }

@router.get("/tv-shows")
async def get_tv_shows():
    """Get all TV shows in the library"""
    if not media_scanner:
        raise HTTPException(status_code=500, detail="Media scanner not initialized")
    
    library = media_scanner.get_library()
    tv_shows = library.get("tv_shows", {})
    
    # Group by show name
    shows_grouped = {}
    for filepath, show_data in tv_shows.items():
        show_name = show_data.get("basic_info", {}).get("show_name", "Unknown Show")
        
        if show_name not in shows_grouped:
            shows_grouped[show_name] = {
                "show_name": show_name,
                "episodes": [],
                "metadata": show_data.get("metadata", {}),
                "seasons": set()
            }
        
        episode_info = {
            "id": filepath,
            "filepath": filepath,
            "season": show_data.get("basic_info", {}).get("season", 1),
            "episode": show_data.get("basic_info", {}).get("episode", 1),
            "title": show_data.get("basic_info", {}).get("title", ""),
            "subtitles": show_data.get("subtitles", []),
            "watch_progress": show_data.get("watch_progress", 0),
            "last_watched": show_data.get("last_watched")
        }
        
        shows_grouped[show_name]["episodes"].append(episode_info)
        shows_grouped[show_name]["seasons"].add(episode_info["season"])
    
    # Convert seasons set to sorted list
    for show in shows_grouped.values():
        show["seasons"] = sorted(list(show["seasons"]))
        show["episodes"] = sorted(show["episodes"], key=lambda x: (x["season"], x["episode"]))
    
    return {
        "tv_shows": list(shows_grouped.values()),
        "count": len(shows_grouped)
    }

@router.get("/item/{item_id:path}")
async def get_media_item(item_id: str):
    """Get detailed information about a specific media item"""
    if not media_scanner:
        raise HTTPException(status_code=500, detail="Media scanner not initialized")
    
    library = media_scanner.get_library()
    
    # Search across all categories
    for category in ["movies", "tv_shows", "videos"]:
        if item_id in library.get(category, {}):
            item_data = library[category][item_id]
            
            # Check if file still exists
            if not os.path.exists(item_id):
                raise HTTPException(status_code=404, detail="Media file not found on disk")
            
            return {
                "item": item_data,
                "category": category,
                "file_exists": True
            }
    
    raise HTTPException(status_code=404, detail="Media item not found")

@router.post("/rescan")
async def trigger_rescan():
    """Trigger a manual rescan of the media library"""
    if not media_scanner:
        raise HTTPException(status_code=500, detail="Media scanner not initialized")
    
    try:
        await media_scanner.initial_scan()
        return {"message": "Library rescan completed", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rescan failed: {str(e)}")

@router.put("/item/{item_id:path}/progress")
async def update_watch_progress(item_id: str, progress: float):
    """Update watch progress for a media item"""
    if not media_scanner:
        raise HTTPException(status_code=500, detail="Media scanner not initialized")
    
    library = media_scanner.get_library()
    
    # Find and update the item
    for category in ["movies", "tv_shows", "videos"]:
        if item_id in library.get(category, {}):
            library[category][item_id]["watch_progress"] = max(0, min(100, progress))
            library[category][item_id]["last_watched"] = asyncio.get_event_loop().time()
            media_scanner.save_library()
            
            return {
                "message": "Progress updated",
                "item_id": item_id,
                "progress": progress
            }
    
    raise HTTPException(status_code=404, detail="Media item not found")
