"use client"

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react'

interface AnalysisTabsProps {
  results: any
  fileType: 'image' | 'video'
  mode: 'quick' | 'deep'
}

export default function AnalysisTabs({ results, fileType, mode }: AnalysisTabsProps) {
  const [activeTab, setActiveTab] = useState('overview')

  const breakdown = results.analysis_breakdown || {}
  const neuralData = breakdown.neural_network
  const frequencyData = breakdown.frequency_domain
  const facialData = breakdown.facial_analysis
  const metadataData = breakdown.metadata_forensics
  const temporalData = breakdown.temporal_analysis
  const audioData = breakdown.audio_analysis

  const renderScoreBar = (score: number, label: string, anomaly?: boolean) => {
    const percentage = Math.round(score * 100)
    
    return (
      <div className="space-y-2" key={label}>
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-700">{label}</span>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-900">{percentage}%</span>
            {anomaly !== undefined && (
              anomaly ? (
                <AlertCircle className="w-4 h-4 text-yellow-600" />
              ) : (
                <CheckCircle className="w-4 h-4 text-green-600" />
              )
            )}
          </div>
        </div>
        <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              percentage < 40 ? 'bg-gradient-to-r from-green-500 to-green-600' :
              percentage < 65 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
              'bg-gradient-to-r from-red-500 to-red-600'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    )
  }

  const renderMetric = (label: string, value: any) => (
    <div className="flex justify-between items-center py-2 border-b border-gray-100" key={label}>
      <span className="text-sm text-gray-600">{label}</span>
      <span className="text-sm font-medium text-gray-900">
        {typeof value === 'number' ? value.toFixed(3) : String(value)}
      </span>
    </div>
  )

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList className="w-full justify-start overflow-x-auto bg-gray-100 p-1 rounded-lg">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        {neuralData && <TabsTrigger value="neural">Neural Network</TabsTrigger>}
        {frequencyData && <TabsTrigger value="frequency">Frequency Domain</TabsTrigger>}
        {facialData && <TabsTrigger value="facial">Facial Analysis</TabsTrigger>}
        {metadataData && <TabsTrigger value="metadata">Metadata</TabsTrigger>}
        {temporalData && fileType === 'video' && <TabsTrigger value="temporal">Temporal</TabsTrigger>}
        {audioData && fileType === 'video' && <TabsTrigger value="audio">Audio</TabsTrigger>}
        <TabsTrigger value="report">Full Report</TabsTrigger>
      </TabsList>

      <TabsContent value="overview" className="space-y-6 p-6">
        <div>
          <h3 className="text-2xl font-bold mb-2">Analysis Summary</h3>
          <p className="text-gray-600 mb-6">
            {results.analysis_type === 'comprehensive' ? 'Comprehensive' : 'Quick'} analysis completed using {
              [neuralData && 'neural networks', 
               frequencyData && 'frequency analysis', 
               facialData && 'facial forensics', 
               metadataData && 'metadata inspection']
              .filter(Boolean).join(', ')
            }.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {neuralData && (
            <div className="p-6 bg-white border-2 border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                Neural Network Analysis
              </h3>
              {renderScoreBar(neuralData.score, 'Detection Score')}
              <div className="mt-4 text-xs text-gray-500">
                {neuralData.num_models} models • {neuralData.model_agreement} agreement
              </div>
            </div>
          )}

          {frequencyData && (
            <div className="p-6 bg-white border-2 border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                Frequency Domain
              </h3>
              {renderScoreBar(frequencyData.score, 'Anomaly Score')}
              <div className="mt-4 space-y-1 text-xs text-gray-500">
                {frequencyData.fft_anomaly && <div className="text-yellow-600">FFT anomaly detected</div>}
                {frequencyData.dct_anomaly && <div className="text-yellow-600">DCT anomaly detected</div>}
                {!frequencyData.fft_anomaly && !frequencyData.dct_anomaly && (
                  <div className="text-green-600">No major anomalies</div>
                )}
              </div>
            </div>
          )}

          {facialData && (
            <div className="p-6 bg-white border-2 border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                Facial Forensics
              </h3>
              {renderScoreBar(facialData.score, 'Manipulation Score')}
              <div className="mt-4 text-xs text-gray-500">
                {facialData.face_detected ? (
                  <div className="text-green-600">Face detected • {facialData.method_used}</div>
                ) : (
                  <div className="text-gray-500">No faces detected</div>
                )}
              </div>
            </div>
          )}

          {metadataData && (
            <div className="p-6 bg-white border-2 border-gray-200 rounded-xl">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                Metadata Forensics
              </h3>
              {renderScoreBar(metadataData.score, 'Suspicion Score')}
              <div className="mt-4 space-y-1 text-xs text-gray-500">
                {metadataData.exif_present ? (
                  <div className="text-green-600">EXIF data present</div>
                ) : (
                  <div className="text-yellow-600">No EXIF data</div>
                )}
                {metadataData.ela_anomalies && (
                  <div className="text-yellow-600">ELA anomalies detected</div>
                )}
              </div>
            </div>
          )}
        </div>
      </TabsContent>

      {neuralData && (
        <TabsContent value="neural" className="space-y-6 p-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-xl font-semibold mb-2">Neural Network Analysis</h3>
              <p className="text-gray-600 text-sm">
                Deep learning models trained to detect AI-generated and manipulated media
              </p>
            </div>

            {renderScoreBar(neuralData.score, 'Overall Neural Score')}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Confidence</div>
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(neuralData.confidence * 100)}%
                </div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Model Agreement</div>
                <div className="text-lg font-semibold text-gray-900 capitalize">
                  {neuralData.model_agreement?.replace('_', ' ')}
                </div>
              </div>
            </div>

            {neuralData.individual_scores && neuralData.model_names && (
              <div className="space-y-4 mt-6">
                <h4 className="font-semibold">Individual Model Predictions</h4>
                <div className="space-y-3">
                  {neuralData.individual_scores.map((score: number, idx: number) => (
                    <div key={idx}>
                      {renderScoreBar(score, neuralData.model_names[idx] || `Model ${idx + 1}`)}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">Methodology</h4>
              <p className="text-sm text-blue-800">
                {neuralData.num_models} specialized deepfake detection models analyzed the media. 
                The ensemble approach combines their predictions to reduce false positives and improve accuracy.
              </p>
            </div>
          </div>
        </TabsContent>
      )}

      {frequencyData && (
        <TabsContent value="frequency" className="space-y-6 p-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-xl font-semibold mb-2">Frequency Domain Analysis</h3>
              <p className="text-gray-600 text-sm">
                FFT and DCT analysis to detect artifacts from GANs, diffusion models, and editing
              </p>
            </div>

            {renderScoreBar(frequencyData.score, 'Overall Frequency Score')}

            <div className="space-y-4 mt-6">
              {renderScoreBar(frequencyData.fft_score, 'FFT Analysis', frequencyData.fft_anomaly)}
              {renderScoreBar(frequencyData.dct_score, 'DCT Analysis', frequencyData.dct_anomaly)}
              {renderScoreBar(frequencyData.high_freq_score, 'High Frequency Score')}
            </div>

            {(frequencyData.fft_anomaly || frequencyData.dct_anomaly) && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-semibold text-yellow-800 mb-2">Detected Anomalies</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
                  {frequencyData.fft_anomaly && (
                    <li>FFT patterns suggest potential manipulation in frequency domain</li>
                  )}
                  {frequencyData.dct_anomaly && (
                    <li>DCT coefficients show compression or generation artifacts</li>
                  )}
                </ul>
              </div>
            )}

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">What This Means</h4>
              <p className="text-sm text-blue-800">
                Frequency analysis examines patterns invisible to the human eye. GANs and diffusion models 
                often leave characteristic fingerprints in the frequency domain that natural images don't have.
              </p>
            </div>
          </div>
        </TabsContent>
      )}

      {facialData && (
        <TabsContent value="facial" className="space-y-6 p-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-xl font-semibold mb-2">Facial Forensics Analysis</h3>
              <p className="text-gray-600 text-sm">
                Examining facial symmetry, eye quality, skin texture, and lighting consistency
              </p>
            </div>

            {!facialData.face_detected ? (
              <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg text-center">
                <p className="text-gray-600">No faces detected in this media</p>
              </div>
            ) : (
              <>
                {renderScoreBar(facialData.score, 'Overall Facial Score')}

                <div className="space-y-4 mt-6">
                  {renderScoreBar(facialData.symmetry_score, 'Facial Symmetry', facialData.symmetry_anomaly)}
                  {renderScoreBar(facialData.eye_quality_score, 'Eye Quality', facialData.eye_anomaly)}
                  {renderScoreBar(facialData.skin_texture_score, 'Skin Texture', facialData.texture_anomaly)}
                  {renderScoreBar(facialData.lighting_score, 'Lighting Consistency')}
                </div>

                <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">Detection Method</h4>
                  <p className="text-sm text-gray-700">
                    Analysis performed using <strong>{facialData.method_used}</strong> for facial landmark detection
                  </p>
                </div>

                {(facialData.symmetry_anomaly || facialData.eye_anomaly || facialData.texture_anomaly) && (
                  <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h4 className="font-semibold text-yellow-800 mb-2">Suspicious Indicators</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
                      {facialData.symmetry_anomaly && <li>Unusual facial asymmetry detected</li>}
                      {facialData.eye_anomaly && <li>Eye region shows abnormal characteristics</li>}
                      {facialData.texture_anomaly && <li>Skin texture appears synthetic or edited</li>}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        </TabsContent>
      )}

      {metadataData && (
        <TabsContent value="metadata" className="space-y-6 p-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-xl font-semibold mb-2">Metadata Forensics</h3>
              <p className="text-gray-600 text-sm">
                EXIF data analysis and error level analysis (ELA) for compression artifacts
              </p>
            </div>

            {renderScoreBar(metadataData.score, 'Overall Metadata Score')}

            <div className="space-y-4 mt-6">
              {renderScoreBar(metadataData.exif_score, 'EXIF Authenticity', metadataData.exif_suspicious)}
              {renderScoreBar(metadataData.ela_score, 'ELA Score', metadataData.ela_anomalies)}
              {renderScoreBar(metadataData.compression_score, 'Compression Analysis')}
            </div>

            <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-3">EXIF Status</h4>
              {metadataData.exif_present ? (
                <div>
                  <p className="text-sm text-green-700 mb-3">EXIF data found</p>
                  {metadataData.metadata_details && Object.keys(metadataData.metadata_details).length > 0 ? (
                    <div className="space-y-1 text-sm">
                      {Object.entries(metadataData.metadata_details).slice(0, 8).map(([key, value]) => 
                        renderMetric(key, value)
                      )}
                      {Object.keys(metadataData.metadata_details).length > 8 && (
                        <div className="text-xs text-gray-500 pt-2">
                          + {Object.keys(metadataData.metadata_details).length - 8} more fields
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-gray-500">Limited metadata available</p>
                  )}
                </div>
              ) : (
                <div>
                  <p className="text-sm text-yellow-700">No EXIF data found</p>
                  <p className="text-xs text-gray-600 mt-2">
                    Missing EXIF data may indicate the file was processed, edited, or generated
                  </p>
                </div>
              )}
            </div>

            {metadataData.editing_software_detected && metadataData.editing_software_detected !== 'Unknown' && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Editing Software</h4>
                <p className="text-sm text-blue-800">
                  Detected: <strong>{metadataData.editing_software_detected}</strong>
                </p>
              </div>
            )}

            {metadataData.ela_anomalies && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-semibold text-yellow-800 mb-2">Compression Anomalies</h4>
                <p className="text-sm text-yellow-700">
                  Error Level Analysis detected inconsistent compression patterns, which may indicate 
                  localized editing or manipulation.
                </p>
              </div>
            )}
          </div>
        </TabsContent>
      )}

      <TabsContent value="report" className="space-y-6 p-6">
        <div className="space-y-4">
          <div>
            <h3 className="text-xl font-semibold mb-2">Detailed Analysis Report</h3>
            <p className="text-gray-600 text-sm">Complete technical findings and methodology</p>
          </div>

          <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                {results.report || 'No detailed report available'}
              </div>
            </div>
          </div>

          <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Raw JSON Data</h4>
            <pre className="text-xs text-blue-800 overflow-x-auto whitespace-pre-wrap font-mono">
              {JSON.stringify(results, null, 2)}
            </pre>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  )
}
