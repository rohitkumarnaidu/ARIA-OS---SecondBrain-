import { api } from '@/lib/api'
import type { GraphNode, GraphEdge } from '@/components/knowledge'

const BASE = '/api/v1/knowledge'

export const knowledgeService = {
  list: () => api.get<{ nodes: GraphNode[]; edges: GraphEdge[] }>(BASE),
  get: (id: string) => api.get<GraphNode>(`${BASE}/${id}`),
  search: (query: string) => api.get<GraphNode[]>(`${BASE}/search`, { params: { q: query } }),
}
