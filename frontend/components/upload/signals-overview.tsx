"use client"

import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'

interface SignalsOverviewProps {
  results: any
  fileType: 'image' | 'video'
  onChartHover?: (chartId: string | null) => void
  hoveredChart?: string | null
}

function EnsembleDistributionStrip({ avgScore, maxScore, id, onHover, isHovered, isDimmed }: { avgScore: number; maxScore: number; id: string; onHover: (id: string | null) => void; isHovered: boolean; isDimmed: boolean }) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 300
    const height = 80
    const margin = { top: 10, right: 10, bottom: 10, left: 10 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const numBars = 16
    const data = Array.from({ length: numBars }, (_, i) => {
      let value = avgScore + (Math.random() - 0.5) * 0.3
      if (i === Math.floor(numBars * 0.7)) value = maxScore
      return Math.max(0, Math.min(1, value))
    })

    const xScale = d3.scaleBand().domain(d3.range(numBars).map(String)).range([0, innerWidth]).padding(0.1)
    const yScale = d3.scaleLinear().domain([0, 1]).range([innerHeight, 0])
    const colorScale = d3.scaleThreshold<number, string>().domain([0.4, 0.65]).range(['#10b981', '#f59e0b', '#ef4444'])

    const defs = svg.append('defs')
    data.forEach((d, i) => {
      const gradient = defs.append('linearGradient').attr('id', `grad-${id}-${i}`).attr('x1', '0%').attr('y1', '100%').attr('x2', '0%').attr('y2', '0%')
      const color = colorScale(d)
      gradient.append('stop').attr('offset', '0%').attr('stop-color', color).attr('stop-opacity', 0.6)
      gradient.append('stop').attr('offset', '100%').attr('stop-color', color).attr('stop-opacity', 1)
    })

    g.selectAll('.bar').data(data).join('rect').attr('class', 'bar')
      .attr('x', (d, i) => xScale(String(i)) || 0).attr('y', innerHeight).attr('width', xScale.bandwidth())
      .attr('height', 0).attr('rx', 2).attr('fill', (d, i) => `url(#grad-${id}-${i})`)
      .transition().duration(800).delay((d, i) => i * 30)
      .attr('y', d => yScale(d)).attr('height', d => innerHeight - yScale(d))
  }, [avgScore, maxScore, id])

  return (
    <div 
      className={`border border-white/10 rounded-2xl p-6 cursor-pointer transition-all duration-500 ease-out h-full flex flex-col justify-center bg-[#1a1a1a] ${
        isHovered ? 'scale-110 z-50 border-cyan-500/50 shadow-[0_0_40px_rgba(0,243,255,0.3)] bg-white/[0.08]' 
        : isDimmed ? 'opacity-40 scale-95' 
        : 'hover:border-cyan-500/30 hover:scale-105'
      }`}
      onMouseEnter={() => onHover(id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="space-y-3">
        <div className="text-sm font-light tracking-wider uppercase text-white/70">Frame Ensemble</div>
        <svg ref={svgRef} width="300" height="80" className="w-full" />
        <div className="text-xs text-white/50 space-y-0.5">
          <div>Avg: {Math.round(avgScore * 100)}%</div>
          <div>Max: {Math.round(maxScore * 100)}% (1 frame)</div>
        </div>
      </div>
    </div>
  )
}

function IdentityTimeline({ shifts, id, onHover, isHovered, isDimmed }: { shifts: number; id: string; onHover: (id: string | null) => void; isHovered: boolean; isDimmed: boolean }) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 300
    const height = 60
    const margin = { top: 15, right: 10, bottom: 15, left: 10 }
    const innerWidth = width - margin.left - margin.right
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    g.append('line').attr('x1', 0).attr('y1', 15).attr('x2', innerWidth).attr('y2', 15).attr('stroke', 'rgba(255,255,255,0.1)').attr('stroke-width', 1.5)

    const numFrames = 50
    const framePositions = d3.range(numFrames).map(i => (i / (numFrames - 1)) * innerWidth)
    g.selectAll('.frame-tick').data(framePositions).join('line').attr('class', 'frame-tick')
      .attr('x1', d => d).attr('y1', 13).attr('x2', d => d).attr('y2', 17).attr('stroke', 'rgba(255,255,255,0.05)').attr('stroke-width', 0.5)

    if (shifts === 0) return

    let numClusters = 1
    if (shifts > 30) numClusters = 5
    else if (shifts > 20) numClusters = 4
    else if (shifts > 10) numClusters = 3
    else if (shifts > 5) numClusters = 2

    const shiftsPerCluster = Math.floor(shifts / numClusters)
    const remainingShifts = shifts % numClusters
    const clusters = d3.range(numClusters).map(i => {
      const clusterShifts = shiftsPerCluster + (i < remainingShifts ? 1 : 0)
      const position = ((i + 0.5) / numClusters) * innerWidth
      const intensity = Math.min(clusterShifts / 10, 1)
      return { position, intensity, count: clusterShifts }
    })

    const markers: Array<{ x: number; r: number }> = []
    clusters.forEach(cluster => {
      const spread = 8 / (cluster.intensity * 2 + 1)
      const markerCount = Math.min(cluster.count, 8)
      for (let i = 0; i < markerCount; i++) {
        const offset = (i - markerCount / 2) * spread
        const x = Math.max(5, Math.min(innerWidth - 5, cluster.position + offset))
        const r = 3 + cluster.intensity * 3
        markers.push({ x, r })
      }
    })

    const defs = svg.append('defs')
    const radialGradient = defs.append('radialGradient').attr('id', `marker-grad-${id}`)
    radialGradient.append('stop').attr('offset', '0%').attr('stop-color', '#ef4444').attr('stop-opacity', 1)
    radialGradient.append('stop').attr('offset', '100%').attr('stop-color', '#dc2626').attr('stop-opacity', 0.7)

    g.selectAll('.marker').data(markers).join('circle').attr('class', 'marker')
      .attr('cx', d => d.x).attr('cy', 15).attr('r', 0).attr('fill', `url(#marker-grad-${id})`)
      .attr('stroke', '#fca5a5').attr('stroke-width', 1)
      .transition().duration(600).delay((d, i) => i * 40).attr('r', d => d.r)
  }, [shifts, id])

  return (
    <div 
      className={`border border-white/10 rounded-2xl p-6 cursor-pointer transition-all duration-500 ease-out h-full flex flex-col justify-center bg-[#1a1a1a] ${
        isHovered ? 'scale-110 z-50 border-cyan-500/50 shadow-[0_0_40px_rgba(0,243,255,0.3)] bg-white/[0.08]' 
        : isDimmed ? 'opacity-40 scale-95' 
        : 'hover:border-cyan-500/30 hover:scale-105'
      }`}
      onMouseEnter={() => onHover(id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="space-y-3">
        <div className="text-sm font-light tracking-wider uppercase text-white/70">Temporal Consistency</div>
        <svg ref={svgRef} width="300" height="60" className="w-full" />
        <div className="text-xs text-white/50">{shifts} identity shifts detected</div>
      </div>
    </div>
  )
}

function CoherenceStrip({ score, id, onHover, isHovered, isDimmed }: { score: number; id: string; onHover: (id: string | null) => void; isHovered: boolean; isDimmed: boolean }) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 300
    const height = 40
    const margin = { top: 5, right: 5, bottom: 5, left: 5 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const defs = svg.append('defs')
    const gradient = defs.append('linearGradient').attr('id', `coh-grad-${id}`).attr('x1', '0%').attr('y1', '0%').attr('x2', '100%').attr('y2', '0%')
    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#ef4444').attr('stop-opacity', 0.8)
    gradient.append('stop').attr('offset', '50%').attr('stop-color', '#f97316').attr('stop-opacity', 0.9)
    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#dc2626').attr('stop-opacity', 1)

    g.append('rect').attr('x', 0).attr('y', 0).attr('width', innerWidth).attr('height', innerHeight).attr('rx', 4).attr('fill', 'rgba(255,255,255,0.05)')
    g.append('rect').attr('x', 0).attr('y', 0).attr('width', 0).attr('height', innerHeight).attr('rx', 4).attr('fill', `url(#coh-grad-${id})`)
      .transition().duration(1200).ease(d3.easeCubicOut).attr('width', score * innerWidth)
  }, [score, id])

  return (
    <div 
      className={`border border-white/10 rounded-2xl p-6 cursor-pointer transition-all duration-500 ease-out h-full flex flex-col justify-center bg-[#1a1a1a] ${
        isHovered ? 'scale-110 z-50 border-cyan-500/50 shadow-[0_0_40px_rgba(0,243,255,0.3)] bg-white/[0.08]' 
        : isDimmed ? 'opacity-40 scale-95' 
        : 'hover:border-cyan-500/30 hover:scale-105'
      }`}
      onMouseEnter={() => onHover(id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="space-y-3">
        <div className="text-sm font-light tracking-wider uppercase text-white/70">Video Model Analysis</div>
        <div className="text-xs text-white/40 mb-2">VideoMAE — Global Temporal Coherence</div>
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-white/40"><span>Realistic</span><span>Unrealistic</span></div>
          <svg ref={svgRef} width="300" height="40" className="w-full" />
        </div>
        <div className="text-xs text-white/50">{Math.round(score * 100)}% coherence</div>
      </div>
    </div>
  )
}

function PhysiologicalBand({ score, blinkNatural, heartbeatDetected, id, onHover, isHovered, isDimmed }: { score: number; blinkNatural: boolean; heartbeatDetected: boolean; id: string; onHover: (id: string | null) => void; isHovered: boolean; isDimmed: boolean }) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 300
    const height = 40
    const margin = { top: 5, right: 5, bottom: 5, left: 5 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const defs = svg.append('defs')
    const gradient = defs.append('linearGradient').attr('id', `phy-grad-${id}`).attr('x1', '0%').attr('y1', '0%').attr('x2', '100%').attr('y2', '0%')
    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#10b981').attr('stop-opacity', 0.6)
    gradient.append('stop').attr('offset', `${(1 - score) * 100}%`).attr('stop-color', '#f59e0b').attr('stop-opacity', 0.8)
    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#ef4444').attr('stop-opacity', 1)

    g.append('rect').attr('x', 0).attr('y', 0).attr('width', innerWidth).attr('height', innerHeight).attr('rx', 4).attr('fill', 'rgba(255,255,255,0.05)')
    g.append('rect').attr('x', 0).attr('y', 0).attr('width', 0).attr('height', innerHeight).attr('rx', 4).attr('fill', `url(#phy-grad-${id})`)
      .transition().duration(1200).ease(d3.easeCubicOut).attr('width', innerWidth)
    
    g.append('line').attr('x1', 0).attr('y1', 0).attr('x2', 0).attr('y2', innerHeight).attr('stroke', '#fff').attr('stroke-width', 2).attr('opacity', 0.5)
      .transition().duration(1200).ease(d3.easeCubicOut).attr('x1', score * innerWidth).attr('x2', score * innerWidth)
  }, [score, id])

  return (
    <div 
      className={`border border-white/10 rounded-2xl p-6 cursor-pointer transition-all duration-500 ease-out h-full flex flex-col justify-center bg-[#1a1a1a] ${
        isHovered ? 'scale-110 z-50 border-cyan-500/50 shadow-[0_0_40px_rgba(0,243,255,0.3)] bg-white/[0.08]' 
        : isDimmed ? 'opacity-40 scale-95' 
        : 'hover:border-cyan-500/30 hover:scale-105'
      }`}
      onMouseEnter={() => onHover(id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="space-y-3">
        <div className="text-sm font-light tracking-wider uppercase text-white/70">Physiological Signals</div>
        <div className="space-y-2 text-xs text-white/60">
          <div className="flex items-start gap-2"><span className="text-white/30">•</span><span>Blink pattern: {blinkNatural ? 'Natural' : 'Unnatural'}</span></div>
          <div className="flex items-start gap-2"><span className="text-white/30">•</span><span>Heartbeat: {heartbeatDetected ? 'Detected' : 'Not detected'}</span></div>
        </div>
        <div className="space-y-2 mt-3">
          <div className="flex justify-between text-xs text-white/40"><span>Natural</span><span>Anomalous</span></div>
          <svg ref={svgRef} width="300" height="40" className="w-full" />
        </div>
        <div className="text-xs text-white/50">{Math.round(score * 100)}% anomaly likelihood</div>
      </div>
    </div>
  )
}

function AudioWaveform({ score, id, onHover, isHovered, isDimmed }: { score: number; id: string; onHover: (id: string | null) => void; isHovered: boolean; isDimmed: boolean }) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 300
    const height = 60
    const margin = { top: 10, right: 10, bottom: 10, left: 10 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const numBars = 40
    const waveData = Array.from({ length: numBars }, (_, i) => {
      const x = i / numBars
      const wave1 = Math.sin(x * Math.PI * 4) * 0.5
      const wave2 = Math.sin(x * Math.PI * 8) * 0.3
      const noise = (Math.random() - 0.5) * 0.2
      return Math.abs(wave1 + wave2 + noise)
    })

    const xScale = d3.scaleBand().domain(d3.range(numBars).map(String)).range([0, innerWidth]).padding(0.2)
    const yScale = d3.scaleLinear().domain([0, 1]).range([innerHeight / 2, 0])

    const defs = svg.append('defs')
    const gradient = defs.append('linearGradient').attr('id', `aud-grad-${id}`).attr('x1', '0%').attr('y1', '100%').attr('x2', '0%').attr('y2', '0%')
    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#00f3ff').attr('stop-opacity', 0.4)
    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#00f3ff').attr('stop-opacity', 1)

    g.selectAll('.bar-top').data(waveData).join('rect').attr('class', 'bar-top')
      .attr('x', (d, i) => xScale(String(i)) || 0).attr('y', innerHeight / 2).attr('width', xScale.bandwidth()).attr('height', 0).attr('rx', 1).attr('fill', `url(#aud-grad-${id})`)
      .transition().duration(800).delay((d, i) => i * 15).attr('y', d => yScale(d)).attr('height', d => innerHeight / 2 - yScale(d))

    g.selectAll('.bar-bottom').data(waveData).join('rect').attr('class', 'bar-bottom')
      .attr('x', (d, i) => xScale(String(i)) || 0).attr('y', innerHeight / 2).attr('width', xScale.bandwidth()).attr('height', 0).attr('rx', 1).attr('fill', `url(#aud-grad-${id})`)
      .transition().duration(800).delay((d, i) => i * 15).attr('height', d => innerHeight / 2 - yScale(d))
  }, [score, id])

  return (
    <div 
      className={`border border-white/10 rounded-2xl p-6 cursor-pointer transition-all duration-500 ease-out h-full flex flex-col justify-center bg-[#1a1a1a] ${
        isHovered ? 'scale-110 z-50 border-cyan-500/50 shadow-[0_0_40px_rgba(0,243,255,0.3)] bg-white/[0.08]' 
        : isDimmed ? 'opacity-40 scale-95' 
        : 'hover:border-cyan-500/30 hover:scale-105'
      }`}
      onMouseEnter={() => onHover(id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="space-y-3">
        <div className="text-sm font-light tracking-wider uppercase text-white/70">Audio Analysis</div>
        <svg ref={svgRef} width="300" height="60" className="w-full" />
        <div className="text-xs text-white/50">Audio present: {Math.round(score * 100)}% confidence</div>
      </div>
    </div>
  )
}

function PhysicsBand({ score, lightingConsistent, depthPlausible, id, onHover, isHovered, isDimmed }: { score: number; lightingConsistent: boolean; depthPlausible: boolean; id: string; onHover: (id: string | null) => void; isHovered: boolean; isDimmed: boolean }) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 300
    const height = 40
    const margin = { top: 5, right: 5, bottom: 5, left: 5 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const defs = svg.append('defs')
    const gradient = defs.append('linearGradient').attr('id', `phy-grad2-${id}`).attr('x1', '0%').attr('y1', '0%').attr('x2', '100%').attr('y2', '0%')
    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#6366f1').attr('stop-opacity', 0.6)
    gradient.append('stop').attr('offset', '50%').attr('stop-color', '#f59e0b').attr('stop-opacity', 0.8)
    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#ef4444').attr('stop-opacity', 1)

    g.append('rect').attr('x', 0).attr('y', 0).attr('width', innerWidth).attr('height', innerHeight).attr('rx', 4).attr('fill', 'rgba(255,255,255,0.05)')
    g.append('rect').attr('x', 0).attr('y', 0).attr('width', 0).attr('height', innerHeight).attr('rx', 4).attr('fill', `url(#phy-grad2-${id})`)
      .transition().duration(1200).ease(d3.easeCubicOut).attr('width', score * innerWidth)
  }, [score, id])

  return (
    <div 
      className={`border border-white/10 rounded-2xl p-6 cursor-pointer transition-all duration-500 ease-out h-full flex flex-col justify-center bg-[#1a1a1a] ${
        isHovered ? 'scale-110 z-50 border-cyan-500/50 shadow-[0_0_40px_rgba(0,243,255,0.3)] bg-white/[0.08]' 
        : isDimmed ? 'opacity-40 scale-95' 
        : 'hover:border-cyan-500/30 hover:scale-105'
      }`}
      onMouseEnter={() => onHover(id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="space-y-3">
        <div className="text-sm font-light tracking-wider uppercase text-white/70">Physics Consistency</div>
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-white/40"><span>Plausible</span><span>Anomalous</span></div>
          <svg ref={svgRef} width="300" height="40" className="w-full" />
        </div>
        <div className="text-xs text-white/50 space-y-0.5">
          <div>Lighting: {lightingConsistent ? 'Consistent' : 'Inconsistent'}</div>
          <div>Depth: {depthPlausible ? 'Plausible' : 'Implausible'}</div>
        </div>
      </div>
    </div>
  )
}

function MetadataCard({ score, hasAudio, suspiciousCount, id, onHover, isHovered, isDimmed }: { score: number; hasAudio: boolean; suspiciousCount: number; id: string; onHover: (id: string | null) => void; isHovered: boolean; isDimmed: boolean }) {
  return (
    <div 
      className={`border border-white/10 rounded-2xl p-6 cursor-pointer transition-all duration-500 ease-out h-full flex flex-col justify-center bg-[#1a1a1a] ${
        isHovered ? 'scale-110 z-50 border-cyan-500/50 shadow-[0_0_40px_rgba(0,243,255,0.3)] bg-white/[0.08]' 
        : isDimmed ? 'opacity-40 scale-95' 
        : 'hover:border-cyan-500/30 hover:scale-105'
      }`}
      onMouseEnter={() => onHover(id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="space-y-3">
        <div className="text-sm font-light tracking-wider uppercase text-white/70">Metadata Forensics</div>
        <div className="space-y-2 text-xs text-white/60">
          <div className="flex items-start gap-2"><span className="text-white/30">•</span><span>Audio: {hasAudio ? 'Present' : 'Not present'}</span></div>
          <div className="flex items-start gap-2"><span className="text-white/30">•</span><span>Suspicious indicators: {suspiciousCount}</span></div>
        </div>
        <div className="text-xs text-white/50">{Math.round(score * 100)}% anomaly score</div>
      </div>
    </div>
  )
}

function ImageChart({ score, title, detail, id, onHover, isHovered, isDimmed }: { score: number; title: string; detail: string; id: string; onHover: (id: string | null) => void; isHovered: boolean; isDimmed: boolean }) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 300
    const height = 50
    const margin = { top: 5, right: 5, bottom: 5, left: 5 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const color = score < 0.4 ? '#10b981' : score < 0.65 ? '#f59e0b' : '#ef4444'
    g.append('rect').attr('x', 0).attr('y', 0).attr('width', innerWidth).attr('height', innerHeight).attr('rx', 4).attr('fill', 'rgba(255,255,255,0.05)')
    g.append('rect').attr('x', 0).attr('y', 0).attr('width', 0).attr('height', innerHeight).attr('rx', 4).attr('fill', color)
      .transition().duration(1000).ease(d3.easeCubicOut).attr('width', score * innerWidth)
  }, [score])

  return (
    <div 
      className={`border border-white/10 rounded-2xl p-6 cursor-pointer transition-all duration-500 ease-out h-full flex flex-col justify-center bg-[#1a1a1a] ${
        isHovered ? 'scale-110 z-50 border-cyan-500/50 shadow-[0_0_40px_rgba(0,243,255,0.3)] bg-white/[0.08]' 
        : isDimmed ? 'opacity-40 scale-95' 
        : 'hover:border-cyan-500/30 hover:scale-105'
      }`}
      onMouseEnter={() => onHover(id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="space-y-3">
        <div className="text-sm font-light tracking-wider uppercase text-white/70">{title}</div>
        <div className="text-xs text-white/40 mb-2">{detail}</div>
        <svg ref={svgRef} width="300" height="50" className="w-full" />
        <div className="text-xs text-white/50">{Math.round(score * 100)}% detection</div>
      </div>
    </div>
  )
}

export default function SignalsOverview({ results, fileType, onChartHover, hoveredChart }: SignalsOverviewProps) {
  const [localHoveredChart, setLocalHoveredChart] = useState<string | null>(null)
  
  const handleChartHover = (chartId: string | null) => {
    setLocalHoveredChart(chartId)
    onChartHover?.(chartId)
  }

  const currentHovered = hoveredChart || localHoveredChart

  if (fileType === 'image') {
    const breakdown = results.analysis_breakdown || {}
    const signals = []

    if (breakdown.neural_network) {
      signals.push({
        id: 'neural',
        title: 'Neural Networks',
        score: breakdown.neural_network.score,
        detail: breakdown.neural_network.model_agreement 
          ? `${breakdown.neural_network.model_agreement.replace('_', ' ')} agreement`
          : `${breakdown.neural_network.num_models || 0} models`
      })
    }

    if (breakdown.frequency_domain) {
      signals.push({
        id: 'frequency',
        title: 'Frequency Domain',
        score: breakdown.frequency_domain.score,
        detail: breakdown.frequency_domain.dct_anomaly || breakdown.frequency_domain.fft_anomaly ? 'Anomalies detected' : 'No major anomalies'
      })
    }

    if (breakdown.facial_analysis) {
      signals.push({
        id: 'facial',
        title: 'Facial Forensics',
        score: breakdown.facial_analysis.score,
        detail: breakdown.facial_analysis.face_detected ? `${breakdown.facial_analysis.method_used || 'Face detected'}` : 'No faces detected'
      })
    }

    if (breakdown.metadata_forensics) {
      signals.push({
        id: 'metadata',
        title: 'Metadata',
        score: breakdown.metadata_forensics.score,
        detail: breakdown.metadata_forensics.exif_present ? 'EXIF present' : 'No EXIF data'
      })
    }

    if (signals.length === 0) return <div className="text-center py-8 text-white/50">No analysis signals available</div>

    return (
      <div className="space-y-8 bg-[#0f0f0f] rounded-3xl p-8 border border-white/10">
        <div>
          <h2 className="text-3xl font-light tracking-[4px] uppercase text-white">Signals Overview</h2>
          <p className="text-white/50 mt-2 tracking-wide">Analysis methods applied to this media</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {signals.map((signal) => (
            <ImageChart 
              key={signal.id}
              score={signal.score} 
              title={signal.title} 
              detail={signal.detail}
              id={signal.id}
              onHover={handleChartHover}
              isHovered={currentHovered === signal.id}
              isDimmed={currentHovered !== null && currentHovered !== signal.id}
            />
          ))}
        </div>
      </div>
    )
  }

  const layerSummaries = results.layer_summaries || {}
  const cards = []

  if (layerSummaries.visual?.frame_based) cards.push({ type: 'ensemble', id: 'ensemble', data: layerSummaries.visual.frame_based })
  if (layerSummaries.visual?.temporal) cards.push({ type: 'temporal', id: 'temporal', data: layerSummaries.visual.temporal })
  if (layerSummaries.visual?.['3d_model']) cards.push({ type: 'coherence', id: 'coherence', data: layerSummaries.visual['3d_model'] })
  if (layerSummaries.physiological) cards.push({ type: 'physiological', id: 'physiological', data: layerSummaries.physiological })
  if (layerSummaries.physics) cards.push({ type: 'physics', id: 'physics', data: layerSummaries.physics })
  if (layerSummaries.metadata) cards.push({ type: 'metadata', id: 'metadata', data: layerSummaries.metadata })
  
  if (layerSummaries.metadata) {
    if (layerSummaries.metadata.has_audio && layerSummaries.audio?.score) {
      cards.push({ type: 'audio', id: 'audio', data: layerSummaries.audio })
    }
  }

  if (cards.length === 0) return <div className="text-center py-8 text-white/50">No analysis signals available</div>

  return (
    <div className="space-y-8 bg-[#0f0f0f] rounded-3xl p-8 border border-white/10">
      <div>
        <h2 className="text-3xl font-light tracking-[4px] uppercase text-white">Signals Overview</h2>
        <p className="text-white/50 mt-2 tracking-wide">Analysis methods applied to this media</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card) => (
          <div key={card.id}>
            {card.type === 'ensemble' && (
              <EnsembleDistributionStrip 
                avgScore={card.data.ensemble_avg} 
                maxScore={card.data.ensemble_max}
                id={card.id}
                onHover={handleChartHover}
                isHovered={currentHovered === card.id}
                isDimmed={currentHovered !== null && currentHovered !== card.id}
              />
            )}
            {card.type === 'temporal' && (
              <IdentityTimeline 
                shifts={card.data.identity_shifts}
                id={card.id}
                onHover={handleChartHover}
                isHovered={currentHovered === card.id}
                isDimmed={currentHovered !== null && currentHovered !== card.id}
              />
            )}
            {card.type === 'coherence' && (
              <CoherenceStrip 
                score={card.data.score}
                id={card.id}
                onHover={handleChartHover}
                isHovered={currentHovered === card.id}
                isDimmed={currentHovered !== null && currentHovered !== card.id}
              />
            )}
            {card.type === 'physiological' && (
              <PhysiologicalBand 
                score={card.data.score} 
                blinkNatural={card.data.natural_blink_pattern} 
                heartbeatDetected={card.data.heartbeat_detected}
                id={card.id}
                onHover={handleChartHover}
                isHovered={currentHovered === card.id}
                isDimmed={currentHovered !== null && currentHovered !== card.id}
              />
            )}
            {card.type === 'physics' && (
              <PhysicsBand 
                score={card.data.score} 
                lightingConsistent={card.data.lighting_consistent} 
                depthPlausible={card.data.depth_plausible}
                id={card.id}
                onHover={handleChartHover}
                isHovered={currentHovered === card.id}
                isDimmed={currentHovered !== null && currentHovered !== card.id}
              />
            )}
            {card.type === 'metadata' && (
              <MetadataCard 
                score={card.data.score}
                hasAudio={card.data.has_audio}
                suspiciousCount={card.data.suspicious_indicators?.length || 0}
                id={card.id}
                onHover={handleChartHover}
                isHovered={currentHovered === card.id}
                isDimmed={currentHovered !== null && currentHovered !== card.id}
              />
            )}
            {card.type === 'audio' && (
              <AudioWaveform 
                score={card.data.score}
                id={card.id}
                onHover={handleChartHover}
                isHovered={currentHovered === card.id}
                isDimmed={currentHovered !== null && currentHovered !== card.id}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
