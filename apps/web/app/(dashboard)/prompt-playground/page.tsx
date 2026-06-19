'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { api } from '@/lib/api'
import { FileText, ChevronRight, Play, Loader2, Tag, Info, FileCode, Copy, Check, AlertCircle, GitCommit, Plus, Minus } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { showSuccess, showError } from '@/lib/toast'

interface PromptMeta {
  name: string
  category: string
  file_path: string
  frontmatter: Record<string, unknown>
  body_length: number
  word_count: number
}

interface PromptDetail {
  name: string
  category: string
  file_path: string
  frontmatter: Record<string, unknown>
  body: string
  body_length: number
  word_count: number
}

const CATEGORY_LABELS: Record<string, string> = {
  system: 'System Prompts',
  agents: 'Agent Prompts',
  templates: 'Templates',
}

export default function PromptPlaygroundPage() {
  const [prompts, setPrompts] = useState<PromptMeta[]>([])
  const [selected, setSelected] = useState<PromptDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [renderVars, setRenderVars] = useState('')
  const [renderedOutput, setRenderedOutput] = useState<string | null>(null)
  const [renderLoading, setRenderLoading] = useState(false)
  const [history, setHistory] = useState<{ hash: string; date: string; author: string; message: string; additions: number; deletions: number }[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)

  useEffect(() => {
    api.get<{ total: number; prompts: PromptMeta[] }>('/api/v1/prompts')
      .then(res => {
        setPrompts(res.prompts)
        if (res.prompts.length > 0) {
          handleSelect(res.prompts[0].name)
        }
      })
      .catch(() => showError('Failed to load prompts'))
      .finally(() => setLoading(false))
  }, [])

  const handleSelect = useCallback(async (name: string) => {
    setDetailLoading(true)
    setRenderedOutput(null)
    setRenderVars('')
    setHistory([])
    try {
      const [detail, hist] = await Promise.all([
        api.get<PromptDetail>(`/api/v1/prompts/${name}`),
        api.get<{ name: string; commits: typeof history }>(`/api/v1/prompts/${name}/history`).catch(() => null),
      ])
      setSelected(detail)
      if (hist) setHistory(hist.commits)
    } catch {
      showError('Failed to load prompt')
    } finally {
      setDetailLoading(false)
    }
  }, [])

  const handleCopy = useCallback(async () => {
    if (!selected) return
    try {
      await navigator.clipboard.writeText(selected.body)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch { /* ignore */ }
  }, [selected])

  const handleRender = useCallback(async () => {
    if (!selected) return
    setRenderLoading(true)
    try {
      let variables: Record<string, string> = {}
      if (renderVars.trim()) {
        try {
          variables = JSON.parse(renderVars)
        } catch {
          showError('Invalid JSON in variables field')
          setRenderLoading(false)
          return
        }
      }
      const res = await api.post<{ rendered: string }>(`/api/v1/prompts/${selected.name}/render`, { variables })
      setRenderedOutput(res.rendered)
    } catch (err) {
      showError('Render failed')
    } finally {
      setRenderLoading(false)
    }
  }, [selected, renderVars])

  const grouped = useMemo(() => {
    const map = new Map<string, PromptMeta[]>()
    for (const p of prompts) {
      const list = map.get(p.category) || []
      list.push(p)
      map.set(p.category, list)
    }
    return Array.from(map.entries()).sort(([a], [b]) => {
      const order = ['system', 'agents', 'templates']
      return order.indexOf(a) - order.indexOf(b)
    })
  }, [prompts])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-0">
      {/* Sidebar */}
      <div className="w-72 shrink-0 border-r border-border-default overflow-y-auto no-scrollbar">
        <div className="p-4 border-b border-border-default">
          <h2 className="text-sm font-display font-semibold text-text-primary">Prompt Library</h2>
          <p className="text-xs text-text-tertiary mt-0.5">{prompts.length} prompts loaded</p>
        </div>
        <div className="p-2 space-y-4">
          {grouped.map(([category, items]) => (
            <div key={category}>
              <h3 className="text-[10px] font-mono font-medium text-text-tertiary uppercase tracking-widest px-2 mb-1">
                {CATEGORY_LABELS[category] || category}
              </h3>
              <div className="space-y-0.5">
                {items.map(p => (
                  <button
                    key={p.name}
                    onClick={() => handleSelect(p.name)}
                    className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-sm transition-colors ${
                      selected?.name === p.name
                        ? 'bg-accent-primary/10 text-accent-primary'
                        : 'text-text-secondary hover:bg-background-elevated'
                    }`}
                  >
                    <FileText size={14} className="shrink-0" />
                    <span className="truncate flex-1">{p.name}</span>
                    <span className="text-[10px] font-mono text-text-tertiary">{p.body_length}B</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto no-scrollbar">
        {detailLoading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 size={20} className="text-accent-primary animate-spin" />
          </div>
        ) : selected ? (
          <div className="max-w-4xl mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 text-xs text-text-tertiary mb-1">
                  <Tag size={12} />
                  {CATEGORY_LABELS[selected.category] || selected.category}
                  <ChevronRight size={10} />
                  {selected.name}
                </div>
                <h1 className="text-xl font-display font-bold text-text-primary">{selected.name}</h1>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="btn btn-ghost btn-sm gap-1.5"
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>

            {/* Frontmatter */}
            <div className="rounded-xl border border-border-default bg-background-card overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border-default">
                <Info size={14} className="text-accent-primary" />
                <span className="text-xs font-medium text-text-secondary">Frontmatter</span>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {Object.entries(selected.frontmatter).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-[10px] font-mono text-text-tertiary uppercase block">{key}</span>
                      <span className="text-sm text-text-primary font-mono">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </span>
                    </div>
                  ))}
                  <div>
                    <span className="text-[10px] font-mono text-text-tertiary uppercase block">Length</span>
                    <span className="text-sm text-text-primary font-mono">{selected.body_length} chars</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-text-tertiary uppercase block">Words</span>
                    <span className="text-sm text-text-primary font-mono">{selected.word_count}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Body */}
            <div className="rounded-xl border border-border-default bg-background-card overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border-default">
                <FileCode size={14} className="text-accent-primary" />
                <span className="text-xs font-medium text-text-secondary">Prompt Body</span>
              </div>
              <pre className="p-4 text-sm text-text-primary font-mono leading-relaxed overflow-x-auto whitespace-pre-wrap max-h-[50vh] overflow-y-auto">
                {selected.body}
              </pre>
            </div>

            {/* Render / Test */}
            <div className="rounded-xl border border-border-default bg-background-card overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border-default">
                <Play size={14} className="text-accent-neon" />
                <span className="text-xs font-medium text-text-secondary">Test Render</span>
              </div>
              <div className="p-4 space-y-3">
                <div>
                  <label className="text-xs text-text-tertiary mb-1 block">
                    Variables <span className="text-text-tertiary">(JSON, optional)</span>
                  </label>
                  <input
                    type="text"
                    value={renderVars}
                    onChange={(e) => setRenderVars(e.target.value)}
                    placeholder='{"user_name": "Alex", "date": "2026-06-20"}'
                    className="w-full input font-mono text-sm"
                  />
                </div>
                <button
                  onClick={handleRender}
                  disabled={renderLoading}
                  className="btn btn-primary btn-sm gap-1.5"
                >
                  {renderLoading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                  {renderLoading ? 'Rendering...' : 'Render'}
                </button>
                {renderedOutput && (
                  <div>
                    <label className="text-xs text-text-tertiary mb-1 block">Rendered Output</label>
                    <pre className="p-3 rounded-lg bg-background-elevated text-sm text-text-primary font-mono leading-relaxed overflow-x-auto whitespace-pre-wrap max-h-[30vh] overflow-y-auto">
                      {renderedOutput}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {/* Version History */}
            {history.length > 0 && (
              <div className="rounded-xl border border-border-default bg-background-card overflow-hidden">
                <div className="flex items-center gap-2 px-4 py-2.5 border-b border-border-default">
                  <GitCommit size={14} className="text-accent-primary" />
                  <span className="text-xs font-medium text-text-secondary">Version History</span>
                  <span className="text-[10px] font-mono text-text-tertiary ml-auto">{history.length} commit{history.length !== 1 ? 's' : ''}</span>
                </div>
                <div className="divide-y divide-border-default">
                  {history.map((commit, i) => (
                    <div key={commit.hash} className="flex items-center gap-3 px-4 py-2.5">
                      <div className="flex flex-col items-center gap-0.5 text-[10px] font-mono">
                        <span className="text-accent-success flex items-center gap-0.5">
                          <Plus size={10} />{commit.additions}
                        </span>
                        <span className="text-accent-error flex items-center gap-0.5">
                          <Minus size={10} />{commit.deletions}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-text-primary truncate">{commit.message}</p>
                        <div className="flex items-center gap-2 text-[11px] text-text-tertiary">
                          <span className="font-mono">{commit.hash}</span>
                          <span>{commit.author}</span>
                          <span>{new Date(commit.date).toLocaleDateString()}</span>
                        </div>
                      </div>
                      {i === 0 && (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-accent-primary/10 text-accent-primary">HEAD</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <AlertCircle size={24} className="text-text-tertiary mx-auto mb-2" />
              <p className="text-sm text-text-tertiary">No prompts loaded</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
