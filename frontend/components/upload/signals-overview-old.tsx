"use client"

interface SignalsOverviewProps {
  results: any
  fileType: 'image' | 'video'
}

function EnsembleDistributionStrip({ avgScore, maxScore }: { avgScore: number; maxScore: number }) {
  const generateDistribution = () => {
    const bars = 16
    const distribution = []
    for (let i = 0; i < bars; i++) {
      let value = avgScore + (Math.random() - 0.5) * 0.3
      if (i === Math.floor(bars * 0.7)) {
        value = maxScore
      }
      distribution.push(Math.max(0, Math.min(1, value)))
    }
    return distribution
  }

  const distribution = generateDistribution()
  const getBarHeight = (value: number) => {
    const heights = ['h-1', 'h-2', 'h-3', 'h-4', 'h-5', 'h-6', 'h-7', 'h-8']
    const index = Math.floor(value * (heights.length - 1))
    return heights[index]
  }

  const getBarColor = (value: number) => {
    if (value < 0.4) return 'bg-emerald-500'
    if (value < 0.65) return 'bg-amber-500'
    return 'bg-rose-500'
  }

  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-neutral-700">Frame Ensemble</div>
      <div className="flex items-end justify-between h-10 gap-1 px-2 py-1 bg-neutral-100 rounded">
        {distribution.map((value, idx) => (
          <div
            key={idx}
            className={`w-full ${getBarHeight(value)} ${getBarColor(value)} rounded-sm transition-all duration-300`}
          />
        ))}
      </div>
      <div className="text-xs text-neutral-600 space-y-0.5">
        <div>Avg: {Math.round(avgScore * 100)}%</div>
        <div>Max: {Math.round(maxScore * 100)}% (1 frame)</div>
      </div>
    </div>
  )
}

function IdentityTimeline({ shifts }: { shifts: number }) {
  const generateClusters = () => {
    if (shifts === 0) return []
    
    const totalFrames = 50
    const clusters: { position: number; intensity: number; count: number }[] = []
    
    let numClusters = 1
    if (shifts > 30) numClusters = 5
    else if (shifts > 20) numClusters = 4
    else if (shifts > 10) numClusters = 3
    else if (shifts > 5) numClusters = 2
    
    const shiftsPerCluster = Math.floor(shifts / numClusters)
    const remainingShifts = shifts % numClusters
    
    for (let i = 0; i < numClusters; i++) {
      const clusterShifts = shiftsPerCluster + (i < remainingShifts ? 1 : 0)
      const position = ((i + 0.5) / numClusters) * 100
      
      const intensity = Math.min(clusterShifts / 10, 1)
      
      clusters.push({
        position,
        intensity,
        count: clusterShifts
      })
    }
    
    return clusters
  }

  const clusters = generateClusters()
  
  const generateMarkers = () => {
    const markers: { position: number; size: number }[] = []
    
    clusters.forEach(cluster => {
      const spread = 8 / (cluster.intensity * 2 + 1)
      const markerCount = Math.min(cluster.count, 8)
      
      for (let i = 0; i < markerCount; i++) {
        const offset = (i - markerCount / 2) * spread
        const position = Math.max(2, Math.min(98, cluster.position + offset))
        
        const size = 6 + cluster.intensity * 6
        
        markers.push({ position, size })
      }
    })
    
    return markers
  }

  const markers = generateMarkers()

  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-neutral-700">Temporal Consistency</div>
      <div className="relative h-10 flex items-center px-2">
        <div className="absolute inset-x-2 h-0.5 bg-neutral-300" />
        
        <div className="absolute inset-x-2 flex justify-between">
          {Array.from({ length: 50 }).map((_, i) => (
            <div key={i} className="w-px h-1 bg-neutral-200" />
          ))}
        </div>
        
        {markers.map((marker, idx) => (
          <div
            key={idx}
            className="absolute bg-rose-500 rounded-full transition-all duration-300"
            style={{ 
              left: `${marker.position}%`,
              width: `${marker.size}px`,
              height: `${marker.size}px`,
              transform: 'translate(-50%, 0)',
              opacity: 0.8
            }}
          />
        ))}
      </div>
      <div className="text-xs text-neutral-600">
        {shifts} identity shifts detected
      </div>
    </div>
  )
}

function CoherenceStrip({ score }: { score: number }) {
  const coherence = Math.round(score * 100)
  
  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-neutral-700">Video Model Analysis</div>
      <div className="text-xs text-neutral-500 mb-2">VideoMAE — Global Temporal Coherence</div>
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-neutral-500">
          <span>Realistic</span>
          <span>Unrealistic</span>
        </div>
        <div className="h-6 bg-neutral-200 rounded overflow-hidden">
          <div
            className="h-full bg-rose-500 transition-all duration-700"
            style={{ width: `${coherence}%` }}
          />
        </div>
      </div>
      <div className="text-xs text-neutral-600">
        {coherence}% coherence
      </div>
    </div>
  )
}

