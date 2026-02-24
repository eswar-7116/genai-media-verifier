"use client"

import { useEffect, useRef, useState } from 'react'
import Image from 'next/image'
import { Upload, FileImage, FileVideo, X } from 'lucide-react'

interface ProcessingSectionProps {
  file: File | null
  progress: string
  uploadProgress: number
  currentStage: string
  onCancel: () => void
}

export default function ProcessingSection({ file, progress, uploadProgress, currentStage, onCancel }: ProcessingSectionProps) {
  const [thumbnailUrl, setThumbnailUrl] = useState<string>('')
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    if (file) {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setThumbnailUrl(e.target?.result as string)
        }
        reader.readAsDataURL(file)
      } else if (file.type.startsWith('video/')) {
        const video = document.createElement('video')
        video.preload = 'metadata'
        video.onloadedmetadata = () => {
          video.currentTime = 0.5
        }
        video.onseeked = () => {
          const canvas = document.createElement('canvas')
          canvas.width = video.videoWidth
          canvas.height = video.videoHeight
          const ctx = canvas.getContext('2d')
          ctx?.drawImage(video, 0, 0, canvas.width, canvas.height)
          setThumbnailUrl(canvas.toDataURL())
        }
        video.src = URL.createObjectURL(file)
      }
    }

    setTimeout(() => setIsAnimating(true), 100)
  }, [file])
  
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      
      <div className={`relative w-full h-full z-10 transition-all duration-1000 ease-out ${isAnimating ? 'opacity-100' : 'opacity-0'}`}>
        <div className="grid grid-cols-1 lg:grid-cols-2 h-full">
          <div className={`transition-all duration-1000 flex items-center justify-center p-8 ${isAnimating ? 'translate-x-0' : '-translate-x-20'}`}>
            <div className="w-4/5 space-y-4">
              <div className="glass-card rounded-3xl p-8 border-neon-blue bg-white/[0.06]">
                <div className="text-center space-y-6 w-full">
                  {file?.type.startsWith('image/') ? (
                    <FileImage className="w-20 h-20 text-neon-blue mx-auto" />
                  ) : (
                    <FileVideo className="w-20 h-20 text-neon-blue mx-auto" />
                  )}
                  <div className="space-y-2">
                    <p className="text-2xl font-light text-white tracking-wide break-words px-2">{file?.name}</p>
                    <p className="text-sm text-white/50 tracking-widest uppercase">
                      {file ? (file.size / 1024 / 1024).toFixed(2) : '0'} MB
                    </p>
                  </div>
                  
                  <div className="pt-6 border-t border-white/10">
                    <div className="inline-flex items-center gap-3 px-6 py-3 bg-cyan-500/10 border border-cyan-500/30 rounded-full">
                      <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(0,243,255,0.8)]" />
                      <span className="text-sm text-cyan-400 tracking-wider uppercase font-light">
                        Processing
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={onCancel}
                className="w-full group relative px-6 py-4 glass-card border-red-500/30 bg-red-500/10 rounded-2xl overflow-hidden transition-all duration-300 hover:bg-red-500/20 hover:border-red-500/50 hover:-translate-y-1"
              >
                <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-red-500/20 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[500px] group-hover:h-[500px]" />
                <div className="relative z-10 flex items-center justify-center gap-3">
                  <X className="w-5 h-5 text-red-400" />
                  <span className="text-base font-light tracking-[2px] uppercase text-red-400">
                    Cancel Analysis
                  </span>
                </div>
              </button>
            </div>
          </div>

          <div className={`transition-all duration-1000 delay-300 flex items-center justify-center p-8 ${isAnimating ? 'translate-x-0 opacity-100' : 'translate-x-20 opacity-0'}`}>
            <div className="w-full space-y-6">
              {thumbnailUrl && (
                <div className="glass-card border-white/10 rounded-2xl p-6 backdrop-blur-xl">
                  <p className="text-xs font-light tracking-[2px] uppercase text-white/50 mb-4">
                    FILE PREVIEW
                  </p>
                  <div className="relative w-full aspect-video rounded-xl overflow-hidden bg-white/5 border border-white/10">
                    <Image
                      src={thumbnailUrl}
                      alt="File preview"
                      fill
                      className="object-contain"
                    />
                  </div>
                </div>
              )}

              <div className="glass-card border-white/10 rounded-2xl p-6 backdrop-blur-xl space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-light tracking-[2px] uppercase text-white/50">
                    PROGRESS
                  </p>
                  <p className="text-sm font-light text-cyan-400">
                    {Math.round(uploadProgress)}%
                  </p>
                </div>
                
                <div className="relative w-full h-2 bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500 ease-out rounded-full"
                    style={{ width: `${uploadProgress}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                  </div>
                </div>

                <div className="pt-2 border-t border-white/5">
                  <p className="text-xs font-light tracking-[2px] uppercase text-white/30 mb-2">
                    CURRENT STAGE
                  </p>
                  <p className="text-sm text-white/70 font-light animate-pulse">
                    {currentStage || 'Initializing...'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </section>
  )
}
