"use client"

import { useRef, useEffect, useState } from "react"
import { Brain, Activity, GitBranch, Mic, ScanFace, FileCode, Zap } from "lucide-react"
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

// Register ScrollTrigger plugin
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

const features = [
  {
    title: "Multi-Model Neural Ensemble",
    description: "4+ deep learning models vote on authenticity with aggressive confidence weighting",
    icon: Brain,
  },
  {
    title: "Frequency Domain Forensics",
    description: "FFT/DCT analysis detects GAN and diffusion model artifacts invisible to human eyes",
    icon: Activity,
  },
  {
    title: "Temporal Consistency Tracking",
    description: "Tracks facial landmarks and identity persistence across video frames to catch unnatural transitions",
    tag: "Video",
    icon: GitBranch,
  },
  {
    title: "Audio-Visual Synchronization",
    description: "Voice deepfake detection with lip-sync correlation analysis",
    tag: "Video",
    icon: Mic,
  },
  {
    title: "Facial Forensics",
    description: "Analyzes symmetry, eye quality, skin texture, and anatomical correctness",
    icon: ScanFace,
  },
  {
    title: "Metadata Intelligence",
    description: "EXIF data analysis and ELA compression forensics reveal editing history",
    icon: FileCode,
  },
  {
    title: "Real-Time Analysis",
    description: "Process thousands of images per minute via distributed edge network",
    icon: Zap,
  },
]