function PhysiologicalBand({ 
  score, 
  blinkNatural, 
  heartbeatDetected 
}: { 
  score: number
  blinkNatural: boolean
  heartbeatDetected: boolean 
}) {
  const anomalyLikelihood = Math.round(score * 100)
  
  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-neutral-700">Physiological Signals</div>
      <div className="space-y-2 text-xs text-neutral-700">
        <div className="flex items-start gap-2">
          <span className="text-neutral-400">•</span>
          <span>Blink pattern: {blinkNatural ? 'Natural' : 'Unnatural'}</span>
        </div>
        <div className="flex items-start gap-2">
          <span className="text-neutral-400">•</span>
          <span>Heartbeat: {heartbeatDetected ? 'Detected' : 'Not detected'}</span>
        </div>
      </div>
      <div className="space-y-2 mt-3">
        <div className="flex justify-between text-xs text-neutral-500">
          <span>Natural</span>
          <span>Anomalous</span>
        </div>
        <div className="h-6 bg-neutral-200 rounded overflow-hidden">
          <div
            className="h-full bg-rose-500 transition-all duration-700"
            style={{ width: `${anomalyLikelihood}%` }}
          />
        </div>
      </div>
      <div className="text-xs text-neutral-600">
        {anomalyLikelihood}% anomaly likelihood
      </div>
    </div>
  )
}

function AudioWaveform({ score }: { score: number }) {
  const waveHeights = [3, 5, 2, 6, 4, 7, 3, 5, 2, 4, 6, 3, 5, 7, 4, 2, 5, 6, 3, 4]
  
  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-neutral-700">Audio Analysis</div>
      <div className="flex items-center justify-between h-10 gap-0.5 px-2 py-1 bg-neutral-100 rounded">
        {waveHeights.map((height, idx) => (
          <div
            key={idx}
            className="w-full bg-blue-500 rounded-sm transition-all duration-300"
            style={{ height: `${height * 4}px` }}
          />
        ))}
      </div>
      <div className="text-xs text-neutral-600">
        Audio present: {Math.round(score * 100)}% confidence
      </div>
    </div>
  )
}

function PhysicsBand({ score, lightingConsistent, depthPlausible }: { 
  score: number
  lightingConsistent: boolean
  depthPlausible: boolean 
}) {
  const anomalyScore = Math.round(score * 100)
  
  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-neutral-700">Physics Consistency</div>
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-neutral-500">
          <span>Plausible</span>
          <span>Anomalous</span>
        </div>
        <div className="h-6 bg-neutral-200 rounded overflow-hidden">
          <div
            className="h-full bg-amber-500 transition-all duration-700"
            style={{ width: `${anomalyScore}%` }}
          />
        </div>
      </div>
      <div className="text-xs text-neutral-600 space-y-0.5">
        <div>Lighting: {lightingConsistent ? 'Consistent' : 'Inconsistent'}</div>
        <div>Depth: {depthPlausible ? 'Plausible' : 'Implausible'}</div>
      </div>
    </div>
  )
}

function MetadataCard({ score, detail }: { score: number; detail: string }) {
  const percentage = Math.round(score * 100)
  
  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-neutral-700">Metadata</div>
      <div className="text-xs text-neutral-500 mb-2">{detail}</div>
      <div className="h-6 bg-neutral-200 rounded overflow-hidden">
        <div
          className="h-full bg-neutral-400 transition-all duration-700"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="text-xs text-neutral-600">
        {percentage}% suspicion
      </div>
    </div>
  )
}

