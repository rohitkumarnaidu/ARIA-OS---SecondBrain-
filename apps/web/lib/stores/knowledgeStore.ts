import { create } from 'zustand'
import { knowledgeService } from '@/lib/services'

import type { GraphNode, GraphEdge } from '@/components/knowledge'

interface KnowledgeStore {
  nodes: GraphNode[]
  edges: GraphEdge[]
  loading: boolean
  error: string | null
  searchQuery: string
  fetch: () => Promise<void>
  search: (query: string) => Promise<void>
  setSearchQuery: (query: string) => void
}

export const useKnowledgeStore = create<KnowledgeStore>((set, get) => ({
  nodes: [],
  edges: [],
  loading: false,
  error: null,
  searchQuery: '',

  fetch: async () => {
    set({ loading: true, error: null })
    try {
      const data = await knowledgeService.list()
      set({ nodes: data.nodes, edges: data.edges, loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load knowledge graph'
      set({ error: message, loading: false })
    }
  },

  search: async (query) => {
    set({ loading: true, error: null, searchQuery: query })
    try {
      const results = await knowledgeService.search(query)
      set({ nodes: results as GraphNode[], loading: false })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Search failed'
      set({ error: message, loading: false })
    }
  },

  setSearchQuery: (query) => set({ searchQuery: query }),
}))
