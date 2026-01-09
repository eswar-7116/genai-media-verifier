"use client"

import { Button } from "@/components/ui/button"
import { Github, Linkedin } from "lucide-react"
import dynamic from 'next/dynamic'
import HeroSection from "@/components/hero-section"

// Global background effects - loaded once for entire page
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

// Lazy load heavy components
const HorizontalScrollFeatures = dynamic(
  () => import("@/components/ui/horizontal-scroll-features").then(mod => ({ default: mod.HorizontalScrollFeatures })),
  { ssr: false }
)

export default function Home() {

  return (
    <main className="min-h-screen bg-black text-white selection:bg-cyan-500/30 overflow-x-hidden font-sans">
      {/* Global background effects - single instances for entire page */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <AnoAI className="opacity-90" />
        <SnowParticles quantity={80} />
      </div>

      {/* HERO SECTION */}
      <HeroSection />

      {/* FEATURES SECTION - HORIZONTAL SCROLL */}
      <HorizontalScrollFeatures />

      <section id="demo" className="relative py-20 px-6 bg-[#050505] overflow-hidden z-10">
        <div className="container max-w-6xl mx-auto text-center space-y-16">
          <div className="space-y-4">
            <h2 className="text-4xl font-bold">Built for Innovation and Trust.</h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Watch how our platform simplifies the complex workflow of digital content verification.
            </p>
          </div>

          <div className="relative aspect-video rounded-3xl overflow-hidden border border-white/5 bg-slate-900 shadow-[0_0_100px_rgba(0,0,0,1)] group cursor-pointer">
            <video
              className="w-full h-full object-cover"
              controls
              muted
              loop
              playsInline
              preload="metadata"
            >
              <source src="/demo-vid.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        </div>
      </section>


      <section id="team" className="relative py-20 px-6 overflow-hidden z-10">
        <div className="container max-w-7xl mx-auto space-y-20">
          <div className="max-w-2xl">
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-neon-blue">Core Team</h2>
            <p className="text-slate-400 text-lg">
              Meet the developers and researchers dedicated to preserving digital truth.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { 
                name: "Faizan", 
                role: "Lead Engineer", 
                img: "/images/faizan.png",
                github: "https://github.com/Shaik-Faizan-Ahmed",
                linkedin: "https://www.linkedin.com/in/faizan-ahmed-shaik/"
              },
              { 
                name: "Vallabha", 
                role: "AI Architecture", 
                img: "/images/vallabha.png",
                github: "http://github.com/vallabhatech",
                linkedin: "http://linkedin.com/in/vallabha-tech"
              },
              { 
                name: "Gurunanda", 
                role: "Product Design", 
                img: "/images/gurunanda.png",
                github: "https://github.com/Gurunanda-2006",
                linkedin: "https://www.linkedin.com/in/punna-gurunanda-653432312/"
              },
              { 
                name: "Eswar Dudi", 
                role: "Backend Architect", 
                img: "/images/eswar.png",
                github: "https://github.com/eswar-7116",
                linkedin: "https://www.linkedin.com/in/eswar-dudi/"
              },
              { 
                name: "Mohammad Rayhaanuddin", 
                role: "Tester", 
                img: "/images/rayhaan.png",
                github: "https://github.com/Rayhaan1905",
                linkedin: "https://www.linkedin.com/in/rayhaan-uddin-22a273322/"
              },
              { 
                name: "Teja Dasarla", 
                role: "Networking", 
                img: "/images/teja.png",
                github: "https://github.com/tejadasarla",
                linkedin: "https://www.linkedin.com/in/teja-dasarla-4b5647308/"
              },
            ].map((member, idx) => (
              <div
                key={idx}
                className="group relative rounded-3xl glass-card border-white/5 transition-all duration-500 aspect-[4/5] flex flex-col"
              >
                <div className="h-130 relative flex-1">
                  <div className="absolute inset-0 rounded-3xl overflow-hidden z-0">
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-80" />
                  </div>
                  <img
                    src={member.img || "/placeholder.svg"}
                    alt={member.name}
                    loading="lazy"
                    className="w-full h-full object-cover object-top rounded-3xl transition-transform duration-500 ease-out group-hover:scale-110 origin-bottom relative z-10"
                  />
                </div>
                <div className="p-8 absolute bottom-0 left-0 w-full z-20 bg-gradient-to-t from-black to-transparent pt-20 rounded-b-3xl">
                  <h3 className="text-3xl font-bold mb-1 tracking-tight text-white">{member.name}</h3>
                  <p className="text-cyan-400 font-bold mb-6">{member.role}</p>
                  <div className="flex gap-4 opacity-60 group-hover:opacity-100 transition-opacity">
                    <a href={member.github} target="_blank" rel="noopener noreferrer">
                      <Github className="w-5 h-5 hover:text-white cursor-pointer transition-colors" />
                    </a>
                    <a href={member.linkedin} target="_blank" rel="noopener noreferrer">
                      <Linkedin className="w-5 h-5 hover:text-white cursor-pointer transition-colors" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION 5: FOOTER (Clean/Minimal) */}
      <footer className="py-24 px-6 border-t border-white/5 bg-black">
        <div className="container max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-20">
            <div className="space-y-8">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <img src="/new-logo.jpeg" alt="AI Analyzer Logo" className="w-8 h-8 object-contain" loading="lazy" />
                V.E.R.I.T.A.S
              </h2>
              <p className="text-slate-500 text-sm max-w-xs leading-relaxed">
                Helping people make informed judgments about digital media.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-10">
              <div className="space-y-6">
                <h4 className="text-sm font-bold text-white uppercase tracking-widest">Resources</h4>
                <ul className="space-y-4 text-sm text-slate-500">
                  <li className="hover:text-white cursor-pointer transition-colors">Documentation</li>
                  <li className="hover:text-white cursor-pointer transition-colors">API Reference</li>
                  <li className="hover:text-white cursor-pointer transition-colors">Security</li>
                </ul>
              </div>
              <div className="space-y-6">
                <h4 className="text-sm font-bold text-white uppercase tracking-widest">Company</h4>
                <ul className="space-y-4 text-sm text-slate-500">
                  <li className="hover:text-white cursor-pointer transition-colors">About</li>
                  <li className="hover:text-white cursor-pointer transition-colors">Careers</li>
                  <li className="hover:text-white cursor-pointer transition-colors">Contact</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="mt-24 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4 text-slate-600 text-xs font-medium">
            <p>© 2026 V.E.R.I.T.A.S — Media analysis to support informed judgment.</p>
            <div className="flex gap-8">
              <span className="hover:text-white cursor-pointer transition-colors">Privacy</span>
              <span className="hover:text-white cursor-pointer transition-colors">Terms</span>
              <span className="hover:text-white cursor-pointer transition-colors">Cookies</span>
            </div>
          </div>
        </div>
      </footer>


    </main>
  )
}
