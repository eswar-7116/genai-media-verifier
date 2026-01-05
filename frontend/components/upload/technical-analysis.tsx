"use client"

import { useState } from 'react'

interface TechnicalAnalysisProps {
  results: any
  fileType: 'image' | 'video'
}

export default function TechnicalAnalysis({ results, fileType }: TechnicalAnalysisProps) {
  const [activeTab, setActiveTab] = useState('overview')

  const tabs = [{ id: 'overview', label: 'Overview' }]

  if (fileType === 'image') {
    const breakdown = results.analysis_breakdown || {}
    if (breakdown.neural_network) tabs.push({ id: 'neural', label: 'Neural' })
    if (breakdown.frequency_domain) tabs.push({ id: 'frequency', label: 'Frequency' })
    if (breakdown.facial_analysis) tabs.push({ id: 'facial', label: 'Facial' })
    if (breakdown.metadata_forensics) tabs.push({ id: 'metadata', label: 'Metadata' })
  } else {
    const layerSummaries = results.layer_summaries || {}
    if (layerSummaries.visual) tabs.push({ id: 'visual', label: 'Visual' })
    if (layerSummaries.audio && layerSummaries.audio.present !== false) tabs.push({ id: 'audio', label: 'Audio' })
    if (layerSummaries.physiological) tabs.push({ id: 'physiological', label: 'Physiological' })
    if (layerSummaries.physics) tabs.push({ id: 'physics', label: 'Physics' })
    if (layerSummaries.specialized) tabs.push({ id: 'specialized', label: 'Specialized' })
    if (layerSummaries.metadata) tabs.push({ id: 'metadata', label: 'Metadata' })
  }

  const renderMetric = (label: string, value: number | string | boolean, suffix = '') => {
    let displayValue: string
    
    if (typeof value === 'boolean') {
      displayValue = value ? 'Yes' : 'No'
    } else if (typeof value === 'number') {
      displayValue = `${Math.round(value * 100)}${suffix}`
    } else {
      displayValue = value
    }
    
    return (
      <div className="flex justify-between items-center py-3 border-b border-white/10 last:border-0">
        <span className="text-sm text-white/60">{label}</span>
        <span className="text-sm font-light text-white">{displayValue}</span>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-light tracking-[4px] uppercase text-white">Technical Analysis</h2>
        <p className="text-white/50 mt-2 tracking-wide">Detailed forensic inspection</p>
      </div>

      <div className="border-b border-white/10">
        <div className="flex gap-8 overflow-x-auto scrollbar-hide">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                pb-4 px-2 text-sm font-light tracking-[2px] uppercase whitespace-nowrap
                transition-all border-b-2 -mb-px
                ${activeTab === tab.id 
                  ? 'border-cyan-400 text-cyan-400' 
                  : 'border-transparent text-white/40 hover:text-white/70'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="min-h-[300px]">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <p className="text-white/70 leading-relaxed">
              This {results.analysis_type || 'comprehensive'} analysis applied multiple forensic methods 
              to detect signs of manipulation or synthetic generation in this {fileType}.
            </p>

            {fileType === 'image' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {results.analysis_breakdown?.neural_network && (
                  <div className="space-y-4">
                    <h3 className="font-light tracking-[2px] uppercase text-white/90">Neural Network Ensemble</h3>
                    <div className="space-y-1">
                      {renderMetric('Detection Score', results.analysis_breakdown.neural_network.score, '%')}
                      {renderMetric('Confidence', results.analysis_breakdown.neural_network.confidence, '%')}
                      {renderMetric('Models Used', results.analysis_breakdown.neural_network.num_models, '')}
                    </div>
                  </div>
                )}
                {results.analysis_breakdown?.frequency_domain && (
                  <div className="space-y-4">
                    <h3 className="font-light tracking-[2px] uppercase text-white/90">Frequency Domain</h3>
                    <div className="space-y-1">
                      {renderMetric('Overall Score', results.analysis_breakdown.frequency_domain.score, '%')}
                      {renderMetric('FFT Analysis', results.analysis_breakdown.frequency_domain.fft_score, '%')}
                      {renderMetric('DCT Analysis', results.analysis_breakdown.frequency_domain.dct_score, '%')}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {results.layer_summaries?.visual?.frame_based && (
                  <div className="space-y-4">
                    <h3 className="font-light tracking-[2px] uppercase text-white/90">Frame Analysis</h3>
                    <div className="space-y-1">
                      {renderMetric('Ensemble Average', results.layer_summaries.visual.frame_based.ensemble_avg, '%')}
                      {renderMetric('Face Average', results.layer_summaries.visual.frame_based.face_avg, '%')}
                      {renderMetric('Frequency Average', results.layer_summaries.visual.frame_based.frequency_avg, '%')}
                    </div>
                  </div>
                )}
                {results.layer_summaries?.visual?.temporal && (
                  <div className="space-y-4">
                    <h3 className="font-light tracking-[2px] uppercase text-white/90">Temporal Consistency</h3>
                    <div className="space-y-1">
                      {renderMetric('Overall Score', results.layer_summaries.visual.temporal.score, '%')}
                      {renderMetric('Identity Shifts', results.layer_summaries.visual.temporal.identity_shifts, '')}
                      {renderMetric('Motion Smoothness', results.layer_summaries.visual.temporal.motion_smoothness, '%')}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {fileType === 'image' && activeTab === 'neural' && results.analysis_breakdown?.neural_network && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              Deep learning models trained on thousands of real and fake images to detect subtle patterns.
            </p>
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-6">
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">Overall Score</div>
                  <div className="text-4xl font-light text-cyan-400">
                    {Math.round(results.analysis_breakdown.neural_network.score * 100)}%
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">Confidence</div>
                  <div className="text-4xl font-light text-cyan-400">
                    {Math.round(results.analysis_breakdown.neural_network.confidence * 100)}%
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">Agreement</div>
                  <div className="text-lg font-light text-white capitalize pt-2">
                    {results.analysis_breakdown.neural_network.model_agreement?.replace('_', ' ')}
                  </div>
                </div>
              </div>
              
              <div className="pt-4 space-y-3">
                <h4 className="text-sm text-white/60 uppercase tracking-wider">Model Scores</h4>
                {results.analysis_breakdown.neural_network.model_names?.map((name: string, idx: number) => {
                  const score = results.analysis_breakdown.neural_network.individual_scores?.[idx]
                  const modelShortName = name.split('/')[1] || name
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-white/50">{modelShortName}</span>
                        <span className="text-white/70">{score ? Math.round(score * 100) : 0}%</span>
                      </div>
                      <div className="w-full bg-white/5 rounded-full h-1.5">
                        <div 
                          className="bg-cyan-400 h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${score ? score * 100 : 0}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {fileType === 'image' && activeTab === 'frequency' && results.analysis_breakdown?.frequency_domain && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              Analyzes frequency domain anomalies using FFT and DCT transforms to detect manipulation artifacts.
            </p>
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-6">
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">Overall Score</div>
                  <div className="text-4xl font-light text-cyan-400">
                    {Math.round(results.analysis_breakdown.frequency_domain.score * 100)}%
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">FFT Score</div>
                  <div className="text-4xl font-light text-cyan-400">
                    {Math.round(results.analysis_breakdown.frequency_domain.fft_score * 100)}%
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">DCT Score</div>
                  <div className="text-4xl font-light text-cyan-400">
                    {Math.round(results.analysis_breakdown.frequency_domain.dct_score * 100)}%
                  </div>
                </div>
              </div>
              
              <div className="pt-4 space-y-2">
                {renderMetric('High Frequency Score', results.analysis_breakdown.frequency_domain.high_freq_score, '%')}
                {renderMetric('FFT Anomaly Detected', results.analysis_breakdown.frequency_domain.fft_anomaly)}
                {renderMetric('DCT Anomaly Detected', results.analysis_breakdown.frequency_domain.dct_anomaly)}
              </div>
            </div>
          </div>
        )}

        {fileType === 'image' && activeTab === 'facial' && results.analysis_breakdown?.facial_analysis && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              Examines facial landmarks, symmetry, skin texture, and lighting consistency using computer vision.
            </p>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">Overall Score</div>
                  <div className="text-4xl font-light text-cyan-400">
                    {Math.round(results.analysis_breakdown.facial_analysis.score * 100)}%
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">Method Used</div>
                  <div className="text-lg font-light text-white pt-2">
                    {results.analysis_breakdown.facial_analysis.method_used || 'N/A'}
                  </div>
                </div>
              </div>
              
              <div className="pt-4 space-y-2">
                {renderMetric('Face Detected', results.analysis_breakdown.facial_analysis.face_detected)}
                {renderMetric('Symmetry Score', results.analysis_breakdown.facial_analysis.symmetry_score, '%')}
                {renderMetric('Eye Quality Score', results.analysis_breakdown.facial_analysis.eye_quality_score, '%')}
                {renderMetric('Skin Texture Score', results.analysis_breakdown.facial_analysis.skin_texture_score, '%')}
                {renderMetric('Lighting Score', results.analysis_breakdown.facial_analysis.lighting_score, '%')}
                {renderMetric('Symmetry Anomaly', results.analysis_breakdown.facial_analysis.symmetry_anomaly)}
                {renderMetric('Eye Anomaly', results.analysis_breakdown.facial_analysis.eye_anomaly)}
                {renderMetric('Texture Anomaly', results.analysis_breakdown.facial_analysis.texture_anomaly)}
              </div>
            </div>
          </div>
        )}

        {fileType === 'video' && activeTab === 'visual' && results.layer_summaries?.visual && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              Multi-modal visual analysis combining frame-based detection, temporal consistency, and 3D video models.
            </p>
            <div className="space-y-6">
              {results.layer_summaries.visual.frame_based && (
                <div className="space-y-4">
                  <h3 className="font-light tracking-[2px] uppercase text-white/90">Frame-Based Analysis</h3>
                  <div className="space-y-1">
                    {renderMetric('Ensemble Average', results.layer_summaries.visual.frame_based.ensemble_avg, '%')}
                    {renderMetric('Ensemble Maximum', results.layer_summaries.visual.frame_based.ensemble_max, '%')}
                    {renderMetric('Face Average', results.layer_summaries.visual.frame_based.face_avg, '%')}
                    {renderMetric('Frequency Average', results.layer_summaries.visual.frame_based.frequency_avg, '%')}
                  </div>
                </div>
              )}
              {results.layer_summaries.visual.temporal && (
                <div className="space-y-4">
                  <h3 className="font-light tracking-[2px] uppercase text-white/90">Temporal Consistency</h3>
                  <div className="space-y-1">
                    {renderMetric('Consistency Score', results.layer_summaries.visual.temporal.score, '%')}
                    {renderMetric('Identity Shifts', results.layer_summaries.visual.temporal.identity_shifts, '')}
                    {renderMetric('Motion Smoothness', results.layer_summaries.visual.temporal.motion_smoothness, '%')}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {fileType === 'video' && activeTab === 'audio' && results.layer_summaries?.audio && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              Analyzes voice characteristics and lip-sync correlation to detect audio deepfakes.
            </p>
            <div className="space-y-6">
              <div className="space-y-2">
                <div className="text-xs text-white/40 tracking-[2px] uppercase">Overall Score</div>
                <div className="text-4xl font-light text-cyan-400">
                  {Math.round(results.layer_summaries.audio.score * 100)}%
                </div>
              </div>
              <div className="space-y-2 pt-4">
                {renderMetric('Voice Deepfake', results.layer_summaries.audio.voice_deepfake, '%')}
                {renderMetric('Lip Sync Quality', results.layer_summaries.audio.lip_sync, '%')}
              </div>
            </div>
          </div>
        )}

        {fileType === 'video' && activeTab === 'physiological' && results.layer_summaries?.physiological && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              Detects physiological signals like heartbeat and blink patterns via remote sensing.
            </p>
            <div className="space-y-6">
              <div className="space-y-2">
                <div className="text-xs text-white/40 tracking-[2px] uppercase">Overall Score</div>
                <div className="text-4xl font-light text-cyan-400">
                  {Math.round(results.layer_summaries.physiological.score * 100)}%
                </div>
              </div>
              <div className="space-y-2 pt-4">
                {renderMetric('Heartbeat Detected', results.layer_summaries.physiological.heartbeat_detected ? 'Yes' : 'No', '')}
                {results.layer_summaries.physiological.heartbeat_detected && 
                  renderMetric('Heart Rate (BPM)', results.layer_summaries.physiological.heartbeat_bpm, '')
                }
                {renderMetric('Natural Blink Pattern', results.layer_summaries.physiological.natural_blink_pattern ? 'Yes' : 'No', '')}
                {renderMetric('Blink Count', results.layer_summaries.physiological.blink_count, '')}
              </div>
            </div>
          </div>
        )}

        {fileType === 'video' && activeTab === 'physics' && results.layer_summaries?.physics && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              Checks lighting consistency and depth plausibility using physics-based analysis.
            </p>
            <div className="space-y-6">
              <div className="space-y-2">
                <div className="text-xs text-white/40 tracking-[2px] uppercase">Overall Score</div>
                <div className="text-4xl font-light text-cyan-400">
                  {Math.round(results.layer_summaries.physics.score * 100)}%
                </div>
              </div>
              <div className="space-y-2 pt-4">
                {renderMetric('Lighting Consistent', results.layer_summaries.physics.lighting_consistent ? 'Yes' : 'No', '')}
                {renderMetric('Depth Plausible', results.layer_summaries.physics.depth_plausible ? 'Yes' : 'No', '')}
              </div>
            </div>
          </div>
        )}

        {fileType === 'video' && activeTab === 'specialized' && results.layer_summaries?.specialized && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              Advanced boundary and compression analysis for detecting splice points and editing artifacts.
            </p>
            <div className="space-y-6">
              {results.layer_summaries.specialized.boundary && (
                <div className="space-y-4">
                  <h3 className="font-light tracking-[2px] uppercase text-white/90">Boundary Analysis</h3>
                  <div className="space-y-1">
                    {renderMetric('Detection Score', results.layer_summaries.specialized.boundary.score, '%')}
                    {renderMetric('Suspicious Transitions', results.layer_summaries.specialized.boundary.suspicious_transitions, '')}
                    {renderMetric('Quality Drops', results.layer_summaries.specialized.boundary.quality_drops, '')}
                  </div>
                </div>
              )}
              {results.layer_summaries.specialized.compression && (
                <div className="space-y-4">
                  <h3 className="font-light tracking-[2px] uppercase text-white/90">Compression Analysis</h3>
                  <div className="space-y-1">
                    {renderMetric('Detection Score', results.layer_summaries.specialized.compression.score, '%')}
                    {renderMetric('Compression Mismatches', results.layer_summaries.specialized.compression.mismatches, '')}
                    {renderMetric('Face Compression', results.layer_summaries.specialized.compression.face_compression, '%')}
                    {renderMetric('Background Compression', results.layer_summaries.specialized.compression.background_compression, '%')}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'metadata' && (
          <div className="space-y-8">
            <p className="text-white/60 leading-relaxed text-sm">
              {fileType === 'image' 
                ? 'Analyzes EXIF metadata and compression patterns using Error Level Analysis.'
                : 'Analyzes video container metadata, encoding parameters, and frame rate consistency.'
              }
            </p>
            <div className="space-y-6">
              {fileType === 'image' && results.analysis_breakdown?.metadata_forensics && (
                <>
                  <div className="space-y-2">
                    <div className="text-xs text-white/40 tracking-[2px] uppercase">Overall Score</div>
                    <div className="text-4xl font-light text-cyan-400">
                      {Math.round(results.analysis_breakdown.metadata_forensics.score * 100)}%
                    </div>
                  </div>
                  
                  <div className="pt-4 space-y-2">
                    {renderMetric('EXIF Present', results.analysis_breakdown.metadata_forensics.exif_present)}
                    {renderMetric('EXIF Score', results.analysis_breakdown.metadata_forensics.exif_score, '%')}
                    {renderMetric('ELA Score', results.analysis_breakdown.metadata_forensics.ela_score, '%')}
                    {renderMetric('Compression Score', results.analysis_breakdown.metadata_forensics.compression_score, '%')}
                    {renderMetric('Editing Software', results.analysis_breakdown.metadata_forensics.editing_software_detected || 'Unknown')}
                    {renderMetric('EXIF Suspicious', results.analysis_breakdown.metadata_forensics.exif_suspicious)}
                    {renderMetric('ELA Anomalies', results.analysis_breakdown.metadata_forensics.ela_anomalies)}
                  </div>
                </>
              )}
              {fileType === 'video' && results.layer_summaries?.metadata && (
                <div className="space-y-2">
                  <div className="text-xs text-white/40 tracking-[2px] uppercase">Overall Score</div>
                  <div className="text-4xl font-light text-cyan-400">
                    {Math.round(results.layer_summaries.metadata.score * 100)}%
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  )
}
