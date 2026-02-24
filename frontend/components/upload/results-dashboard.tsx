"use client"

import { Button } from '@/components/ui/button'
import { Download, RotateCcw } from 'lucide-react'
import RiskGauge from './risk-gauge'
import SignalsOverview from './signals-overview'
import KeyIndicators from './key-indicators'
import TechnicalAnalysis from './technical-analysis'
import { useState } from 'react'

interface ResultsDashboardProps {
  results: any
  fileType: 'image' | 'video'
  mode: 'quick' | 'deep'
  onReset: () => void
}

export default function ResultsDashboard({ 
  results, 
  fileType, 
  mode, 
  onReset 
}: ResultsDashboardProps) {
  const [hoveredChart, setHoveredChart] = useState<string | null>(null)
  
  const handleDownload = () => {
    const dataStr = JSON.stringify(results, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `analysis-report-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const finalScore = results.final_score || 0
  const riskLevel = results.risk_level || 'Unknown'
  const confidence = results.confidence || 0

  return (
    <section id="results-section" className="relative py-20 px-6 overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      
      <div className="relative max-w-7xl mx-auto space-y-16 z-10">
        
        <div className="text-center space-y-4 animate-fade-in-up">
          <p className="text-sm font-light tracking-[3px] uppercase text-white/50">
            ANALYSIS COMPLETE
          </p>
          <h2 className="text-5xl md:text-6xl font-light tracking-[8px] text-white uppercase">
            RESULTS
          </h2>
        </div>

        <div 
          className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start animate-fade-in-up opacity-0"
          style={{ animationDelay: '0.2s', animationFillMode: 'forwards' }}
        >
          <div className="flex justify-center">
            <div className="bg-[#1a1a1a] border border-white/10 rounded-3xl p-8 w-full">
              <RiskGauge 
                manipulationScore={finalScore}
                riskLevel={riskLevel}
                gaugeType="risk"
              />
            </div>
          </div>

          <div className="flex justify-center">
            <div className="bg-[#1a1a1a] border border-white/10 rounded-3xl p-8 w-full">
              <RiskGauge 
                manipulationScore={confidence}
                riskLevel="confidence"
                gaugeType="confidence"
              />
            </div>
          </div>

          <div className="flex items-center">
            <div className="bg-[#1a1a1a] border border-white/10 rounded-3xl p-8 w-full">
              <KeyIndicators 
                results={results}
                fileType={fileType}
              />
            </div>
          </div>
        </div>

        <div 
          className="animate-fade-in-up opacity-0"
          style={{ animationDelay: '0.4s', animationFillMode: 'forwards' }}
        >
          <SignalsOverview 
            results={results}
            fileType={fileType}
            onChartHover={setHoveredChart}
            hoveredChart={hoveredChart}
          />
        </div>

        <div 
          className="animate-fade-in-up opacity-0"
          style={{ animationDelay: '0.6s', animationFillMode: 'forwards' }}
        >
          <div className="bg-[#1a1a1a] border border-white/10 rounded-3xl p-8">
            <TechnicalAnalysis 
              results={results}
              fileType={fileType}
            />
          </div>
        </div>

        <div 
          className="animate-fade-in-up opacity-0"
          style={{ animationDelay: '0.8s', animationFillMode: 'forwards' }}
        >
          <div className="bg-[#1a1a1a] border border-white/10 rounded-3xl p-8">
            <div className="space-y-4">
              <h3 className="text-xl font-light tracking-[3px] uppercase text-white/90">Important Notice</h3>
              <p className="text-sm text-white/60 leading-relaxed">
                This assessment is probabilistic in nature and should not be considered definitive proof of authenticity or manipulation. 
                The multi-method approach increases detection accuracy but cannot guarantee perfect results. The findings are intended to 
                support journalistic and legal workflows and should be used alongside contextual analysis, source verification, chain of 
                custody validation, and human expert judgment.
              </p>
            </div>
          </div>
        </div>

        <div 
          className="flex items-center justify-center gap-6 pt-8 animate-fade-in-up opacity-0"
          style={{ animationDelay: '1s', animationFillMode: 'forwards' }}
        >
          <button
            onClick={onReset}
            className="group relative px-10 py-4 glass-card border-white/20 overflow-hidden transition-all duration-300 hover:bg-white/[0.12] hover:border-white/35 hover:-translate-y-0.5"
          >
            <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-white/10 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[300px] group-hover:h-[300px]" />
            <span className="relative z-10 flex items-center gap-3 text-white tracking-[1px] uppercase text-sm">
              <RotateCcw className="w-4 h-4" />
              New Analysis
            </span>
          </button>

          <button
            onClick={handleDownload}
            className="group relative px-10 py-4 glass-card border-neon-blue overflow-hidden transition-all duration-300 hover:bg-cyan-500/10 hover:-translate-y-0.5"
          >
            <span className="absolute top-1/2 left-1/2 w-0 h-0 rounded-full bg-cyan-500/20 -translate-x-1/2 -translate-y-1/2 transition-all duration-[600ms] group-hover:w-[300px] group-hover:h-[300px]" />
            <span className="relative z-10 flex items-center gap-3 text-neon-blue tracking-[1px] uppercase text-sm">
              <Download className="w-4 h-4" />
              Download Report
            </span>
          </button>
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
      `}</style>
    </section>
  )
}
