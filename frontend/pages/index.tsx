import { useState, useEffect } from 'react'
import { ArrowLeft, Settings, Download, Share2 } from 'lucide-react'
import VideoPlayer from '../components/VideoPlayer'
import LibraryBrowser from '../components/LibraryBrowser'
import CaptionModeSelector from '../components/CaptionModeSelector'

interface MediaItem {
  id: string
  title: string
  filepath: string
  overview?: string
  poster_path?: string
  release_date?: string
  vote_average?: number
  subtitles: string[]
  watch_progress: number
  last_watched?: number
}

export default function Home() {  const [selectedMedia, setSelectedMedia] = useState<MediaItem | null>(null)
  const [selectedCaptionMode, setSelectedCaptionMode] = useState('original')
  const [showSettings, setShowSettings] = useState(false)
  const [isTransforming, setIsTransforming] = useState(false)

  const handleSelectMedia = (media: MediaItem) => {
    setSelectedMedia(media)
    setSelectedCaptionMode('original') // Reset to original when switching media
    setShowSettings(false) // Reset settings when changing media
  }

  const handleBackToLibrary = () => {
    setSelectedMedia(null)
    setShowSettings(false)
  }
    // Explicitly handle settings toggle
  const toggleSettings = () => {
    const newState = !showSettings;
    console.log("Toggling settings. Current state:", showSettings, "New state:", newState);
    setShowSettings(newState);
    
    // Force a DOM update if needed
    setTimeout(() => {
      console.log("Settings state after update:", newState);
    }, 100);
  }

  const handleCaptionModeChange = async (mode: string) => {
    if (mode === selectedCaptionMode) return
    
    setIsTransforming(true)
    setSelectedCaptionMode(mode)
    
    // If not original mode, pre-transform the captions
    if (mode !== 'original' && selectedMedia?.subtitles.length) {
      try {
        await fetch('/api/captions/transform', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            subtitle_path: selectedMedia.subtitles[0],
            mode: mode
          })
        })
      } catch (error) {
        console.error('Failed to transform captions:', error)
      }
    }
    
    setIsTransforming(false)
  }

  const handleProgressUpdate = async (progress: number) => {
    if (!selectedMedia) return
    
    try {
      await fetch(`/api/library/item/${encodeURIComponent(selectedMedia.filepath)}/progress`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ progress })
      })
    } catch (error) {
      console.error('Failed to update progress:', error)
    }
  }

  const exportSubtitles = async () => {
    if (!selectedMedia?.subtitles.length || selectedCaptionMode === 'original') return
    
    try {
      const response = await fetch('/api/captions/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subtitle_path: selectedMedia.subtitles[0],
          mode: selectedCaptionMode,
          output_format: 'srt'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        // You could show a success message or download link here
        console.log('Subtitles exported:', data.output_path)
      }
    } catch (error) {
      console.error('Failed to export subtitles:', error)
    }
  }

  if (selectedMedia) {
    return (
      <div className="min-h-screen bg-media-dark">
        {/* Header */}
        <div className="bg-media-gray border-b border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleBackToLibrary}
                className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Library</span>
              </button>
              
              <div className="text-white">
                <h1 className="text-xl font-semibold truncate max-w-md">
                  {selectedMedia.title}
                </h1>
                {selectedMedia.overview && (
                  <p className="text-sm text-gray-400 truncate max-w-lg">
                    {selectedMedia.overview}
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {selectedCaptionMode !== 'original' && (
                <button
                  onClick={exportSubtitles}
                  className="flex items-center space-x-2 px-3 py-2 bg-media-accent hover:bg-media-hover text-white rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span className="hidden sm:inline">Export</span>
                </button>
              )}
                <button
                onClick={toggleSettings}
                className={`p-2 rounded-lg transition-colors ${
                  showSettings ? 'bg-media-accent text-white' : 'text-gray-400 hover:text-white'
                }`}
                aria-label="Toggle Settings"
                title="Settings"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="flex h-[calc(100vh-73px)]">
          {/* Video Player */}
          <div className="flex-1 relative">
            <VideoPlayer
              mediaItem={selectedMedia}
              selectedCaptionMode={selectedCaptionMode}
              onProgress={handleProgressUpdate}
            />
            
            {/* Transformation Loading Overlay */}
            {isTransforming && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-10">
                <div className="bg-media-gray rounded-lg p-6 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-media-accent mx-auto mb-4"></div>
                  <p className="text-white">Transforming captions...</p>
                  <p className="text-gray-400 text-sm mt-1">This may take a moment</p>
                </div>
              </div>
            )}          </div>
          {/* Settings Sidebar */}
          {showSettings && (
            <div className="w-80 bg-media-gray border-l border-gray-700 p-6 overflow-y-auto z-50">
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-white mb-4">Settings</h2>
                <CaptionModeSelector
                  selectedMode={selectedCaptionMode}
                  onModeChange={handleCaptionModeChange}
                  disabled={!selectedMedia.subtitles.length}
                />
                
                {/* Media Info */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white">Media Info</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-400">File:</span>
                      <p className="text-white break-all">{selectedMedia.filepath.split('/').pop()}</p>
                    </div>
                    
                    {selectedMedia.release_date && (
                      <div>
                        <span className="text-gray-400">Release Date:</span>
                        <p className="text-white">{selectedMedia.release_date}</p>
                      </div>
                    )}
                    
                    {selectedMedia.vote_average && selectedMedia.vote_average > 0 && (
                      <div>
                        <span className="text-gray-400">Rating:</span>
                        <p className="text-white">{selectedMedia.vote_average}/10</p>
                      </div>
                    )}
                    
                    <div>
                      <span className="text-gray-400">Subtitles:</span>
                      <p className="text-white">
                        {selectedMedia.subtitles.length > 0 
                          ? `${selectedMedia.subtitles.length} available`
                          : 'None available'
                        }
                      </p>
                    </div>
                    
                    {selectedMedia.watch_progress > 0 && (
                      <div>
                        <span className="text-gray-400">Progress:</span>
                        <p className="text-white">{Math.round(selectedMedia.watch_progress)}%</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-white">Quick Actions</h3>
                  <div className="space-y-2">
                    <button className="w-full px-4 py-2 bg-media-gray border border-gray-600 hover:border-gray-500 text-white rounded-lg transition-colors text-left">
                      Mark as Watched
                    </button>
                    <button className="w-full px-4 py-2 bg-media-gray border border-gray-600 hover:border-gray-500 text-white rounded-lg transition-colors text-left">
                      Add to Favorites
                    </button>
                    <button 
                      onClick={exportSubtitles}
                      disabled={selectedCaptionMode === 'original' || !selectedMedia.subtitles.length}
                      className="w-full px-4 py-2 bg-media-gray border border-gray-600 hover:border-gray-500 text-white rounded-lg transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Export Current Captions
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-media-dark">
      {/* Header */}
      <div className="bg-media-gray border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">🎥 LLM Media Player</h1>
            <p className="text-gray-400 mt-1">AI-powered media center with intelligent captions</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="flex items-center space-x-2 px-4 py-2 bg-media-accent hover:bg-media-hover text-white rounded-lg transition-colors">
              <Share2 className="w-4 h-4" />
              <span>Share Library</span>
            </button>            
            <button 
              onClick={toggleSettings} 
              className="p-2 text-gray-400 hover:text-white transition-colors"
              aria-label="Toggle Settings"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex">
        <div className={`flex-1 p-6 ${showSettings ? 'pr-0' : ''}`}>
          <LibraryBrowser onSelectMedia={handleSelectMedia} />
        </div>
        
        {/* Library Settings Panel */}
        {showSettings && (
          <div className="w-80 bg-media-gray border-l border-gray-700 p-6 overflow-y-auto z-50 h-[calc(100vh-73px)]">
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-white mb-4">Settings</h2>
              
              {/* General Settings */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">General</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-white">Dark Mode</span>
                    <label className="relative inline-block w-12 h-6 rounded-full bg-gray-600">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <span className="absolute cursor-pointer inset-0.5 rounded-full bg-media-accent peer-checked:right-0.5 peer-checked:left-auto left-0.5 w-5 h-5 transition-all"></span>
                    </label>
                  </div>
                  
                  <div>
                    <label className="block text-white mb-1">Default Caption Mode</label>
                    <select className="w-full px-3 py-2 bg-media-gray border border-gray-600 rounded text-white">
                      <option value="original">Original</option>
                      <option value="weed">Chill/Stoner</option>
                      <option value="theo_von">Theo Von</option>
                      <option value="joey_diaz">Joey Diaz</option>
                    </select>
                  </div>
                </div>
              </div>
              
              {/* Library Settings */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Library</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-white mb-1">Default View</label>
                    <select className="w-full px-3 py-2 bg-media-gray border border-gray-600 rounded text-white">
                      <option value="grid">Grid</option>
                      <option value="list">List</option>
                    </select>
                  </div>
                  
                  <button className="w-full px-4 py-2 bg-media-gray border border-gray-600 hover:border-gray-500 text-white rounded-lg transition-colors text-left">
                    Scan Library Now
                  </button>
                </div>
              </div>
              
              {/* About */}
              <div className="pt-4 mt-6 border-t border-gray-700">
                <p className="text-gray-400 text-sm">LLM Media Player v1.0.0</p>
                <p className="text-gray-500 text-xs mt-1">Powered by AI-enhanced captions</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
