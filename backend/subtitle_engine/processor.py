import os
import json
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import pysrt
import webvtt
import subprocess
import ollama
from dotenv import load_dotenv
from caption_modes.modes import CaptionModes

load_dotenv()

class SubtitleProcessor:
    def __init__(self):
        # Initialize Ollama client
        self.ollama_client = ollama.Client(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        self.current_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        # Test Ollama connection
        try:
            models = self.get_available_models()
            if models:
                print(f"🦙 Connected to Ollama with {len(models)} models available")
                if self.current_model not in [m['name'] for m in models]:
                    print(f"⚠️ Model '{self.current_model}' not found. Available models: {[m['name'] for m in models]}")
                    if models:
                        self.current_model = models[0]['name']
                        print(f"🔄 Switched to available model: {self.current_model}")
            else:
                print("⚠️ No Ollama models found. Please pull a model first with: ollama pull llama3.2")
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
        self.cache_dir = Path(os.getenv('CAPTION_MODE_CACHE_DIR', './data/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load caption modes from our consolidated modes file
        self.caption_modes = CaptionModes.get_all_modes()
        self.quick_transforms = CaptionModes.get_quick_transforms()
    
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
            # Use Ollama for caption transformation
            full_prompt = f"{prompt}\n\nOriginal caption: {text}\n\nTransformed caption:"
            
            response = self.ollama_client.generate(
                model=self.current_model,
                prompt=full_prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 200,
                    'stop': ['\n\n', 'Original caption:', 'Transformed caption:']
                }
            )
            
            transformed_text = response['response'].strip()
            return transformed_text if transformed_text else text
                
        except Exception as e:
            print(f"Error transforming caption with Ollama: {e}")
            # Fallback to quick transform if available
            if mode in self.quick_transforms:
                print(f"🔄 Using quick transform fallback for {mode} mode")
                return self.quick_transforms[mode](text)
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
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available Ollama models"""
        try:
            models = self.ollama_client.list()
            return models.get('models', [])
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
            return []
    
    def set_current_model(self, model_name: str) -> bool:
        """Set the current model for caption transformation"""
        try:
            available_models = [m['name'] for m in self.get_available_models()]
            if model_name in available_models:
                self.current_model = model_name
                print(f"🔄 Switched to model: {model_name}")
                return True
            else:
                print(f"❌ Model '{model_name}' not available. Available models: {available_models}")
                return False
        except Exception as e:
            print(f"Error setting model: {e}")
            return False
    
    def get_current_model(self) -> str:
        """Get the currently selected model"""
        return self.current_model
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a new model from Ollama registry"""
        try:
            print(f"📥 Pulling model: {model_name}...")
            self.ollama_client.pull(model_name)
            print(f"✅ Successfully pulled model: {model_name}")
            return True
        except Exception as e:
            print(f"❌ Error pulling model {model_name}: {e}")
            return False
