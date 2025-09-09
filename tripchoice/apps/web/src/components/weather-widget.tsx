'use client'

import { useState, useEffect } from 'react'
import { Cloud, Sun, CloudRain, Snowflake, Wind, Droplets, Eye, Thermometer } from 'lucide-react'

interface WeatherData {
  temperature: number
  condition: string
  humidity: number
  windSpeed: number
  visibility: number
  feelsLike: number
  icon: string
}

interface WeatherWidgetProps {
  destination: string
  compact?: boolean
}

export function WeatherWidget({ destination, compact = false }: WeatherWidgetProps) {
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)

  // Mock weather data - in real app, this would come from an API
  useEffect(() => {
    const mockWeatherData: Record<string, WeatherData> = {
      'Kashmir': {
        temperature: 12,
        condition: 'Partly Cloudy',
        humidity: 65,
        windSpeed: 8,
        visibility: 10,
        feelsLike: 10,
        icon: 'partly-cloudy'
      },
      'Goa': {
        temperature: 32,
        condition: 'Sunny',
        humidity: 75,
        windSpeed: 12,
        visibility: 15,
        feelsLike: 35,
        icon: 'sunny'
      },
      'Kerala': {
        temperature: 28,
        condition: 'Light Rain',
        humidity: 85,
        windSpeed: 10,
        visibility: 8,
        feelsLike: 32,
        icon: 'rain'
      },
      'Dubai': {
        temperature: 35,
        condition: 'Clear',
        humidity: 45,
        windSpeed: 15,
        visibility: 20,
        feelsLike: 38,
        icon: 'sunny'
      },
      'Thailand': {
        temperature: 31,
        condition: 'Thunderstorm',
        humidity: 80,
        windSpeed: 18,
        visibility: 6,
        feelsLike: 36,
        icon: 'storm'
      }
    }

    // Simulate API call delay
    setTimeout(() => {
      const destinationKey = Object.keys(mockWeatherData).find(key =>
        destination.toLowerCase().includes(key.toLowerCase())
      ) || 'Kashmir'

      setWeather(mockWeatherData[destinationKey])
      setLoading(false)
    }, 800)
  }, [destination])

  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'sunny':
      case 'clear':
        return <Sun className="w-6 h-6 text-yellow-500" />
      case 'partly cloudy':
        return <Cloud className="w-6 h-6 text-slate-400" />
      case 'light rain':
      case 'rain':
        return <CloudRain className="w-6 h-6 text-blue-500" />
      case 'snow':
        return <Snowflake className="w-6 h-6 text-blue-300" />
      case 'thunderstorm':
      case 'storm':
        return <CloudRain className="w-6 h-6 text-slate-600" />
      default:
        return <Cloud className="w-6 h-6 text-slate-400" />
    }
  }

  if (loading) {
    return (
      <div className={`bg-white/90 backdrop-blur-sm rounded-xl border border-slate-200 p-4 ${compact ? 'p-3' : 'p-6'}`}>
        <div className="animate-pulse">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-slate-200 rounded-full"></div>
            <div className="h-4 bg-slate-200 rounded w-24"></div>
          </div>
          <div className="space-y-2">
            <div className="h-6 bg-slate-200 rounded w-16"></div>
            <div className="h-4 bg-slate-200 rounded w-20"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!weather) return null

  if (compact) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-lg border border-slate-200 p-3 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getWeatherIcon(weather.condition)}
            <span className="font-semibold text-ink">{weather.temperature}°C</span>
          </div>
          <div className="text-xs text-slate-600">{weather.condition}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-white/95 to-slate-50/95 backdrop-blur-sm rounded-xl border border-slate-200 shadow-lg hover:shadow-xl transition-all duration-300 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-ink text-lg">{destination}</h3>
          <div className="text-sm text-slate-600">Live Weather</div>
        </div>
        {getWeatherIcon(weather.condition)}
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Thermometer className="w-5 h-5 text-red-500" />
            <span className="text-sm text-slate-600">Temperature</span>
          </div>
          <div className="text-right">
            <div className="font-bold text-2xl text-ink">{weather.temperature}°C</div>
            <div className="text-xs text-slate-500">Feels like {weather.feelsLike}°C</div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Cloud className="w-5 h-5 text-blue-500" />
            <span className="text-sm text-slate-600">Condition</span>
          </div>
          <span className="font-medium text-ink">{weather.condition}</span>
        </div>

        <div className="grid grid-cols-3 gap-4 pt-2 border-t border-slate-200">
          <div className="text-center">
            <Droplets className="w-4 h-4 text-blue-400 mx-auto mb-1" />
            <div className="text-xs text-slate-500">Humidity</div>
            <div className="font-semibold text-sm text-ink">{weather.humidity}%</div>
          </div>

          <div className="text-center">
            <Wind className="w-4 h-4 text-slate-400 mx-auto mb-1" />
            <div className="text-xs text-slate-500">Wind</div>
            <div className="font-semibold text-sm text-ink">{weather.windSpeed} km/h</div>
          </div>

          <div className="text-center">
            <Eye className="w-4 h-4 text-green-400 mx-auto mb-1" />
            <div className="text-xs text-slate-500">Visibility</div>
            <div className="font-semibold text-sm text-ink">{weather.visibility} km</div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-slate-200">
        <div className="text-xs text-slate-500 text-center">
          Perfect weather for adventure! 🌟
        </div>
      </div>
    </div>
  )
}
