import os
import json
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import pysrt
import webvtt
import subprocess
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class SubtitleProcessor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')) if os.getenv('ANTHROPIC_API_KEY') else None
        self.cache_dir = Path(os.getenv('CAPTION_MODE_CACHE_DIR', './data/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Available caption modes
        self.caption_modes = {
            'weed': {
                'name': '🥦 Weed Mode',
                'description': 'Chill, slangy, stoner-friendly vibes',
                'prompt': """Transform this caption into a chill, stoner-friendly version. Use slang like "dude", "man", "totally", etc. Make it sound relaxed and casual. Keep the meaning but make it sound like someone high is describing what's happening. Be laid back and use simple words."""
            },
            'theo_von': {
                'name': '🎣 Theo Von Mode',
                'description': 'Southern metaphors and absurd storytelling',
                'prompt': """Rewrite this caption in Theo Von's style. Use bizarre Southern metaphors, weird personal anecdotes, and absurd comparisons. Make it funny but still convey the scene. Think Louisiana swamp stories mixed with random observations about life. Keep it entertaining and slightly nonsensical."""
            },
            'joey_diaz': {
                'name': '🥩 Joey Diaz Mode',
                'description': 'Explosive Bronx-style storytelling',
                'prompt': """Transform this caption into Joey Diaz's explosive storytelling style. Use phrases like "Listen to me", "Back in the day", add some energy and passion. Make it sound like Joey is describing the scene with his characteristic intensity and Brooklyn attitude. Keep it colorful but appropriate."""
            },
            'fact_check': {
                'name': '🧠 Fact-Check Mode',
                'description': 'Adds quick fact-checks to statements',
                'prompt': """For this caption, add brief fact-checks or clarifications in brackets after any claims that might be historically, scientifically, or factually questionable. If something is accurate, you can add [✓ Correct] or similar. Keep additions short and informative."""
            },
            'trivia': {
                'name': '🧾 Trivia Mode',
                'description': 'Sprinkles in fun facts about people/places/topics',
                'prompt': """Add interesting trivia or fun facts related to anything mentioned in this caption. Include brief tidbits in brackets like [Fun fact: ...] or [Did you know: ...]. Keep facts relevant and entertaining but don't overwhelm the original caption."""
            },
            'original': {
                'name': '📝 Original',
                'description': 'Unmodified original captions',
                'prompt': None
            }
        }
    
    def get_available_modes(self) -> Dict:
        """Get list of available caption transformation modes"""
        return self.caption_modes
    
    def extract_subtitles_from_video(self, video_path: str, output_path: str) -> bool:
        """Extract subtitles from video file using ffmpeg"""
        try:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-map', '0:s:0',  # First subtitle stream
                '-c:s', 'srt',    # Convert to SRT format
                output_path,
                '-y'              # Overwrite if exists
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            print(f"Error extracting subtitles: {e}")
            return False
    
    def parse_subtitle_file(self, subtitle_path: str) -> List[Dict]:
        """Parse subtitle file into structured data"""
        subtitle_path = Path(subtitle_path)
        
        if subtitle_path.suffix.lower() == '.srt':
            return self._parse_srt(subtitle_path)
        elif subtitle_path.suffix.lower() == '.vtt':
            return self._parse_vtt(subtitle_path)
        else:
            raise ValueError(f"Unsupported subtitle format: {subtitle_path.suffix}")
    
    def _parse_srt(self, srt_path: Path) -> List[Dict]:
        """Parse SRT subtitle file"""
        subtitles = pysrt.open(str(srt_path))
        parsed = []
        
        for sub in subtitles:
            parsed.append({
                'index': sub.index,
                'start_time': self._time_to_seconds(sub.start),
                'end_time': self._time_to_seconds(sub.end),
                'text': sub.text.replace('\n', ' ').strip(),
                'original_text': sub.text.replace('\n', ' ').strip()
            })
        
        return parsed
    
    def _parse_vtt(self, vtt_path: Path) -> List[Dict]:
        """Parse VTT subtitle file"""
        vtt = webvtt.read(str(vtt_path))
        parsed = []
        
        for i, caption in enumerate(vtt):
            parsed.append({
                'index': i + 1,
                'start_time': self._vtt_time_to_seconds(caption.start),
                'end_time': self._vtt_time_to_seconds(caption.end),
                'text': caption.text.replace('\n', ' ').strip(),
                'original_text': caption.text.replace('\n', ' ').strip()
            })
        
        return parsed
    
    def _time_to_seconds(self, time_obj) -> float:
        """Convert pysrt time object to seconds"""
        return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000
    
    def _vtt_time_to_seconds(self, time_str: str) -> float:
        """Convert VTT time string to seconds"""
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        elif len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
        else:
            return float(parts[0])
    
    def _get_cache_key(self, subtitle_path: str, mode: str) -> str:
        """Generate cache key for transformed subtitles"""
        content = f"{subtitle_path}{mode}{os.path.getmtime(subtitle_path)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    async def transform_caption_text(self, text: str, mode: str) -> str:
        """Transform a single caption using the specified mode"""
        if mode == 'original' or mode not in self.caption_modes:
            return text
        
        prompt = self.caption_modes[mode]['prompt']
        if not prompt:
            return text
        
        try:
            # Try OpenAI first
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            
            # Fallback to Anthropic
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=200,
                    messages=[
                        {"role": "user", "content": f"{prompt}\n\nOriginal caption: {text}"}
                    ]
                )
                return response.content[0].text.strip()
            
            else:
                print("No LLM API keys configured")
                return text
                
        except Exception as e:
            print(f"Error transforming caption: {e}")
            return text
    
    async def transform_subtitles(self, subtitle_path: str, mode: str, batch_size: int = 5) -> Dict:
        """Transform entire subtitle file using specified mode"""
        cache_key = self._get_cache_key(subtitle_path, mode)
        cache_path = self._get_cache_path(cache_key)
        
        # Check cache first
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_result = json.load(f)
                    print(f"📋 Using cached transformation for {mode} mode")
                    return cached_result
            except Exception as e:
                print(f"Error reading cache: {e}")
        
        # Parse original subtitles
        try:
            subtitles = self.parse_subtitle_file(subtitle_path)
        except Exception as e:
            return {"error": f"Failed to parse subtitle file: {e}"}
        
        if mode == 'original':
            result = {
                "mode": mode,
                "subtitle_path": subtitle_path,
                "subtitles": subtitles,
                "cache_key": cache_key
            }
        else:
            # Transform subtitles in batches
            print(f"🎭 Transforming {len(subtitles)} captions to {mode} mode...")
            
            transformed_subtitles = []
            for i in range(0, len(subtitles), batch_size):
                batch = subtitles[i:i + batch_size]
                
                # Transform batch
                tasks = []
                for subtitle in batch:
                    task = self.transform_caption_text(subtitle['text'], mode)
                    tasks.append(task)
                
                # Wait for batch to complete
                transformed_texts = await asyncio.gather(*tasks)
                
                # Update subtitles with transformed text
                for subtitle, transformed_text in zip(batch, transformed_texts):
                    subtitle_copy = subtitle.copy()
                    subtitle_copy['text'] = transformed_text
                    transformed_subtitles.append(subtitle_copy)
                
                print(f"✅ Processed batch {i//batch_size + 1}/{(len(subtitles) + batch_size - 1)//batch_size}")
            
            result = {
                "mode": mode,
                "subtitle_path": subtitle_path,
                "subtitles": transformed_subtitles,
                "cache_key": cache_key
            }
        
        # Cache the result
        try:
            with open(cache_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"💾 Cached transformation result")
        except Exception as e:
            print(f"Error caching result: {e}")
        
        return result
    
    def export_subtitles(self, subtitles_data: Dict, output_path: str, format: str = 'srt') -> bool:
        """Export transformed subtitles to file"""
        try:
            subtitles = subtitles_data['subtitles']
            
            if format.lower() == 'srt':
                return self._export_srt(subtitles, output_path)
            elif format.lower() == 'vtt':
                return self._export_vtt(subtitles, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            print(f"Error exporting subtitles: {e}")
            return False
    
    def _export_srt(self, subtitles: List[Dict], output_path: str) -> bool:
        """Export subtitles as SRT format"""
        try:
            srt_content = []
            
            for sub in subtitles:
                start_time = self._seconds_to_srt_time(sub['start_time'])
                end_time = self._seconds_to_srt_time(sub['end_time'])
                
                srt_content.append(f"{sub['index']}")
                srt_content.append(f"{start_time} --> {end_time}")
                srt_content.append(sub['text'])
                srt_content.append("")  # Blank line between subtitles
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(srt_content))
            
            return True
            
        except Exception as e:
            print(f"Error exporting SRT: {e}")
            return False
    
    def _export_vtt(self, subtitles: List[Dict], output_path: str) -> bool:
        """Export subtitles as VTT format"""
        try:
            vtt_content = ["WEBVTT", ""]
            
            for sub in subtitles:
                start_time = self._seconds_to_vtt_time(sub['start_time'])
                end_time = self._seconds_to_vtt_time(sub['end_time'])
                
                vtt_content.append(f"{start_time} --> {end_time}")
                vtt_content.append(sub['text'])
                vtt_content.append("")  # Blank line between subtitles
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(vtt_content))
            
            return True
            
        except Exception as e:
            print(f"Error exporting VTT: {e}")
            return False
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convert seconds to VTT time format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    
    def get_subtitle_info(self, subtitle_path: str) -> Dict:
        """Get information about a subtitle file"""
        try:
            subtitles = self.parse_subtitle_file(subtitle_path)
            
            return {
                "path": subtitle_path,
                "format": Path(subtitle_path).suffix.lower(),
                "count": len(subtitles),
                "duration": subtitles[-1]['end_time'] if subtitles else 0,
                "languages": ["en"],  # Could be enhanced to detect language
                "available_modes": list(self.caption_modes.keys())
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze subtitle file: {e}"}
