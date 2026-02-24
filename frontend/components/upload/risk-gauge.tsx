"use client"

interface RiskGaugeProps {
  manipulationScore: number
  riskLevel: string
  gaugeType?: 'risk' | 'confidence'
}

export default function RiskGauge({ manipulationScore, riskLevel, gaugeType = 'risk' }: RiskGaugeProps) {
  const percentage = Math.round(manipulationScore * 100)
  
  const getRiskConfig = () => {
    if (gaugeType === 'confidence') {
      let confidenceLevel = 'Low Confidence'
      let color = '#ef4444'
      
      if (manipulationScore >= 0.7) {
        confidenceLevel = 'High Confidence'
        color = '#10b981'
      } else if (manipulationScore >= 0.4) {
        confidenceLevel = 'Medium Confidence'
        color = '#f59e0b'
      }
      
      return {
        label: confidenceLevel.toUpperCase(),
        color: `text-[${color}]`,
        gaugeColor: color,
        glowColor: `${color}4D`
      }
    }
    
    const level = riskLevel.toLowerCase()
    if (level === 'low') return { 
      label: 'LOW RISK', 
      color: 'text-emerald-400',
      gaugeColor: '#10b981',
      glowColor: 'rgba(16, 185, 129, 0.3)'
    }
    if (level === 'medium') return { 
      label: 'MEDIUM RISK', 
      color: 'text-amber-400',
      gaugeColor: '#f59e0b',
      glowColor: 'rgba(245, 158, 11, 0.3)'
    }
    return { 
      label: 'HIGH RISK', 
      color: 'text-rose-400',
      gaugeColor: '#f43f5e',
      glowColor: 'rgba(244, 63, 94, 0.3)'
    }
  }

  const config = getRiskConfig()
  const circumference = 2 * Math.PI * 110
  const offset = circumference - (percentage / 100) * circumference

  return (
    <div className="flex flex-col items-center space-y-6">
      <div className="relative">
        <svg width="280" height="280" viewBox="0 0 280 280" className="transform -rotate-90">
          <circle
            cx="140"
            cy="140"
            r="110"
            fill="none"
            stroke="rgba(255, 255, 255, 0.05)"
            strokeWidth="16"
          />
          <circle
            cx="140"
            cy="140"
            r="110"
            fill="none"
            stroke={config.gaugeColor}
            strokeWidth="16"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            style={{
              filter: `drop-shadow(0 0 10px ${config.glowColor})`
            }}
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={`text-7xl font-light tracking-wider ${config.color} mb-2`}
               style={{ 
                 textShadow: `0 0 20px ${config.glowColor}`,
                 color: config.gaugeColor
               }}>
            {percentage}
          </div>
          <div className="text-xs text-white/40 tracking-[3px] uppercase">
            {gaugeType === 'risk' ? 'Manipulation' : 'Confidence'}
          </div>
        </div>
      </div>

      <div className="text-center">
        <div className={`text-lg font-light tracking-[3px] uppercase ${config.color}`}
             style={{ color: config.gaugeColor }}>
          {config.label}
        </div>
      </div>
    </div>
  )
}
