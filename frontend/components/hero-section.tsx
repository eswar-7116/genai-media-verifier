'use client';

import { useRouter } from 'next/navigation';

export default function HeroSection() {
  const router = useRouter();

  return (
    <div id="home" className="flex h-screen w-screen relative bg-gradient-to-br from-black via-[#0a0a0f] to-black overflow-hidden z-10">
      <div 
        className="fixed inset-0 pointer-events-none z-[9999] opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          willChange: 'opacity'
        }}
      />

      <div className="flex-1 relative overflow-hidden flex items-center justify-center">
        <video 
          className="w-full h-full object-cover"
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          poster="/video-poster.jpg"
        >
          <source src="/Unsettling_Glitched_Face_Video_Generation.mp4" type="video/mp4" />
        </video>
        
        <div className="absolute right-0 top-[10%] bottom-[10%] w-px bg-gradient-to-b from-transparent via-white/10 to-transparent" />
      </div>

      <div className="flex-1 flex items-center justify-center p-[60px] relative">
        <div 
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `
              radial-gradient(circle at 30% 50%, rgba(20, 30, 60, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 70% 80%, rgba(10, 20, 40, 0.1) 0%, transparent 40%)
            `
          }}
        />

        <div className="max-w-[520px] relative z-10 -translate-y-[70px]">
          <p className="text-sm font-light tracking-[3px] uppercase text-white/50 mb-6 animate-fade-in-up opacity-0 [animation-delay:0.2s] [animation-fill-mode:forwards]">
            TRUST WHAT YOU SEE?
          </p>

          <h1 className="text-[92px] font-normal tracking-[12px] leading-none mb-8 text-white uppercase animate-fade-in-up opacity-0 [animation-delay:0.4s] [animation-fill-mode:forwards] font-space">
            V.E.R.I.T.A.S
          </h1>

          <p className="text-[17px] font-light text-white/60 mb-[120px] tracking-[0.5px] animate-fade-in-up opacity-0 [animation-delay:0.6s] [animation-fill-mode:forwards]">
            AI-assisted media credibility analysis
          </p>

          <div className="flex gap-5 animate-fade-in-up opacity-0 [animation-delay:0.8s] [animation-fill-mode:forwards]">
            <button 
              onClick={() => router.push('/upload')}
              className="group relative px-12 py-4 text-[15px] font-normal tracking-[1px] uppercase border border-white/20 bg-white/[0.08] backdrop-blur-[10px] text-white cursor-pointer overflow-hidden transition-all duration-300 hover:bg-white/[0.12] hover:border-white/35 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(255,255,255,0.08)] will-change-transform"
            >
              <span className="relative z-10">Upload</span>
              <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-white/10 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[300px] group-hover:h-[300px]" />
            </button>

            <button 
              onClick={() => router.push('/learn')}
              className="group relative px-12 py-4 text-[15px] font-normal tracking-[1px] uppercase border border-white/15 bg-transparent text-white/70 cursor-pointer overflow-hidden transition-all duration-300 hover:text-white/90 hover:border-white/25 hover:-translate-y-0.5 will-change-transform"
            >
              <span className="relative z-10">Learn</span>
              <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-white/10 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[300px] group-hover:h-[300px]" />
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
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

        .will-change-transform {
          will-change: transform;
        }
        @media (max-width: 1024px) {
          .flex-1:first-child::after {
            display: none;
          }
        }
      `}</style>
    </div>
  );
}
