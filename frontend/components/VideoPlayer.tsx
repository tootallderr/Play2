import { useState, useEffect } from 'react'
import { Play, Pause, Volume2, VolumeX, Settings, Maximize } from 'lucide-react'

interface MediaItem {
  id: string
  title: string
  filepath: string
  subtitles: string[]
  watch_progress: number
}

interface VideoPlayerProps {
  mediaItem: MediaItem
  onProgress?: (progress: number) => void
  selectedCaptionMode?: string
}

export default function VideoPlayer({ mediaItem, onProgress, selectedCaptionMode = 'original' }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [showControls, setShowControls] = useState(true)
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null)
  const [subtitleTrack, setSubtitleTrack] = useState<string | null>(null)

  useEffect(() => {
    let hideControlsTimer: NodeJS.Timeout

    const showControlsTemporarily = () => {
      setShowControls(true)
      clearTimeout(hideControlsTimer)
      hideControlsTimer = setTimeout(() => setShowControls(false), 3000)
    }

    const handleMouseMove = () => showControlsTemporarily()
    const handleKeyPress = (e: KeyboardEvent) => {
      switch (e.key) {
        case ' ':
          e.preventDefault()
          togglePlayPause()
          break
        case 'ArrowLeft':
          e.preventDefault()
          seekBy(-10)
          break
        case 'ArrowRight':
          e.preventDefault()
          seekBy(10)
          break
        case 'f':
          toggleFullscreen()
          break
        case 'm':
          toggleMute()
          break
      }
      showControlsTemporarily()
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('keydown', handleKeyPress)

    return () => {
      clearTimeout(hideControlsTimer)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('keydown', handleKeyPress)
    }
  }, [isPlaying])

  useEffect(() => {
    // Load subtitle track when caption mode changes
    if (mediaItem.subtitles.length > 0 && selectedCaptionMode !== 'original') {
      loadTransformedSubtitles()
    }
  }, [selectedCaptionMode, mediaItem])

  const loadTransformedSubtitles = async () => {
    try {
      const response = await fetch('/api/captions/transform', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subtitle_path: mediaItem.subtitles[0],
          mode: selectedCaptionMode
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        const subtitleUrl = `/api/captions/stream/${result.result.cache_key}?format=vtt`
        setSubtitleTrack(subtitleUrl)
      }
    } catch (error) {
      console.error('Failed to load transformed subtitles:', error)
    }
  }

  const togglePlayPause = () => {
    if (videoElement) {
      if (isPlaying) {
        videoElement.pause()
      } else {
        videoElement.play()
      }
    }
  }

  const seekBy = (seconds: number) => {
    if (videoElement) {
      videoElement.currentTime = Math.max(0, Math.min(duration, videoElement.currentTime + seconds))
    }
  }

  const seekTo = (time: number) => {
    if (videoElement) {
      videoElement.currentTime = time
    }
  }

  const toggleMute = () => {
    if (videoElement) {
      videoElement.muted = !videoElement.muted
      setIsMuted(videoElement.muted)
    }
  }

  const toggleFullscreen = () => {
    if (videoElement) {
      if (document.fullscreenElement) {
        document.exitFullscreen()
      } else {
        videoElement.requestFullscreen()
      }
    }
  }

  const handleVideoRef = (video: HTMLVideoElement) => {
    setVideoElement(video)
    
    video.addEventListener('loadedmetadata', () => {
      setDuration(video.duration)
      // Resume from last position
      if (mediaItem.watch_progress > 0) {
        video.currentTime = (mediaItem.watch_progress / 100) * video.duration
      }
    })

    video.addEventListener('timeupdate', () => {
      setCurrentTime(video.currentTime)
      const progress = (video.currentTime / video.duration) * 100
      onProgress?.(progress)
    })

    video.addEventListener('play', () => setIsPlaying(true))
    video.addEventListener('pause', () => setIsPlaying(false))
    video.addEventListener('volumechange', () => {
      setVolume(video.volume)
      setIsMuted(video.muted)
    })
  }

  const formatTime = (time: number) => {
    const hours = Math.floor(time / 3600)
    const minutes = Math.floor((time % 3600) / 60)
    const seconds = Math.floor(time % 60)
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    }
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <div className="relative w-full h-full bg-black group">
      <video
        ref={handleVideoRef}
        className="w-full h-full object-contain"
        src={`/api/player/stream/${encodeURIComponent(mediaItem.filepath)}`}
        onClick={togglePlayPause}
        crossOrigin="anonymous"
      >
        {subtitleTrack && (
          <track
            kind="subtitles"
            src={subtitleTrack}
            srcLang="en"
            label="Transformed Captions"
            default
          />
        )}
        {mediaItem.subtitles.length > 0 && selectedCaptionMode === 'original' && (
          <track
            kind="subtitles"
            src={`/media/${mediaItem.subtitles[0]}`}
            srcLang="en"
            label="Original"
            default
          />
        )}
      </video>

      {/* Play/Pause Overlay */}
      <div 
        className={`absolute inset-0 flex items-center justify-center transition-opacity duration-300 ${
          showControls ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={togglePlayPause}
      >
        <button className="bg-black/50 hover:bg-black/70 rounded-full p-4 transition-all duration-200">
          {isPlaying ? (
            <Pause className="w-12 h-12 text-white" />
          ) : (
            <Play className="w-12 h-12 text-white ml-1" />
          )}
        </button>
      </div>

      {/* Controls Bar */}
      <div 
        className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 transition-opacity duration-300 ${
          showControls ? 'opacity-100' : 'opacity-0'
        }`}
      >
        {/* Progress Bar */}
        <div className="mb-4">
          <div 
            className="w-full h-2 bg-gray-600 rounded-full cursor-pointer"
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect()
              const pos = (e.clientX - rect.left) / rect.width
              seekTo(pos * duration)
            }}
          >
            <div 
              className="h-full bg-media-accent rounded-full transition-all duration-100"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={togglePlayPause}
              className="hover:text-media-accent transition-colors"
            >
              {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
            </button>

            <div className="flex items-center space-x-2">
              <button
                onClick={toggleMute}
                className="hover:text-media-accent transition-colors"
              >
                {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={(e) => {
                  const newVolume = parseFloat(e.target.value)
                  if (videoElement) {
                    videoElement.volume = newVolume
                    videoElement.muted = newVolume === 0
                  }
                }}
                className="w-20 accent-media-accent"
              />
            </div>

            <div className="text-sm">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button className="hover:text-media-accent transition-colors">
              <Settings className="w-5 h-5" />
            </button>
            <button
              onClick={toggleFullscreen}
              className="hover:text-media-accent transition-colors"
            >
              <Maximize className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Caption Mode Indicator */}
      {selectedCaptionMode !== 'original' && (
        <div className="absolute top-4 right-4">
          <div className={`mode-badge ${selectedCaptionMode}`}>
            {selectedCaptionMode.replace('_', ' ').toUpperCase()}
          </div>
        </div>
      )}
    </div>
  )
}
