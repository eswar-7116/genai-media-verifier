"use client"

import { useCallback, useState } from 'react'
import { Upload, FileImage, FileVideo, Zap, Shield, AlertTriangle } from 'lucide-react'

type AnalysisMode = 'quick' | 'deep'

interface UploadSectionProps {
  file: File | null
  onFileSelect: (file: File) => void
  onAnalyze: (mode: AnalysisMode) => void
  disabled: boolean
  error: string | null
}

const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/bmp', 'image/webp']
const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska']
const MAX_FILE_SIZE = 50 * 1024 * 1024

export default function UploadSection({ 
  file, 
  onFileSelect, 
  onAnalyze, 
  disabled,
  error 
}: UploadSectionProps) {
  const [showQuickWarning, setShowQuickWarning] = useState(false)
  
  const validateFile = (file: File): string | null => {
    if (file.size > MAX_FILE_SIZE) {
      return 'File size exceeds 50MB limit'
    }

    const isValidImage = ALLOWED_IMAGE_TYPES.includes(file.type)
    const isValidVideo = ALLOWED_VIDEO_TYPES.includes(file.type)

    if (!isValidImage && !isValidVideo) {
      return 'Unsupported file format'
    }

    return null
  }

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      const error = validateFile(droppedFile)
      if (error) {
        alert(error)
        return
      }
      onFileSelect(droppedFile)
    }
  }, [onFileSelect])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      const error = validateFile(selectedFile)
      if (error) {
        alert(error)
        return
      }
      onFileSelect(selectedFile)
    }
  }

  const handleQuickAnalysis = () => {
    setShowQuickWarning(true)
  }

  const confirmQuickAnalysis = () => {
    setShowQuickWarning(false)
    onAnalyze('quick')
  }

  const isVideoFile = file && file.type.startsWith('video/')

  return (
    <>
      <section className="relative flex items-center justify-center px-6 overflow-hidden h-screen">
        <div className="absolute inset-0 bg-grid opacity-20" />
        
        <div className="relative w-full max-w-3xl space-y-6 z-10">
          <div className="text-center space-y-2 animate-fade-in-up">
            <p className="text-xs font-light tracking-[3px] uppercase text-white/50">
              AI-POWERED VERIFICATION
            </p>
            <h1 className="text-4xl md:text-5xl font-light tracking-[8px] text-white uppercase">
              ANALYZE
            </h1>
            <p className="text-white/60 text-sm tracking-wide">
              Upload media for comprehensive authenticity analysis
            </p>
          </div>

          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className={`
              group relative glass-card rounded-3xl p-10
              transition-all duration-500
              ${disabled 
                ? 'opacity-50 cursor-not-allowed' 
                : 'cursor-pointer hover:bg-white/[0.08] hover:border-white/20'
              }
              ${file ? 'border-neon-blue bg-white/[0.06]' : 'border-white/10'}
              animate-fade-in-up
              [animation-delay:0.2s]
              [animation-fill-mode:forwards]
              opacity-0
            `}
            style={{ animationDelay: '0.2s' }}
          >
            <input
              type="file"
              id="file-input"
              className="hidden"
              accept={[...ALLOWED_IMAGE_TYPES, ...ALLOWED_VIDEO_TYPES].join(',')}
              onChange={handleFileInput}
              disabled={disabled}
            />
            
            <label 
              htmlFor="file-input" 
              className="flex flex-col items-center justify-center cursor-pointer"
            >
              {file ? (
                <div className="text-center space-y-3">
                  {file.type.startsWith('image/') ? (
                    <FileImage className="w-14 h-14 text-neon-blue mx-auto animate-pulse" />
                  ) : (
                    <FileVideo className="w-14 h-14 text-neon-blue mx-auto animate-pulse" />
                  )}
                  <div className="space-y-1">
                    <p className="text-lg font-light text-white tracking-wide">{file.name}</p>
                    <p className="text-xs text-white/50 tracking-widest uppercase">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center space-y-5">
                  <Upload className="w-14 h-14 text-white/30 mx-auto group-hover:text-white/50 transition-colors duration-500" />
                  <div className="space-y-2">
                    <p className="text-base font-light text-white/70 tracking-wide">
                      Drag & drop media file
                    </p>
                    <p className="text-xs text-white/40 tracking-widest uppercase">or</p>
                    <div className="inline-block px-6 py-2 border border-white/20 bg-white/[0.05] backdrop-blur-[10px] text-white/80 text-xs tracking-[2px] uppercase hover:bg-white/[0.12] hover:border-white/35 transition-all duration-300">
                      Browse Files
                    </div>
                  </div>
                </div>
              )}
            </label>

            {!file && (
              <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent h-32 animate-scan" />
              </div>
            )}
          </div>

          <div 
            className="text-center space-y-1 animate-fade-in-up opacity-0"
            style={{ animationDelay: '0.4s', animationFillMode: 'forwards' }}
          >
            <div className="flex items-center justify-center gap-6 text-xs text-white/40 tracking-widest uppercase">
              <span>JPG • PNG • BMP • WEBP</span>
              <span className="text-white/20">|</span>
              <span>MP4 • AVI • MOV • MKV</span>
            </div>
            <p className="text-[10px] text-white/30 tracking-wider">Maximum file size: 50 MB</p>
          </div>

          {error && (
            <div className="glass-card border-red-500/30 bg-red-500/10 rounded-2xl p-3 text-red-400 text-center tracking-wide animate-fade-in-up text-sm">
              {error}
            </div>
          )}

          {file && (
            <div 
              className="flex flex-col gap-4 animate-fade-in-up opacity-0"
              style={{ animationDelay: '0.6s', animationFillMode: 'forwards' }}
            >
              {!isVideoFile && (
                <div className="flex justify-center">
                  <button
                    onClick={() => onAnalyze('deep')}
                    disabled={disabled}
                    className="group relative px-12 py-5 glass-card border-neon-blue overflow-hidden transition-all duration-300 hover:bg-cyan-500/10 hover:border-cyan-400 hover:-translate-y-1 hover:shadow-[0_0_30px_rgba(0,243,255,0.3)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
                  >
                    <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-cyan-500/20 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[500px] group-hover:h-[500px]" />
                    <div className="relative z-10 space-y-1">
                      <p className="text-lg font-light tracking-[3px] uppercase text-white">Begin Analysis</p>
                      <p className="text-[10px] text-white/50 tracking-wider uppercase">Comprehensive Multi-Layer Detection</p>
                    </div>
                  </button>
                </div>
              )}

              {isVideoFile && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <button
                      onClick={handleQuickAnalysis}
                      disabled={disabled}
                      className="group relative px-6 py-5 glass-card border-yellow-500/40 overflow-hidden transition-all duration-300 hover:bg-yellow-500/10 hover:border-yellow-400 hover:-translate-y-1 hover:shadow-[0_0_30px_rgba(255,200,0,0.3)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
                    >
                      <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-yellow-500/20 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[500px] group-hover:h-[500px]" />
                      <div className="relative z-10 space-y-2">
                        <Zap className="w-6 h-6 text-yellow-400 mx-auto" />
                        <p className="text-sm font-light tracking-[2px] uppercase text-white">Quick Analysis</p>
                        <p className="text-[9px] text-white/50 tracking-wider uppercase">Faster • Less Accurate</p>
                      </div>
                    </button>

                    <button
                      onClick={() => onAnalyze('deep')}
                      disabled={disabled}
                      className="group relative px-6 py-5 glass-card border-neon-blue overflow-hidden transition-all duration-300 hover:bg-cyan-500/10 hover:border-cyan-400 hover:-translate-y-1 hover:shadow-[0_0_30px_rgba(0,243,255,0.3)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
                    >
                      <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-cyan-500/20 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[500px] group-hover:h-[500px]" />
                      <div className="relative z-10 space-y-2">
                        <Shield className="w-6 h-6 text-cyan-400 mx-auto" />
                        <p className="text-sm font-light tracking-[2px] uppercase text-white">Begin Analysis</p>
                        <p className="text-[9px] text-white/50 tracking-wider uppercase">Comprehensive • Recommended</p>
                      </div>
                    </button>
                  </div>
                  <p className="text-center text-[10px] text-white/40 tracking-wider">
                    Choose your analysis mode
                  </p>
                </>
              )}
            </div>
          )}
        </div>

        <style jsx>{`
          @keyframes scan {
            0% { top: -10%; }
            100% { top: 110%; }
          }
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(30px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          .animate-fade-in-up {
            animation: fadeInUp 0.8s ease forwards;
          }
          .animate-scan {
            animation: scan 3s ease-in-out infinite;
          }
        `}</style>
      </section>

      {showQuickWarning && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="relative glass-card border-yellow-500/40 rounded-2xl p-8 max-w-md w-full space-y-6 animate-scale-in">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-8 h-8 text-yellow-400 flex-shrink-0 animate-pulse" />
              <div className="space-y-2">
                <h3 className="text-xl font-light tracking-[2px] uppercase text-white">
                  Quick Analysis Mode
                </h3>
                <p className="text-sm text-white/70 leading-relaxed">
                  By choosing this option, the analysis will be <strong className="text-yellow-400">faster but potentially less accurate</strong>.
                </p>
                <div className="space-y-1 text-xs text-white/50">
                  <p>• Skips physiological analysis</p>
                  <p>• Skips physics consistency checks</p>
                  <p>• Skips specialized detection layers</p>
                </div>
                <p className="text-xs text-yellow-400/80 pt-2">
                  For best results, we recommend using comprehensive analysis.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowQuickWarning(false)}
                className="flex-1 px-4 py-3 glass-card border-white/20 text-white/80 text-sm tracking-wider uppercase hover:bg-white/10 transition-all duration-300"
              >
                Cancel
              </button>
              <button
                onClick={confirmQuickAnalysis}
                className="flex-1 px-4 py-3 glass-card border-yellow-500/40 bg-yellow-500/10 text-yellow-400 text-sm tracking-wider uppercase hover:bg-yellow-500/20 hover:border-yellow-400 transition-all duration-300"
              >
                Continue
              </button>
            </div>
          </div>
          
          <style jsx>{`
            @keyframes fade-in {
              from { opacity: 0; }
              to { opacity: 1; }
            }
            @keyframes scale-in {
              from {
                opacity: 0;
                transform: scale(0.9);
              }
              to {
                opacity: 1;
                transform: scale(1);
              }
            }
            .animate-fade-in {
              animation: fade-in 0.3s ease forwards;
            }
            .animate-scale-in {
              animation: scale-in 0.4s ease forwards;
            }
          `}</style>
        </div>
      )}
    </>
  )
}