export default function SignalsOverview({ results, fileType }: SignalsOverviewProps) {
  if (fileType === 'image') {
    const breakdown = results.analysis_breakdown || {}
    const signals = []

    if (breakdown.neural_network) {
      signals.push({
        type: 'neural',
        title: 'Neural Networks',
        score: breakdown.neural_network.score,
        detail: breakdown.neural_network.model_agreement 
          ? `${breakdown.neural_network.model_agreement.replace('_', ' ')} agreement`
          : `${breakdown.neural_network.num_models || 0} models`
      })
    }

    if (breakdown.frequency_domain) {
      signals.push({
        type: 'frequency',
        title: 'Frequency Domain',
        score: breakdown.frequency_domain.score,
        detail: breakdown.frequency_domain.dct_anomaly || breakdown.frequency_domain.fft_anomaly
          ? 'Anomalies detected'
          : 'No major anomalies'
      })
    }

    if (breakdown.facial_analysis) {
      signals.push({
        type: 'facial',
        title: 'Facial Forensics',
        score: breakdown.facial_analysis.score,
        detail: breakdown.facial_analysis.face_detected 
          ? `${breakdown.facial_analysis.method_used || 'Face detected'}`
          : 'No faces detected'
      })
    }

    if (breakdown.metadata_forensics) {
      signals.push({
        type: 'metadata',
        title: 'Metadata',
        score: breakdown.metadata_forensics.score,
        detail: breakdown.metadata_forensics.exif_present 
          ? 'EXIF present'
          : 'No EXIF data'
      })
    }

    if (signals.length === 0) {
      return (
        <div className="text-center py-8 text-neutral-500">
          No analysis signals available
        </div>
      )
    }

    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-neutral-900 tracking-tight">Signals Overview</h2>
          <p className="text-neutral-600 mt-1">Analysis methods applied to this media</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {signals.map((signal, idx) => (
            <div key={idx} className="p-6 bg-white rounded-lg border border-neutral-200 shadow-sm">
              {signal.type === 'metadata' ? (
                <MetadataCard score={signal.score} detail={signal.detail} />
              ) : (
                <div className="space-y-3">
                  <div className="text-sm font-medium text-neutral-700">{signal.title}</div>
                  <div className="text-xs text-neutral-500 mb-2">{signal.detail}</div>
                  <div className="h-6 bg-neutral-200 rounded overflow-hidden">
                    <div
                      className={`h-full transition-all duration-700 ${
                        signal.score < 0.4 ? 'bg-emerald-500' :
                        signal.score < 0.65 ? 'bg-amber-500' : 'bg-rose-500'
                      }`}
                      style={{ width: `${Math.round(signal.score * 100)}%` }}
                    />
                  </div>
                  <div className="text-xs text-neutral-600">
                    {Math.round(signal.score * 100)}% detection
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  const layerSummaries = results.layer_summaries || {}
  const cards = []

  if (layerSummaries.visual?.frame_based) {
    cards.push({
      type: 'ensemble',
      data: layerSummaries.visual.frame_based
    })
  }

  if (layerSummaries.visual?.temporal) {
    cards.push({
      type: 'temporal',
      data: layerSummaries.visual.temporal
    })
  }

  if (layerSummaries.visual?.['3d_model']) {
    cards.push({
      type: 'coherence',
      data: layerSummaries.visual['3d_model']
    })
  }

  if (layerSummaries.physiological) {
    cards.push({
      type: 'physiological',
      data: layerSummaries.physiological
    })
  }

  if (layerSummaries.physics) {
    cards.push({
      type: 'physics',
      data: layerSummaries.physics
    })
  }

  if (layerSummaries.metadata) {
    if (layerSummaries.metadata.has_audio && layerSummaries.audio?.score) {
      cards.push({
        type: 'audio',
        data: layerSummaries.audio
      })
    } else {
      cards.push({
        type: 'no-audio',
        data: layerSummaries.metadata
      })
    }
  }

  if (cards.length === 0) {
    return (
      <div className="text-center py-8 text-neutral-500">
        No analysis signals available
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-neutral-900 tracking-tight">Signals Overview</h2>
        <p className="text-neutral-600 mt-1">Analysis methods applied to this media</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {cards.map((card, idx) => (
          <div key={idx} className="p-6 bg-white rounded-lg border border-neutral-200 shadow-sm">
            {card.type === 'ensemble' && (
              <EnsembleDistributionStrip
                avgScore={card.data.ensemble_avg}
                maxScore={card.data.ensemble_max}
              />
            )}
            {card.type === 'temporal' && (
              <IdentityTimeline shifts={card.data.identity_shifts} />
            )}
            {card.type === 'coherence' && (
              <CoherenceStrip score={card.data.score} />
            )}
            {card.type === 'physiological' && (
              <PhysiologicalBand
                score={card.data.score}
                blinkNatural={card.data.natural_blink_pattern}
                heartbeatDetected={card.data.heartbeat_detected}
              />
            )}
            {card.type === 'physics' && (
              <PhysicsBand
                score={card.data.score}
                lightingConsistent={card.data.lighting_consistent}
                depthPlausible={card.data.depth_plausible}
              />
            )}
            {card.type === 'audio' && (
              <AudioWaveform score={card.data.score} />
            )}
            {card.type === 'no-audio' && (
              <div className="space-y-3">
                <div className="text-sm font-medium text-neutral-700">Metadata</div>
                <div className="text-xs text-neutral-500 mb-2">No audio</div>
                <div className="h-6 bg-neutral-200 rounded overflow-hidden">
                  <div className="h-full bg-neutral-400 w-0" />
                </div>
                <div className="text-xs text-neutral-600">0% audio present</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
