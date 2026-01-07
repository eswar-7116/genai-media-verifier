'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';

const AnoAI = dynamic(() => import("@/components/ui/animated-shader-background"), { ssr: false });
const SnowParticles = dynamic(() => import("@/components/ui/snow-particles").then(mod => ({ default: mod.SnowParticles })), { ssr: false });

export default function LearnPage() {
  const router = useRouter();
  const sectionsRef = useRef<(HTMLElement | null)[]>([]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('section-visible');
          }
        });
      },
      { threshold: 0.3 }
    );

    sectionsRef.current.forEach((section) => {
      if (section) observer.observe(section);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <main className="bg-black text-white overflow-x-hidden">
      <style jsx global>{`
        html {
          scroll-snap-type: y mandatory;
          scroll-behavior: smooth;
        }

        .snap-section {
          scroll-snap-align: start;
          scroll-snap-stop: always;
        }

        .section-content {
          opacity: 0;
          transform: translateY(30px);
          transition: opacity 0.8s ease, transform 0.8s ease;
        }

        .section-visible .section-content {
          opacity: 1;
          transform: translateY(0);
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
      `}</style>

      {/* HERO SECTION */}
      <section
        ref={(el) => { sectionsRef.current[0] = el; }}
        className="snap-section flex h-screen w-screen relative bg-gradient-to-br from-black via-[#0a0a0f] to-black overflow-hidden"
      >
        {/* Noise texture overlay */}
        <div 
          className="fixed inset-0 pointer-events-none z-[9999] opacity-[0.03]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          }}
        />

        {/* Left Side - Video */}
        <div className="flex-1 relative overflow-hidden flex items-center justify-center p-12 z-50">
          <video 
            className="w-[80%] h-[80%] object-cover rounded-2xl shadow-2xl z-50"
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
          >
            <source src="/Unsettling_Glitched_Face_Video_Generation.mp4" type="video/mp4" />
          </video>
          
          {/* Vertical divider line */}
          <div className="absolute right-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
        </div>

        {/* Right Side - Content */}
        <div className="flex-1 flex items-center justify-center p-[60px] relative">
          <div className="max-w-[520px] relative z-10 -translate-y-[20px] section-content">
            <p className="text-sm font-light tracking-[3px] uppercase text-white/50 mb-6">
              DEEPFAKE DETECTION
            </p>

            <h1 className="text-[72px] font-normal tracking-[8px] leading-tight mb-8 text-white uppercase">
              Learn to Spot Deepfakes
            </h1>

            <p className="text-[17px] font-light text-white/60 mb-6 tracking-[0.5px]">
              How V.E.R.I.T.A.S analyzes images and videos — and how you can recognize similar signs yourself.
            </p>

            <p className="text-[14px] font-light text-white/40 tracking-[0.5px]">
              You don't need to be an expert. Many deepfakes reveal themselves through subtle clues.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 1 - FACIAL DETAILS */}
      <section
        ref={(el) => { sectionsRef.current[1] = el; }}
        className="snap-section flex h-screen w-screen relative bg-black overflow-hidden"
      >
        <div className="flex-1 relative overflow-hidden flex items-center justify-center p-12 z-50">
          <img 
            src="/section1.jpg"
            alt="Facial Analysis"
            className="w-[75%] h-[75%] object-cover rounded-2xl shadow-2xl z-50"
          />
          <div className="absolute right-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
        </div>

        <div className="flex-1 flex items-center justify-center p-[60px] relative">
          <div className="max-w-[520px] relative z-10 section-content">
            <h2 className="text-[48px] font-normal tracking-[4px] leading-tight mb-8 text-white">
              Study the Face Closely
            </h2>

            <p className="text-[17px] font-light text-white/70 mb-8 leading-relaxed">
              Deepfakes often struggle with fine facial details. Skin may appear unnaturally smooth, facial proportions can feel slightly off, and features like the eyes or mouth may lack natural variation.
            </p>

            <p className="text-[17px] font-light text-white/70 mb-10 leading-relaxed">
              These inconsistencies are subtle, but when viewed carefully, they often stand out.
            </p>

            <div className="border-l-2 border-cyan-500/50 pl-6">
              <p className="text-[14px] font-medium text-cyan-400 mb-2 tracking-[1px] uppercase">
                How V.E.R.I.T.A.S checks this:
              </p>
              <p className="text-[15px] font-light text-white/60 leading-relaxed">
                We analyze facial landmarks, symmetry, eye quality, and texture consistency to detect signs of manipulation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2 - MOTION & IDENTITY */}
      <section
        ref={(el) => { sectionsRef.current[2] = el; }}
        className="snap-section flex h-screen w-screen relative bg-black overflow-hidden"
      >
        <div className="flex-1 flex items-center justify-center p-[60px] relative">
          <div className="max-w-[520px] relative z-10 section-content">
            <h2 className="text-[48px] font-normal tracking-[4px] leading-tight mb-8 text-white">
              Watch How the Face Moves
            </h2>

            <p className="text-[17px] font-light text-white/70 mb-8 leading-relaxed">
              In manipulated videos, faces may lag behind head movement, shift unnaturally, or subtly change identity across frames. These motion inconsistencies are difficult for synthetic models to maintain over time.
            </p>

            <p className="text-[17px] font-light text-white/70 mb-10 leading-relaxed">
              Watching how expressions evolve is often more revealing than a single frame.
            </p>

            <div className="border-l-2 border-cyan-500/50 pl-6">
              <p className="text-[14px] font-medium text-cyan-400 mb-2 tracking-[1px] uppercase">
                How V.E.R.I.T.A.S checks this:
              </p>
              <p className="text-[15px] font-light text-white/60 leading-relaxed">
                We track facial identity and landmark stability across frames to identify unnatural motion and identity shifts.
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 relative overflow-hidden flex items-center justify-center p-12 z-50">
          <div className="absolute left-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
          <video 
            src="/section2.mp4"
            className="w-[75%] h-[75%] object-cover rounded-2xl shadow-2xl z-50"
            autoPlay
            muted
            loop
            playsInline
          />
        </div>
      </section>

      {/* SECTION 3 - EYES & BLINKING */}
      <section
        ref={(el) => { sectionsRef.current[3] = el; }}
        className="snap-section flex h-screen w-screen relative bg-black overflow-hidden"
      >
        <div className="flex-1 relative overflow-hidden flex items-center justify-center p-12 z-50">
          <video 
            src="/section3.mp4"
            className="w-[75%] h-[75%] object-cover rounded-2xl shadow-2xl z-50"
            autoPlay
            muted
            loop
            playsInline
          />
          <div className="absolute right-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
        </div>

        <div className="flex-1 flex items-center justify-center p-[60px] relative">
          <div className="max-w-[520px] relative z-10 section-content">
            <h2 className="text-[48px] font-normal tracking-[4px] leading-tight mb-8 text-white">
              Pay Attention to the Eyes
            </h2>

            <p className="text-[17px] font-light text-white/70 mb-8 leading-relaxed">
              Blinking, eye movement, and micro-expressions are involuntary in real humans. Deepfakes often reproduce these patterns imperfectly, resulting in blinks that feel mechanical, irregular, or unnatural.
            </p>

            <p className="text-[17px] font-light text-white/70 mb-10 leading-relaxed">
              Eyes can reveal manipulation even when the rest of the face looks convincing.
            </p>

            <div className="border-l-2 border-cyan-500/50 pl-6">
              <p className="text-[14px] font-medium text-cyan-400 mb-2 tracking-[1px] uppercase">
                How V.E.R.I.T.A.S checks this:
              </p>
              <p className="text-[15px] font-light text-white/60 leading-relaxed">
                We analyze blink patterns, eye movement coherence, and subtle physiological signals that are difficult for synthetic media to replicate.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 4 - LIGHTING & SHADOWS */}
      <section
        ref={(el) => { sectionsRef.current[4] = el; }}
        className="snap-section flex h-screen w-screen relative bg-black overflow-hidden"
      >
        <div className="flex-1 flex items-center justify-center p-[60px] relative">
          <div className="max-w-[520px] relative z-10 section-content">
            <h2 className="text-[48px] font-normal tracking-[4px] leading-tight mb-8 text-white">
              Check Lighting and Shadows
            </h2>

            <p className="text-[17px] font-light text-white/70 mb-8 leading-relaxed">
              Real-world lighting follows physical rules. In manipulated media, facial lighting may not match the surrounding environment, and shadows can behave inconsistently.
            </p>

            <p className="text-[17px] font-light text-white/70 mb-10 leading-relaxed">
              These physical mismatches are often overlooked but can be strong indicators of synthetic content.
            </p>

            <div className="border-l-2 border-cyan-500/50 pl-6">
              <p className="text-[14px] font-medium text-cyan-400 mb-2 tracking-[1px] uppercase">
                How V.E.R.I.T.A.S checks this:
              </p>
              <p className="text-[15px] font-light text-white/60 leading-relaxed">
                We evaluate lighting consistency, shadow direction, and depth plausibility to ensure the face aligns with real-world physics.
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 relative overflow-hidden flex items-center justify-center p-12 z-50">
          <div className="absolute left-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
          <img 
            src="/section4.png"
            alt="Lighting Analysis"
            className="w-[75%] h-[75%] object-cover rounded-2xl shadow-2xl z-50"
          />
        </div>
      </section>

      {/* SECTION 5 - AUDIO & LIP-SYNC */}
      <section
        ref={(el) => { sectionsRef.current[5] = el; }}
        className="snap-section flex h-screen w-screen relative bg-black overflow-hidden"
      >
        <div className="flex-1 relative overflow-hidden flex items-center justify-center p-12 z-50">
          <video 
            src="/section5.mp4"
            className="w-[75%] h-[75%] object-cover rounded-2xl shadow-2xl z-50"
            autoPlay
            muted
            loop
            playsInline
          />
          <div className="absolute right-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
        </div>

        <div className="flex-1 flex items-center justify-center p-[60px] relative">
          <div className="max-w-[520px] relative z-10 section-content">
            <h2 className="text-[48px] font-normal tracking-[4px] leading-tight mb-8 text-white">
              Listen as Carefully as You Watch
            </h2>

            <p className="text-[17px] font-light text-white/70 mb-8 leading-relaxed">
              When audio is present, mismatches between lip movement and speech timing can reveal manipulation. Synthetic voices may also sound emotionally flat or slightly unnatural.
            </p>

            <p className="text-[17px] font-light text-white/70 mb-10 leading-relaxed">
              Audio inconsistencies often confirm visual suspicion.
            </p>

            <div className="border-l-2 border-cyan-500/50 pl-6">
              <p className="text-[14px] font-medium text-cyan-400 mb-2 tracking-[1px] uppercase">
                How V.E.R.I.T.A.S checks this:
              </p>
              <p className="text-[15px] font-light text-white/60 leading-relaxed">
                When audio is available, we compare lip movement with speech timing and analyze voice characteristics for signs of synthetic generation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 6 - INVISIBLE ARTIFACTS */}
      <section
        ref={(el) => { sectionsRef.current[6] = el; }}
        className="snap-section flex h-screen w-screen relative bg-black overflow-hidden"
      >
        <div className="flex-1 flex items-center justify-center p-[60px] relative">
          <div className="max-w-[520px] relative z-10 section-content">
            <h2 className="text-[48px] font-normal tracking-[4px] leading-tight mb-8 text-white">
              Some Clues Are Invisible to Humans
            </h2>

            <p className="text-[17px] font-light text-white/70 mb-8 leading-relaxed">
              Not all signs of manipulation are visible. Deepfakes often leave behind subtle digital artifacts at the pixel level that humans cannot reliably detect.
            </p>

            <p className="text-[17px] font-light text-white/70 mb-10 leading-relaxed">
              This is where AI tools provide critical support.
            </p>

            <div className="border-l-2 border-cyan-500/50 pl-6">
              <p className="text-[14px] font-medium text-cyan-400 mb-2 tracking-[1px] uppercase">
                How V.E.R.I.T.A.S checks this:
              </p>
              <p className="text-[15px] font-light text-white/60 leading-relaxed">
                We analyze images in the frequency domain to detect artifacts introduced by generative models that are invisible to the human eye.
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 relative overflow-hidden flex items-center justify-center p-12 z-50">
          <div className="absolute left-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
          <img 
            src="/section6.jpg"
            alt="Digital Artifacts"
            className="w-[75%] h-[75%] object-cover rounded-2xl shadow-2xl z-50"
          />
        </div>
      </section>

      {/* SECTION 7 - CONTEXT & SOURCE */}
      <section
        ref={(el) => { sectionsRef.current[7] = el; }}
        className="snap-section flex h-screen w-screen relative bg-black overflow-hidden"
      >
        <div className="flex-1 relative overflow-hidden flex items-center justify-center p-12 z-50">
          <video 
            src="/section7.mp4"
            className="w-[75%] h-[75%] object-cover rounded-2xl shadow-2xl z-50"
            autoPlay
            muted
            loop
            playsInline
          />
          <div className="absolute right-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
        </div>

        <div className="flex-1 flex items-center justify-center p-[60px] relative">
          <div className="max-w-[520px] relative z-10 section-content">
            <h2 className="text-[48px] font-normal tracking-[4px] leading-tight mb-8 text-white">
              Always Question the Context
            </h2>

            <p className="text-[17px] font-light text-white/70 mb-8 leading-relaxed">
              Even convincing media can be misleading without proper context. Deepfakes spread fastest when content is emotionally charged or shared from unverified sources.
            </p>

            <p className="text-[17px] font-light text-white/70 mb-10 leading-relaxed">
              Critical thinking remains essential.
            </p>

            <div className="border-l-2 border-cyan-500/50 pl-6">
              <p className="text-[14px] font-medium text-cyan-400 mb-2 tracking-[1px] uppercase">
                How V.E.R.I.T.A.S checks this:
              </p>
              <p className="text-[15px] font-light text-white/60 leading-relaxed">
                We examine metadata and file properties for signs of editing, re-encoding, or missing source information, but human judgment is still key.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FINAL SECTION - HUMANS + AI */}
      <section
        ref={(el) => { sectionsRef.current[8] = el; }}
        className="snap-section flex h-screen w-screen relative overflow-hidden items-center justify-center"
      >
        {/* Animated background - same as landing page */}
        <div className="fixed inset-0 z-0 pointer-events-none">
          <AnoAI className="opacity-90" />
          <SnowParticles quantity={80} />
        </div>

        <div className="max-w-[800px] text-center space-y-12 px-6 section-content relative z-20">
          <h2 className="text-[56px] font-normal tracking-[6px] leading-tight text-white uppercase">
            Human Judgment, Strengthened by AI
          </h2>

          <p className="text-[20px] font-light text-white/70 leading-relaxed max-w-[600px] mx-auto">
            No single clue proves media is fake.
          </p>

          <p className="text-[20px] font-light text-white/70 leading-relaxed max-w-[600px] mx-auto">
            V.E.R.I.T.A.S combines multiple forensic signals to support informed decisions — not replace human judgment.
          </p>

          <div className="flex gap-5 justify-center pt-8">
            <button 
              onClick={() => router.push('/upload')}
              className="group relative px-12 py-4 text-[15px] font-normal tracking-[1px] uppercase border border-white/20 bg-white/[0.08] backdrop-blur-[10px] text-white cursor-pointer overflow-hidden transition-all duration-300 hover:bg-white/[0.12] hover:border-white/35 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(255,255,255,0.08)]"
            >
              <span className="relative z-10">Analyze Media with V.E.R.I.T.A.S</span>
              <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-white/10 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[400px] group-hover:h-[400px]" />
            </button>

            <button 
              onClick={() => router.push('/')}
              className="group relative px-12 py-4 text-[15px] font-normal tracking-[1px] uppercase border border-white/15 bg-transparent text-white/70 cursor-pointer overflow-hidden transition-all duration-300 hover:text-white/90 hover:border-white/25 hover:-translate-y-0.5"
            >
              <span className="relative z-10">Return to Home</span>
              <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-white/10 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[400px] group-hover:h-[400px]" />
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
