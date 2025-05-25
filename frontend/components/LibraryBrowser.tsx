import { useState, useEffect } from 'react'
import { Search, Filter, Grid, List } from 'lucide-react'
import MediaCard from './MediaCard'

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

interface LibraryBrowserProps {
  onSelectMedia: (item: MediaItem) => void
}

export default function LibraryBrowser({ onSelectMedia }: LibraryBrowserProps) {
  const [movies, setMovies] = useState<MediaItem[]>([])
  const [tvShows, setTvShows] = useState<any[]>([])
  const [videos, setVideos] = useState<MediaItem[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'movies' | 'tv' | 'videos'>('movies')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadLibrary()
  }, [])

  const loadLibrary = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load movies
      const moviesResponse = await fetch('/api/library/movies')
      if (moviesResponse.ok) {
        const moviesData = await moviesResponse.json()
        setMovies(moviesData.movies)
      }

      // Load TV shows
      const tvResponse = await fetch('/api/library/tv-shows')
      if (tvResponse.ok) {
        const tvData = await tvResponse.json()
        setTvShows(tvData.tv_shows)
      }

      // Load general videos
      const videosResponse = await fetch('/api/library/')
      if (videosResponse.ok) {
        const libraryData = await videosResponse.json()
        const videoItems = Object.values(libraryData.library.videos || {}) as MediaItem[]
        setVideos(videoItems)
      }

    } catch (err) {
      setError('Failed to load media library')
      console.error('Library loading error:', err)
    } finally {
      setLoading(false)
    }
  }

  const searchMedia = async () => {
    if (!searchQuery.trim()) {
      loadLibrary()
      return
    }

    try {
      const response = await fetch(`/api/library/search?q=${encodeURIComponent(searchQuery)}`)
      if (response.ok) {
        const data = await response.json()
        
        // Categorize search results
        const searchMovies = data.results.filter((item: any) => item.content_type === 'movie')
        const searchTvShows = data.results.filter((item: any) => item.content_type === 'tv_show')
        const searchVideos = data.results.filter((item: any) => item.content_type === 'video')
        
        setMovies(searchMovies)
        setTvShows(searchTvShows)
        setVideos(searchVideos)
      }
    } catch (err) {
      console.error('Search error:', err)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      searchMedia()
    }
  }

  const getCurrentItems = () => {
    switch (activeTab) {
      case 'movies':
        return movies
      case 'tv':
        // Flatten TV show episodes for display
        return tvShows.flatMap(show => 
          show.episodes.map((episode: any) => ({
            ...episode,
            title: `${show.show_name} - S${episode.season}E${episode.episode}`,
            show_name: show.show_name,
            poster_path: show.metadata?.poster_path
          }))
        )
      case 'videos':
        return videos
      default:
        return []
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-media-accent"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <p className="text-red-400 mb-4">{error}</p>
        <button 
          onClick={loadLibrary}
          className="px-4 py-2 bg-media-accent text-white rounded-lg hover:bg-media-hover transition-colors"
        >
          Retry
        </button>
      </div>
    )
  }

  const currentItems = getCurrentItems()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h1 className="text-3xl font-bold">Media Library</h1>
        
        {/* Search and Controls */}
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search movies, shows, videos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="pl-10 pr-4 py-2 bg-media-gray border border-gray-600 rounded-lg focus:border-media-accent focus:outline-none w-64"
            />
          </div>
          
          <button
            onClick={searchMedia}
            className="px-4 py-2 bg-media-accent text-white rounded-lg hover:bg-media-hover transition-colors"
          >
            Search
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'grid' ? 'bg-media-accent text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'list' ? 'bg-media-accent text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 bg-media-gray rounded-lg p-1">
        {[
          { key: 'movies', label: 'Movies', count: movies.length },
          { key: 'tv', label: 'TV Shows', count: tvShows.length },
          { key: 'videos', label: 'Videos', count: videos.length },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`flex-1 px-4 py-2 rounded-md transition-colors ${
              activeTab === tab.key
                ? 'bg-media-accent text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      {/* Content Grid/List */}
      {currentItems.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">No media found</p>
          <p className="text-gray-500 text-sm mt-2">
            {searchQuery ? 'Try a different search term' : 'Add some media files to get started'}
          </p>
        </div>
      ) : (
        <div className={
          viewMode === 'grid'
            ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6'
            : 'space-y-4'
        }>
          {currentItems.map((item) => (
            <MediaCard
              key={item.id}
              item={item}
              viewMode={viewMode}
              onClick={() => onSelectMedia(item)}
            />
          ))}
        </div>
      )}

      {/* Stats Footer */}
      <div className="flex justify-center pt-8 text-sm text-gray-400">
        Total: {movies.length} movies, {tvShows.length} TV shows, {videos.length} videos
      </div>
    </div>
  )
}
