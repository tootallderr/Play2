import os
import json
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tmdbsimple as tmdb
from dotenv import load_dotenv

load_dotenv()
tmdb.API_KEY = os.getenv('TMDB_API_KEY')

class MediaFileHandler(FileSystemEventHandler):
    def __init__(self, scanner):
        self.scanner = scanner
        self.video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.m4v', '.wmv', '.flv', '.webm'}
        
    def on_created(self, event):
        if not event.is_directory and Path(event.src_path).suffix.lower() in self.video_extensions:
            asyncio.create_task(self.scanner.process_new_file(event.src_path))
    
    def on_deleted(self, event):
        if not event.is_directory:
            asyncio.create_task(self.scanner.remove_file(event.src_path))

class MediaScanner:
    def __init__(self, watched_directories: List[str]):
        self.watched_dirs = [d.strip() for d in watched_directories if d.strip()]
        self.observer = Observer()
        self.library_file = "data/media_library.json"
        self.library_data = self.load_library()
        
    def load_library(self) -> Dict:
        """Load existing library data"""
        try:
            if os.path.exists(self.library_file):
                with open(self.library_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading library: {e}")
        
        return {
            "movies": {},
            "tv_shows": {},
            "videos": {},
            "last_scan": None
        }
    
    def save_library(self):
        """Save library data to disk"""
        os.makedirs(os.path.dirname(self.library_file), exist_ok=True)
        with open(self.library_file, 'w') as f:
            json.dump(self.library_data, f, indent=2)
    
    def get_file_hash(self, filepath: str) -> str:
        """Generate hash for file to detect changes"""
        stat = os.stat(filepath)
        return hashlib.md5(f"{filepath}{stat.st_size}{stat.st_mtime}".encode()).hexdigest()
    
    def detect_content_type(self, filepath: str) -> tuple:
        """Detect if file is movie, TV show, or general video"""
        path = Path(filepath)
        parent_dirs = [p.name.lower() for p in path.parents]
        filename = path.stem.lower()
        
        # TV Show patterns
        tv_patterns = ['season', 'episode', 's0', 'e0', 'x0']
        if any(pattern in filename for pattern in tv_patterns) or 'tv' in parent_dirs:
            return 'tv_show', self.extract_tv_info(filepath)
        
        # Movie patterns (in movies folder or typical movie naming)
        if 'movies' in parent_dirs or len(filename.split()) > 1:
            return 'movie', self.extract_movie_info(filepath)
        
        return 'video', {'title': path.stem}
    
    def extract_tv_info(self, filepath: str) -> Dict:
        """Extract TV show information from filename"""
        path = Path(filepath)
        filename = path.stem
        
        # Basic pattern matching for TV shows
        import re
        
        # Pattern: Show.Name.S01E01 or Show.Name.1x01
        season_episode = re.search(r'[Ss](\d+)[Ee](\d+)', filename)
        if not season_episode:
            season_episode = re.search(r'(\d+)x(\d+)', filename)
        
        if season_episode:
            season = int(season_episode.group(1))
            episode = int(season_episode.group(2))
            show_name = re.split(r'[Ss]\d+[Ee]\d+|\d+x\d+', filename)[0].replace('.', ' ').strip()
        else:
            season, episode = 1, 1
            show_name = filename.replace('.', ' ')
        
        return {
            'show_name': show_name,
            'season': season,
            'episode': episode,
            'title': filename
        }
    
    def extract_movie_info(self, filepath: str) -> Dict:
        """Extract movie information from filename"""
        path = Path(filepath)
        filename = path.stem
        
        # Remove common movie filename artifacts
        import re
        clean_title = re.sub(r'\(?\d{4}\)?', '', filename)  # Remove year
        clean_title = re.sub(r'\[.*?\]', '', clean_title)   # Remove brackets
        clean_title = clean_title.replace('.', ' ').strip()
        
        return {
            'title': clean_title,
            'filename': filename
        }
    
    async def fetch_tmdb_metadata(self, title: str, content_type: str) -> Dict:
        """Fetch metadata from TMDB"""
        try:
            if content_type == 'movie':
                search = tmdb.Search()
                response = search.movie(query=title)
                if response['results']:
                    movie_data = response['results'][0]
                    return {
                        'tmdb_id': movie_data['id'],
                        'title': movie_data['title'],
                        'overview': movie_data.get('overview', ''),
                        'release_date': movie_data.get('release_date', ''),
                        'poster_path': movie_data.get('poster_path', ''),
                        'backdrop_path': movie_data.get('backdrop_path', ''),
                        'vote_average': movie_data.get('vote_average', 0)
                    }
            elif content_type == 'tv_show':
                search = tmdb.Search()
                response = search.tv(query=title)
                if response['results']:
                    tv_data = response['results'][0]
                    return {
                        'tmdb_id': tv_data['id'],
                        'name': tv_data['name'],
                        'overview': tv_data.get('overview', ''),
                        'first_air_date': tv_data.get('first_air_date', ''),
                        'poster_path': tv_data.get('poster_path', ''),
                        'backdrop_path': tv_data.get('backdrop_path', ''),
                        'vote_average': tv_data.get('vote_average', 0)
                    }
        except Exception as e:
            print(f"Error fetching TMDB data for '{title}': {e}")
        
        return {}
    
    def find_subtitles(self, video_path: str) -> List[str]:
        """Find subtitle files for a video"""
        video_file = Path(video_path)
        subtitle_extensions = ['.srt', '.vtt', '.ass', '.ssa']
        subtitles = []
        
        # Look for subtitle files with same name
        for ext in subtitle_extensions:
            subtitle_path = video_file.with_suffix(ext)
            if subtitle_path.exists():
                subtitles.append(str(subtitle_path))
        
        # Look for subtitle files in same directory
        for subtitle_file in video_file.parent.glob(f"{video_file.stem}*"):
            if subtitle_file.suffix.lower() in subtitle_extensions:
                subtitles.append(str(subtitle_file))
        
        return subtitles
    
    async def process_new_file(self, filepath: str):
        """Process a newly discovered media file"""
        try:
            print(f"📁 Processing new file: {filepath}")
            
            # Get file info
            file_hash = self.get_file_hash(filepath)
            content_type, basic_info = self.detect_content_type(filepath)
            
            # Skip if already processed and unchanged
            if filepath in self.library_data.get(f"{content_type}s", {}) and \
               self.library_data[f"{content_type}s"][filepath].get('file_hash') == file_hash:
                return
            
            # Find subtitles
            subtitles = self.find_subtitles(filepath)
            
            # Fetch metadata
            search_title = basic_info.get('show_name', basic_info.get('title', ''))
            metadata = await self.fetch_tmdb_metadata(search_title, content_type)
            
            # Create media entry
            media_entry = {
                'filepath': filepath,
                'file_hash': file_hash,
                'content_type': content_type,
                'subtitles': subtitles,
                'metadata': metadata,
                'basic_info': basic_info,
                'added_date': asyncio.get_event_loop().time(),
                'watch_progress': 0,
                'last_watched': None
            }
            
            # Store in library
            category = f"{content_type}s"
            if category not in self.library_data:
                self.library_data[category] = {}
            
            self.library_data[category][filepath] = media_entry
            self.save_library()
            
            print(f"✅ Added {content_type}: {search_title}")
            
        except Exception as e:
            print(f"❌ Error processing file {filepath}: {e}")
    
    async def remove_file(self, filepath: str):
        """Remove deleted file from library"""
        for category in ['movies', 'tv_shows', 'videos']:
            if filepath in self.library_data[category]:
                del self.library_data[category][filepath]
                self.save_library()
                print(f"🗑️ Removed from library: {filepath}")
                break
    
    async def initial_scan(self):
        """Perform initial scan of all watched directories"""
        print("🔍 Starting initial media library scan...")
        
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.m4v', '.wmv', '.flv', '.webm'}
        
        for watch_dir in self.watched_dirs:
            if not os.path.exists(watch_dir):
                print(f"⚠️ Directory not found: {watch_dir}")
                continue
                
            print(f"📂 Scanning directory: {watch_dir}")
            
            for root, dirs, files in os.walk(watch_dir):
                for file in files:
                    if Path(file).suffix.lower() in video_extensions:
                        filepath = os.path.join(root, file)
                        await self.process_new_file(filepath)
        
        self.library_data['last_scan'] = asyncio.get_event_loop().time()
        self.save_library()
        print("✅ Initial scan completed!")
    
    async def start_monitoring(self):
        """Start monitoring watched directories"""
        # Perform initial scan
        await self.initial_scan()
        
        # Set up file system monitoring
        event_handler = MediaFileHandler(self)
        
        for watch_dir in self.watched_dirs:
            if os.path.exists(watch_dir):
                self.observer.schedule(event_handler, watch_dir, recursive=True)
                print(f"👀 Monitoring directory: {watch_dir}")
        
        self.observer.start()
        print("🎬 Media scanner active!")
    
    async def stop_monitoring(self):
        """Stop monitoring directories"""
        self.observer.stop()
        self.observer.join()
        print("🛑 Media scanner stopped")
    
    def get_library(self) -> Dict:
        """Get current library data"""
        return self.library_data
    
    def search_library(self, query: str) -> List[Dict]:
        """Search library for matching content"""
        results = []
        query_lower = query.lower()
        
        for category in ['movies', 'tv_shows', 'videos']:
            for filepath, media_item in self.library_data[category].items():
                # Search in title, show name, and metadata
                searchable_text = []
                
                if 'basic_info' in media_item:
                    searchable_text.append(media_item['basic_info'].get('title', ''))
                    searchable_text.append(media_item['basic_info'].get('show_name', ''))
                
                if 'metadata' in media_item:
                    searchable_text.append(media_item['metadata'].get('title', ''))
                    searchable_text.append(media_item['metadata'].get('name', ''))
                    searchable_text.append(media_item['metadata'].get('overview', ''))
                
                if any(query_lower in text.lower() for text in searchable_text if text):
                    results.append(media_item)
        
        return results
