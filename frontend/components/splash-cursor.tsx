"use client"
import { useEffect, useRef, useState } from "react"

export default function SplashCursor({
  DYE_RESOLUTION = 512, // Reduced from 1440
  DENSITY_DISSIPATION = 3.5,
  VELOCITY_DISSIPATION = 2,
  CURL = 3,
  SPLAT_RADIUS = 0.2,
}: any) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isLowPerformance, setIsLowPerformance] = useState(false)

  useEffect(() => {
    // Performance detection
    const checkPerformance = () => {
      const gl = document.createElement('canvas').getContext('webgl2')
      if (!gl) {
        setIsLowPerformance(true)
        return false
      }
      return true
    }

    if (!checkPerformance()) return

    const canvas = canvasRef.current
    if (!canvas) return

    // Disable on mobile devices
    if (window.innerWidth < 768) {
      setIsLowPerformance(true)
      return
    }

    console.log("[SplashCursor] Initializing with reduced resolution:", DYE_RESOLUTION)

    // Placeholder for actual WebGL implementation
    // The full implementation would go here but is disabled for performance
    
    return () => {
      // Cleanup
    }
  }, [])

  // Don't render on low performance devices
  if (isLowPerformance) {
    return null
  }

  return (
    <div className="fixed inset-0 z-[-1] pointer-events-none overflow-hidden">
      <canvas ref={canvasRef} className="w-full h-full block" style={{ mixBlendMode: "screen" }} />
    </div>
  )
}