export function HorizontalScrollFeatures() {
  const sectionRef = useRef<HTMLDivElement>(null)
  const cardsContainerRef = useRef<HTMLDivElement>(null)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  useEffect(() => {
    if (isMobile || !sectionRef.current || !cardsContainerRef.current) return

    const section = sectionRef.current
    const cardsContainer = cardsContainerRef.current

    // Calculate total scroll distance needed
    const cardWidth = 380 + 24 // card width + gap
    const totalWidth = cardWidth * features.length
    const viewportWidth = window.innerWidth
    const scrollDistance = totalWidth - viewportWidth + 300 // extra padding

    // Create the horizontal scroll animation
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: section,
        pin: true,
        scrub: 1,
        start: "top top",
        end: () => `+=${scrollDistance * 2}`,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onEnter: () => {
          section.setAttribute('data-features-active', 'true');
        },
        onLeave: () => {
          section.setAttribute('data-features-active', 'false');
        },
        onEnterBack: () => {
          section.setAttribute('data-features-active', 'true');
        },
        onLeaveBack: () => {
          section.setAttribute('data-features-active', 'false');
        },
      }
    })

    tl.to(cardsContainer, {
      x: -scrollDistance,
      ease: "none"
    })

    // Cleanup
    return () => {
      ScrollTrigger.getAll().forEach(trigger => trigger.kill())
    }
  }, [isMobile])

  if (isMobile) {
    return (
      <section id="features" className="py-20 px-6">
        <div className="container max-w-7xl mx-auto space-y-12">
          <div className="space-y-4 max-w-xl">
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white">
              Advanced Detection <br />
              Features.
            </h2>
            <p className="text-slate-400 text-lg">
              Multi-layered analysis combining neural networks, signal processing, and biological verification.
            </p>
          </div>

          <div className="space-y-6">
            {features.map((feature, idx) => {
              const Icon = feature.icon
              return (
                <div
                  key={idx}
                  className="bg-white/[0.02] border border-white/10 rounded-2xl p-8 hover:bg-white/[0.04] transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className="text-white/60">
                      <Icon size={28} strokeWidth={1.5} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
                        {feature.tag && (
                          <span className="text-xs px-2 py-1 bg-white/10 text-white/70 rounded">
                            {feature.tag}
                          </span>
                        )}
                      </div>
                      <p className="text-slate-400 text-sm leading-relaxed">{feature.description}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>
    )
  }

  return (
    <section
      id="features"
      ref={sectionRef}
      className="relative h-screen overflow-hidden z-10"
    >
      <div className="h-screen flex items-center">
        <div className="w-full">
          <div className="container max-w-7xl mx-auto px-6 mb-12">
            <div className="space-y-4 max-w-xl">
              <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white">
                Advanced Detection <br />
                Features.
              </h2>
              <p className="text-slate-400 text-lg">
                Multi-layered analysis combining neural networks, signal processing, and biological verification.
              </p>
            </div>
          </div>

          <div className="overflow-hidden">
            <div
              ref={cardsContainerRef}
              className="flex gap-6 pl-6 md:pl-[calc((100vw-1280px)/2+1.5rem)]"
            >
              {features.map((feature, idx) => {
                const Icon = feature.icon
                return (
                  <div
                    key={idx}
                    className="group flex-shrink-0 w-[380px] bg-white/[0.02] border border-white/10 rounded-2xl p-8 hover:bg-white/[0.04] transition-colors relative overflow-hidden"
                  >
                    {/* Scanline effect */}
                    <div className="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent animate-scanline" />
                    </div>
                    
                    <div className="mb-6 relative">
                      <Icon size={32} className="text-white/60 transition-all duration-300 group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(34,211,238,0.6)]" strokeWidth={1.5} />
                      {/* Icon glitch layers */}
                      <Icon size={32} className="absolute top-0 left-0 text-red-500/40 opacity-0 group-hover:opacity-100 transition-opacity duration-75 group-hover:translate-x-[-2px] group-hover:translate-y-[-1px]" strokeWidth={1.5} />
                      <Icon size={32} className="absolute top-0 left-0 text-blue-500/40 opacity-0 group-hover:opacity-100 transition-opacity duration-75 group-hover:translate-x-[2px] group-hover:translate-y-[1px]" strokeWidth={1.5} />
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <h3 className="glitch-text text-2xl font-semibold text-white relative">
                          {feature.title}
                          <span className="glitch-text-layer" data-text={feature.title}></span>
                          <span className="glitch-text-layer" data-text={feature.title}></span>
                        </h3>
                        {feature.tag && (
                          <span className="text-xs px-2 py-1 bg-white/10 text-white/70 rounded group-hover:bg-cyan-500/20 group-hover:text-cyan-400 transition-colors">
                            {feature.tag}
                          </span>
                        )}
                      </div>
                      <p className="text-slate-400 text-base leading-relaxed group-hover:text-slate-300 transition-colors">{feature.description}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

<style jsx>{`
  @keyframes scanline {
    0% {
      transform: translateY(-100%);
    }
    100% {
      transform: translateY(100%);
    }
  }

  .animate-scanline {
    animation: scanline 2s ease-in-out infinite;
  }

  .glitch-text {
    position: relative;
    display: inline-block;
  }

  .glitch-text-layer {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    opacity: 0;
    pointer-events: none;
  }

  .glitch-text-layer::before {
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }

  .glitch-text-layer:nth-child(1)::before {
    color: #ff0000;
    z-index: -1;
  }

  .glitch-text-layer:nth-child(2)::before {
    color: #00ffff;
    z-index: -2;
  }

  .group:hover .glitch-text-layer {
    opacity: 0.8;
    animation: glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) infinite;
  }

  .group:hover .glitch-text-layer:nth-child(1) {
    animation-delay: 0s;
  }

  .group:hover .glitch-text-layer:nth-child(2) {
    animation-delay: 0.1s;
  }

  @keyframes glitch {
    0% {
      clip-path: inset(40% 0 61% 0);
      transform: translate(-2px, -2px);
    }
    20% {
      clip-path: inset(92% 0 1% 0);
      transform: translate(2px, 2px);
    }
    40% {
      clip-path: inset(43% 0 1% 0);
      transform: translate(-2px, 2px);
    }
    60% {
      clip-path: inset(25% 0 58% 0);
      transform: translate(2px, -2px);
    }
    80% {
      clip-path: inset(54% 0 7% 0);
      transform: translate(-2px, 2px);
    }
    100% {
      clip-path: inset(58% 0 43% 0);
      transform: translate(2px, -2px);
    }
  }
`}</style>
