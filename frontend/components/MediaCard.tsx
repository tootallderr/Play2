import { Play, Clock, Star } from 'lucide-react'

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
  show_name?: string
}

interface MediaCardProps {
  item: MediaItem
  viewMode: 'grid' | 'list'
  onClick: () => void
}

export default function MediaCard({ item, viewMode, onClick }: MediaCardProps) {
  const getPosterUrl = (posterPath?: string) => {
    if (!posterPath) return '/placeholder-poster.jpg'
    if (posterPath.startsWith('http')) return posterPath
    return `https://image.tmdb.org/t/p/w500${posterPath}`
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return ''
    return new Date(dateString).getFullYear().toString()
  }

  const formatLastWatched = (timestamp?: number) => {
    if (!timestamp) return ''
    const date = new Date(timestamp * 1000)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    return date.toLocaleDateString()
  }

  if (viewMode === 'list') {
    return (
      <div 
        onClick={onClick}
        className="media-card p-4 cursor-pointer hover:bg-gray-800/50"
      >
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0">
            <img
              src={getPosterUrl(item.poster_path)}
              alt={item.title}
              className="w-16 h-24 object-cover rounded"
              onError={(e) => {
                e.currentTarget.src = '/placeholder-poster.jpg'
              }}
            />
          </div>
          
          <div className="flex-grow min-w-0">
            <h3 className="text-lg font-semibold truncate">{item.title}</h3>
            {item.show_name && (
              <p className="text-sm text-gray-400 truncate">{item.show_name}</p>
            )}
            {item.overview && (
              <p className="text-sm text-gray-300 line-clamp-2 mt-1">
                {item.overview}
              </p>
            )}
            
            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
              {item.release_date && (
                <span>{formatDate(item.release_date)}</span>
              )}
              {item.vote_average && item.vote_average > 0 && (
                <div className="flex items-center space-x-1">
                  <Star className="w-3 h-3 fill-current text-yellow-500" />
                  <span>{item.vote_average.toFixed(1)}</span>
                </div>
              )}
              {item.subtitles.length > 0 && (
                <span className="bg-media-accent/20 text-media-accent px-2 py-1 rounded">
                  CC
                </span>
              )}
            </div>
          </div>
          
          <div className="flex flex-col items-end space-y-2">
            <button className="bg-media-accent hover:bg-media-hover text-white p-2 rounded-full transition-colors">
              <Play className="w-4 h-4 ml-0.5" />
            </button>
            
            {item.watch_progress > 0 && (
              <div className="text-xs text-gray-400 text-right">
                <div className="flex items-center space-x-1 mb-1">
                  <Clock className="w-3 h-3" />
                  <span>{Math.round(item.watch_progress)}%</span>
                </div>
                {item.last_watched && (
                  <div className="text-gray-500">
                    {formatLastWatched(item.last_watched)}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        {item.watch_progress > 0 && (
          <div className="mt-3">
            <div className="w-full h-1 bg-gray-600 rounded-full">
              <div 
                className="h-full bg-media-accent rounded-full transition-all"
                style={{ width: `${item.watch_progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div 
      onClick={onClick}
      className="media-card cursor-pointer group"
    >
      <div className="relative aspect-[2/3] mb-3">
        <img
          src={getPosterUrl(item.poster_path)}
          alt={item.title}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.currentTarget.src = '/placeholder-poster.jpg'
          }}
        />
        
        {/* Play Overlay */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <button className="bg-media-accent hover:bg-media-hover text-white p-3 rounded-full transition-all transform group-hover:scale-110">
            <Play className="w-6 h-6 ml-0.5" />
          </button>
        </div>
        
        {/* Progress Bar */}
        {item.watch_progress > 0 && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-600">
            <div 
              className="h-full bg-media-accent transition-all"
              style={{ width: `${item.watch_progress}%` }}
            />
          </div>
        )}
        
        {/* Subtitle Badge */}
        {item.subtitles.length > 0 && (
          <div className="absolute top-2 right-2">
            <span className="bg-black/80 text-white text-xs px-2 py-1 rounded">
              CC
            </span>
          </div>
        )}
        
        {/* Rating Badge */}
        {item.vote_average && item.vote_average > 0 && (
          <div className="absolute top-2 left-2">
            <div className="bg-black/80 text-white text-xs px-2 py-1 rounded flex items-center space-x-1">
              <Star className="w-3 h-3 fill-current text-yellow-500" />
              <span>{item.vote_average.toFixed(1)}</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="p-3">
        <h3 className="font-semibold truncate" title={item.title}>
          {item.title}
        </h3>
        {item.show_name && (
          <p className="text-sm text-gray-400 truncate" title={item.show_name}>
            {item.show_name}
          </p>
        )}
        
        <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
          <span>{formatDate(item.release_date)}</span>
          {item.last_watched && (
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>{formatLastWatched(item.last_watched)}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
