'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import * as d3 from 'd3'
import { cn } from '@/components/ui/utils'

export interface GraphNode {
  id: string
  title: string
  type: 'note' | 'resource' | 'idea'
  createdAt: string
  tags?: string[]
  description?: string
}

export interface GraphEdge {
  source: string
  target: string
  label?: string
}

interface KnowledgeGraphProps {
  nodes: GraphNode[]
  edges: GraphEdge[]
  onNodeClick: (id: string) => void
  searchQuery?: string
}

interface SimNode extends GraphNode {
  x: number
  y: number
  vx: number
  vy: number
  fx?: number | null
  fy?: number | null
}

interface SimLink {
  source: string | SimNode
  target: string | SimNode
  label?: string
}

const NODE_RADIUS = 24
const COLORS: Record<string, string> = {
  note: 'var(--accent-secondary)',
  resource: 'var(--accent-primary)',
  idea: 'var(--accent-warning)',
}

export function KnowledgeGraph({ nodes, edges, onNodeClick, searchQuery }: KnowledgeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const [tooltip, setTooltip] = useState<{ x: number; y: number; title: string } | null>(null)

  const simulationRef = useRef<d3.Simulation<SimNode, SimLink> | null>(null)

  const handleResize = useCallback(() => {
    if (!containerRef.current || !svgRef.current) return
    const { width, height } = containerRef.current.getBoundingClientRect()
    d3.select(svgRef.current).attr('width', width).attr('height', height)
    if (simulationRef.current) {
      simulationRef.current.force('center', d3.forceCenter(width / 2, height / 2))
      simulationRef.current.alpha(0.3).restart()
    }
  }, [])

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return

    const container = containerRef.current
    const { width, height } = container.getBoundingClientRect()

    const svgSel = d3.select(svgRef.current)
    svgSel.selectAll('*').remove()
    svgSel.attr('width', width).attr('height', height)

    const g = svgSel.append('g')

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => { g.attr('transform', event.transform) })

    svgSel.call(zoom)

    const simNodes: SimNode[] = nodes.map(n => ({ ...n, x: width / 2, y: height / 2, vx: 0, vy: 0 }))
    const simLinks: SimLink[] = edges.map(e => ({ source: e.source, target: e.target, label: e.label }))

    const linkGroup = g.append('g').attr('class', 'links')
    const nodeGroup = g.append('g').attr('class', 'nodes')

    const linkSel = linkGroup
      .selectAll<SVGLineElement, SimLink>('line')
      .data(simLinks)
      .join('line')
      .attr('stroke', 'var(--border)')
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.5)

    const nodeSel = nodeGroup
      .selectAll<SVGGElement, SimNode>('g.node')
      .data(simNodes)
      .join('g')
      .attr('class', 'node')
      .style('cursor', 'pointer')
      .on('click', (_event, d) => { onNodeClick(d.id) })
      .on('mouseenter', (event, d) => {
        const rect = container.getBoundingClientRect()
        setTooltip({ x: event.clientX - rect.left, y: event.clientY - rect.top - 10, title: d.title })
      })
      .on('mouseleave', () => { setTooltip(null) })

    const drag = d3.drag<SVGGElement, SimNode>()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart()
        d.fx = d.x
        d.fy = d.y
      })
      .on('drag', (event, d) => {
        d.fx = event.x
        d.fy = event.y
      })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0)
        d.fx = null
        d.fy = null
      })

    nodeSel.call(drag)

    const shapeG = nodeSel.append('g').attr('class', 'shape')

    shapeG.each(function (d) {
      const sel = d3.select(this)
      if (d.type === 'note') {
        sel.append('circle')
          .attr('r', NODE_RADIUS)
          .attr('fill', COLORS[d.type])
          .attr('fill-opacity', 0.15)
          .attr('stroke', COLORS[d.type])
          .attr('stroke-width', 2)
        sel.append('circle')
          .attr('r', 6)
          .attr('fill', COLORS[d.type])
      } else if (d.type === 'resource') {
        const s = NODE_RADIUS * 0.8
        sel.append('rect')
          .attr('x', -s)
          .attr('y', -s)
          .attr('width', s * 2)
          .attr('height', s * 2)
          .attr('rx', 6)
          .attr('fill', COLORS[d.type])
          .attr('fill-opacity', 0.15)
          .attr('stroke', COLORS[d.type])
          .attr('stroke-width', 2)
        sel.append('rect')
          .attr('x', -5)
          .attr('y', -5)
          .attr('width', 10)
          .attr('height', 10)
          .attr('rx', 2)
          .attr('fill', COLORS[d.type])
      } else if (d.type === 'idea') {
        sel.append('polygon')
          .attr('points', `0,${-NODE_RADIUS} ${NODE_RADIUS},0 0,${NODE_RADIUS} ${-NODE_RADIUS},0`)
          .attr('fill', COLORS[d.type])
          .attr('fill-opacity', 0.15)
          .attr('stroke', COLORS[d.type])
          .attr('stroke-width', 2)
        sel.append('polygon')
          .attr('points', `0,-7 7,0 0,7 -7,0`)
          .attr('fill', COLORS[d.type])
      }
    })

    nodeSel.append('text')
      .text(d => d.title.length > 16 ? d.title.slice(0, 14) + '…' : d.title)
      .attr('text-anchor', 'middle')
      .attr('dy', NODE_RADIUS + 16)
      .attr('fill', 'var(--text-secondary)')
      .attr('font-size', 10)
      .attr('font-family', 'var(--font-dm-sans), DM Sans, sans-serif')
      .style('pointer-events', 'none')

    const simulation = d3.forceSimulation<SimNode>(simNodes)
      .force('link', d3.forceLink<SimNode, SimLink>(simLinks).id(d => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(NODE_RADIUS + 10))
      .on('tick', () => {
        linkSel
          .attr('x1', d => (d.source as SimNode).x)
          .attr('y1', d => (d.source as SimNode).y)
          .attr('x2', d => (d.target as SimNode).x)
          .attr('y2', d => (d.target as SimNode).y)

        nodeSel.attr('transform', d => `translate(${d.x},${d.y})`)
      })

    simulationRef.current = simulation

    const ro = new ResizeObserver(() => { handleResize() })
    ro.observe(container)

    return () => {
      simulation.stop()
      ro.disconnect()
      simulationRef.current = null
    }
  }, [nodes, edges, onNodeClick, handleResize])

  const matchIds = searchQuery
    ? new Set(
        nodes
          .filter(n => n.title.toLowerCase().includes(searchQuery.toLowerCase()))
          .map(n => n.id)
      )
    : null

  return (
    <div
      ref={containerRef}
      className="w-full h-full min-h-[500px] relative rounded-xl overflow-hidden border border-[var(--border)] bg-[var(--background-card)]"
    >
      <svg
        ref={svgRef}
        className="w-full h-full"
        style={{ cursor: 'grab' }}
      />
      {tooltip && (
        <div
          className={cn(
            'absolute z-50 px-3 py-1.5 rounded-lg text-xs font-medium pointer-events-none',
            'bg-[var(--background-elevated)] border border-[var(--border)]',
            'text-[var(--text-primary)] shadow-lg backdrop-blur-[8px]',
          )}
          style={{ left: tooltip.x, top: tooltip.y, transform: 'translate(-50%, -100%)' }}
        >
          {tooltip.title}
        </div>
      )}
      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-[var(--text-muted)] text-sm">
          No nodes to display
        </div>
      )}
      <style>{`
        @keyframes node-glow {
          0%, 100% { filter: drop-shadow(0 0 4px var(--accent-primary)); }
          50% { filter: drop-shadow(0 0 12px var(--accent-primary)); }
        }
        .node-search-highlight > .shape > * {
          animation: node-glow 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
}
