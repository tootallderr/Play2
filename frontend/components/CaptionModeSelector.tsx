import { useState, useEffect } from 'react'
import { Wand2, Brain, Zap, CheckCircle, BookOpen, FileText } from 'lucide-react'

interface CaptionMode {
  key: string
  name: string
  description: string
  icon: React.ReactNode
}

interface CaptionModeSelectorProps {
  selectedMode: string
  onModeChange: (mode: string) => void
  disabled?: boolean
}

export default function CaptionModeSelector({ selectedMode, onModeChange, disabled = false }: CaptionModeSelectorProps) {
  const [availableModes, setAvailableModes] = useState<CaptionMode[]>([])
  const [loading, setLoading] = useState(true)

  const modeIcons: Record<string, React.ReactNode> = {
    weed: <span className="text-xl">🥦</span>,
    theo_von: <span className="text-xl">🎣</span>,
    joey_diaz: <span className="text-xl">🥩</span>,
    fact_check: <Brain className="w-5 h-5" />,
    trivia: <BookOpen className="w-5 h-5" />,
    original: <FileText className="w-5 h-5" />
  }

  useEffect(() => {
    loadAvailableModes()
  }, [])

  const loadAvailableModes = async () => {
    try {
      const response = await fetch('/api/captions/modes')
      if (response.ok) {
        const data = await response.json()
        const modes = Object.entries(data.modes).map(([key, info]: [string, any]) => ({
          key,
          name: info.name,
          description: info.description,
          icon: modeIcons[key] || <Wand2 className="w-5 h-5" />
        }))
        setAvailableModes(modes)
      }
    } catch (error) {
      console.error('Failed to load caption modes:', error)
      // Fallback to default modes
      setAvailableModes([
        {
          key: 'original',
          name: '📝 Original',
          description: 'Unmodified original captions',
          icon: <FileText className="w-5 h-5" />
        },
        {
          key: 'weed',
          name: '🥦 Weed Mode',
          description: 'Chill, slangy, stoner-friendly vibes',
          icon: <span className="text-xl">🥦</span>
        },
        {
          key: 'theo_von',
          name: '🎣 Theo Von Mode',
          description: 'Southern metaphors and absurd storytelling',
          icon: <span className="text-xl">🎣</span>
        },
        {
          key: 'joey_diaz',
          name: '🥩 Joey Diaz Mode',
          description: 'Explosive Bronx-style storytelling',
          icon: <span className="text-xl">🥩</span>
        },
        {
          key: 'fact_check',
          name: '🧠 Fact-Check Mode',
          description: 'Adds quick fact-checks to statements',
          icon: <Brain className="w-5 h-5" />
        },
        {
          key: 'trivia',
          name: '🧾 Trivia Mode',
          description: 'Sprinkles in fun facts about people/places/topics',
          icon: <BookOpen className="w-5 h-5" />
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-4 bg-gray-600 rounded w-32 mb-4"></div>
        <div className="grid grid-cols-2 gap-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-600 rounded-lg"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white">Caption Mode</h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {availableModes.map((mode) => (
          <button
            key={mode.key}
            onClick={() => !disabled && onModeChange(mode.key)}
            disabled={disabled}
            className={`relative p-4 rounded-lg border-2 transition-all duration-200 text-left ${
              selectedMode === mode.key
                ? 'border-media-accent bg-media-accent/10'
                : 'border-gray-600 bg-media-gray hover:border-gray-500'
            } ${
              disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-105'
            }`}
          >
            {/* Selected Indicator */}
            {selectedMode === mode.key && (
              <div className="absolute top-2 right-2">
                <CheckCircle className="w-5 h-5 text-media-accent" />
              </div>
            )}
            
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-1">
                {mode.icon}
              </div>
              <div className="flex-grow min-w-0">
                <h4 className="font-medium text-white truncate">
                  {mode.name}
                </h4>
                <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                  {mode.description}
                </p>
              </div>
            </div>
            
            {/* Mode-specific styling */}
            <div className={`absolute bottom-0 left-0 right-0 h-1 rounded-b-lg transition-all duration-200 ${
              selectedMode === mode.key ? 'opacity-100' : 'opacity-0'
            } ${
              mode.key === 'weed' ? 'bg-green-500' :
              mode.key === 'theo_von' ? 'bg-orange-500' :
              mode.key === 'joey_diaz' ? 'bg-red-500' :
              mode.key === 'fact_check' ? 'bg-blue-500' :
              mode.key === 'trivia' ? 'bg-purple-500' :
              'bg-gray-500'
            }`} />
          </button>
        ))}
      </div>
      
      {selectedMode !== 'original' && (
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
          <div className="flex items-start space-x-2">
            <Zap className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="text-blue-300 font-medium">AI Transformation Active</p>
              <p className="text-blue-200/80 mt-1">
                Captions are being transformed using AI. This may take a moment for the first load.
              </p>
            </div>
          </div>
        </div>
      )}
      
      {disabled && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
          <div className="flex items-start space-x-2">
            <Wand2 className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="text-yellow-300 font-medium">No Subtitles Available</p>
              <p className="text-yellow-200/80 mt-1">
                This media doesn't have subtitle files. Caption transformation is only available for media with subtitles.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
