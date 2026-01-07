"use client"

import { useState, useRef, useEffect } from 'react'
import dynamic from 'next/dynamic'
import UploadSection from '@/components/upload/upload-section'
import ProcessingSection from '@/components/upload/processing-section'
import ResultsDashboard from '@/components/upload/results-dashboard'

// Dynamic imports for background effects
const AnoAI = dynamic(() => import("@/components/ui/animated-shader-background"), { 
  ssr: false,
  loading: () => (
    <div className="fixed inset-0 z-0 bg-gradient-to-br from-slate-900/50 to-transparent" />
  )
})

const SnowParticles = dynamic(
  () => import("@/components/ui/snow-particles").then(mod => ({ default: mod.SnowParticles })),
  { ssr: false }
)

type AnalysisState = 'idle' | 'uploading' | 'processing' | 'complete' | 'error'
type AnalysisMode = 'quick' | 'deep'
type FileType = 'image' | 'video'

export default function UploadPage() {
  const [state, setState] = useState<AnalysisState>('idle')
  const [mode, setMode] = useState<AnalysisMode | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [fileType, setFileType] = useState<FileType | null>(null)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<string>('')
  const [progressMessages, setProgressMessages] = useState<string[]>([])
  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [currentStage, setCurrentStage] = useState<string>('')
  const resultsRef = useRef<HTMLDivElement>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const isAnalyzingRef = useRef<boolean>(false)

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile)
    setError(null)
    
    const type = selectedFile.type.startsWith('image/') ? 'image' : 'video'
    setFileType(type)
  }

  // Helper function to parse stage from message and calculate progress
  const getStageFromMessage = (message: string): { stage: string; progress: number } => {
    console.log('Processing message:', message)
    
    // File uploaded
    if (message.includes('uploaded') || message.includes('Starting')) {
      return { stage: 'Initializing', progress: 5 }
    }
    
    // Layer 1 - Metadata
    if (message.includes('LAYER 1') || message.includes('Metadata')) {
      if (message.includes('score')) {
        return { stage: 'Layer 1: Metadata Complete', progress: 15 }
      }
      return { stage: 'Layer 1: Analyzing Metadata', progress: 10 }
    }
    
    // Layer 2A - Frame extraction
    if (message.includes('LAYER 2A') && message.includes('Extracting')) {
      return { stage: 'Layer 2A: Extracting Frames', progress: 20 }
    }
    if (message.includes('Extracted') && message.includes('frames')) {
      return { stage: 'Layer 2A: Frames Ready', progress: 25 }
    }
    
    // Layer 2A - Frame analysis with progress
    if (message.includes('Analyzing frames')) {
      return { stage: 'Layer 2A: Analyzing Frames', progress: 30 }
    }
    if (message.includes('Processed')) {
      const match = message.match(/(\d+)\/(\d+)/)
      if (match) {
        const current = parseInt(match[1])
        const total = parseInt(match[2])
        const frameProgress = 30 + (current / total) * 15
        return { stage: `Layer 2A: Processing Frames ${current}/${total}`, progress: frameProgress }
      }
      return { stage: 'Layer 2A: Processing Frames', progress: 35 }
    }
    if (message.includes('Average score') || message.includes('Highest')) {
      return { stage: 'Layer 2A: Frame Analysis Complete', progress: 45 }
    }
    
    // Layer 2A - Temporal
    if (message.includes('Temporal')) {
      if (message.includes('Score')) {
        return { stage: 'Layer 2A: Temporal Complete', progress: 52 }
      }
      return { stage: 'Layer 2A: Temporal Analysis', progress: 48 }
    }
    
    // Layer 2A - 3D Model
    if (message.includes('3D Model')) {
      if (message.includes('Score')) {
        return { stage: 'Layer 2A: 3D Model Complete', progress: 60 }
      }
      return { stage: 'Layer 2A: 3D Video Model', progress: 55 }
    }
    
    // Layer 2B - Audio
    if (message.includes('LAYER 2B')) {
      if (message.includes('No audio')) {
        return { stage: 'Layer 2B: Audio Skipped', progress: 65 }
      }
      if (message.includes('Score')) {
        return { stage: 'Layer 2B: Audio Complete', progress: 68 }
      }
      return { stage: 'Layer 2B: Analyzing Audio', progress: 63 }
    }
    
    // Layer 2C - Physiological
    if (message.includes('LAYER 2C') || message.includes('Physiological')) {
      if (message.includes('Heartbeat')) {
        return { stage: 'Layer 2C: Physiological Complete', progress: 75 }
      }
      return { stage: 'Layer 2C: Physiological Signals', progress: 72 }
    }
    
    // Layer 2D - Physics
    if (message.includes('LAYER 2D') || message.includes('Physics')) {
      if (message.includes('Score')) {
        return { stage: 'Layer 2D: Physics Complete', progress: 80 }
      }
      return { stage: 'Layer 2D: Physics Check', progress: 78 }
    }
    
    // Layer 3 - Boundary
    if (message.includes('LAYER 3') && message.includes('boundaries')) {
      return { stage: 'Layer 3: Boundary Analysis', progress: 83 }
    }
    if (message.includes('Suspicious transitions')) {
      return { stage: 'Layer 3: Boundary Complete', progress: 86 }
    }
    
    // Layer 3 - Compression
    if (message.includes('LAYER 3') && message.includes('compression')) {
      return { stage: 'Layer 3: Compression Analysis', progress: 89 }
    }
    if (message.includes('Compression mismatches')) {
      return { stage: 'Layer 3: Compression Complete', progress: 92 }
    }
    
    // Final fusion
    if (message.includes('Combining')) {
      return { stage: 'Finalizing Analysis', progress: 95 }
    }
    
    // Complete
    if (message.includes('complete') || message.includes('Complete') || message.includes('Final Score')) {
      return { stage: 'Analysis Complete', progress: 100 }
    }
    
    // Default - keep current progress
    return { stage: message, progress: uploadProgress }
  }

  // Pre-connect to SSE on page load for deep scan mode
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    console.log('Setting up SSE connection on page load...')
    const eventSource = new EventSource(`${apiUrl}/analyze/progress`)
    eventSourceRef.current = eventSource
    
    eventSource.onopen = () => {
      console.log('SSE connection established and ready')
    }
    
    eventSource.onmessage = (event) => {
      console.log('SSE message received:', event.data)
      
      // Only process messages if we're currently analyzing
      if (!isAnalyzingRef.current) {
        console.log('Ignoring SSE message - not currently analyzing')
        return
      }
      
      try {
        const data = JSON.parse(event.data)
        if (data.message) {
          console.log('Raw message:', data.message)
          
          // Parse stage and progress
          const { stage, progress } = getStageFromMessage(data.message)
          
          console.log('Parsed - Stage:', stage, 'Progress:', progress)
          
          // Only update if progress is moving forward (prevents jumping back)
          setUploadProgress(prev => {
            // Always allow progress to increase
            if (progress > prev) {
              return progress
            }
            // If it's the same stage but lower progress, keep current
            return prev
          })
          
          setProgressMessages(prev => [...prev, data.message])
          setProgress(data.message)
          setCurrentStage(stage)
        }
      } catch (e) {
        console.error('Error parsing SSE message:', e)
      }
    }
    
    eventSource.onerror = (error) => {
      console.log('SSE error or connection closed:', error)
      // Don't close here, will reconnect automatically
    }
    
    // Cleanup on unmount
    return () => {
      console.log('Cleaning up SSE connection...')
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [])

  const handleAnalyze = async (selectedMode: AnalysisMode) => {
    if (!file || !fileType) return

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    // Clear all previous progress
    setProgress('')
    setProgressMessages([])
    setUploadProgress(0)
    setCurrentStage('')
    
    setMode(selectedMode)
    setState('uploading')
    
    // Enable SSE message processing
    isAnalyzingRef.current = true
    
    // Small delay to ensure state is cleared before starting
    await new Promise(resolve => setTimeout(resolve, 100))
    
    setProgress('Uploading file...')
    setProgressMessages(['Uploading file...'])
    setUploadProgress(5)
    setCurrentStage('Uploading file...')

    try {
      const formData = new FormData()
      formData.append('file', file)

      let endpoint = ''
      if (fileType === 'image') {
        endpoint = selectedMode === 'quick' ? '/analyze/image' : '/analyze/image/comprehensive'
      } else {
        endpoint = selectedMode === 'quick' ? '/analyze/video' : '/analyze/video/comprehensive'
      }

      setState('processing')
      
      let progressInterval: NodeJS.Timeout | null = null
      
      if (selectedMode === 'deep') {
        // SSE is already connected from useEffect, just log
        console.log('Using pre-connected SSE for progress updates')
        console.log('Starting analysis request...')
      } else {
        // For quick scan, simulate progress
        const progressSteps = [
          { msg: 'Uploading file...', progress: 10 },
          { msg: fileType === 'video' ? 'Extracting frames...' : 'Processing image...', progress: 25 },
          { msg: 'Analyzing neural patterns...', progress: 40 },
          { msg: 'Checking frequency domain...', progress: 55 },
          { msg: 'Scanning facial landmarks...', progress: 70 },
          { msg: 'Examining metadata...', progress: 85 },
          { msg: 'Generating report...', progress: 95 }
        ]

        let stepIndex = 0
        progressInterval = setInterval(() => {
          if (stepIndex < progressSteps.length) {
            const step = progressSteps[stepIndex]
            setProgress(step.msg)
            setCurrentStage(step.msg)
            setProgressMessages(prev => [...prev, step.msg])
            setUploadProgress(step.progress)
            stepIndex++
          }
        }, 1500)
      }

      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        body: formData,
      })

      if (progressInterval) {
        clearInterval(progressInterval)
      }

      setUploadProgress(100)
      setCurrentStage('Analysis Complete!')

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const data = await response.json()
      setResults(data)
      setState('complete')
      
      // Disable SSE message processing
      isAnalyzingRef.current = false
      
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }, 300)

    } catch (err) {
      setState('error')
      setError(err instanceof Error ? err.message : 'Analysis failed')
      setUploadProgress(0)
      // Disable SSE message processing on error
      isAnalyzingRef.current = false
    }
  }

  const handleReset = () => {
    setState('idle')
    setMode(null)
    setFile(null)
    setFileType(null)
    setResults(null)
    setError(null)
    setProgress('')
    setProgressMessages([])
    setUploadProgress(0)
    setCurrentStage('')
    isAnalyzingRef.current = false
    
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = () => {
    setState('idle')
    setMode(null)
    setFile(null)
    setFileType(null)
    setResults(null)
    setError(null)
    setProgress('')
    setProgressMessages([])
    setUploadProgress(0)
    setCurrentStage('')
    isAnalyzingRef.current = false
    
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <main className="min-h-screen bg-black text-white selection:bg-cyan-500/30 overflow-x-hidden font-sans">
      {/* Global background effects */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <AnoAI className="opacity-90" />
        <SnowParticles quantity={80} />
      </div>

      {/* Noise texture overlay */}
      <div 
        className="fixed inset-0 pointer-events-none z-[9999] opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Content */}
      <div className="relative z-10">
        {/* Upload Section - Always visible in idle state */}
        {state === 'idle' && (
          <UploadSection
            file={file}
            onFileSelect={handleFileSelect}
            onAnalyze={handleAnalyze}
            disabled={state !== 'idle'}
            error={error}
          />
        )}

        {/* Processing Section - Shows during upload/processing */}
        {(state === 'uploading' || state === 'processing' || state === 'complete') && (
          <ProcessingSection 
            file={file}
            progress={progressMessages.join('\n')}
            uploadProgress={uploadProgress}
            currentStage={currentStage}
            onCancel={handleCancel}
          />
        )}

        {/* Results Section - Appears below processing section */}
        {state === 'complete' && results && (
          <div ref={resultsRef}>
            <ResultsDashboard
              results={results}
              fileType={fileType!}
              mode={mode!}
              onReset={handleReset}
            />
          </div>
        )}
      </div>
    </main>
  )
}
