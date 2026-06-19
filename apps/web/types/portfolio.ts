export type ProjectPhase = 'planning' | 'design' | 'build' | 'test' | 'launch' | 'maintain'

export interface Project {
  id: string
  title: string
  description?: string
  phase: ProjectPhase
  github_url?: string
  live_url?: string
  next_action?: string
  blocker?: string
  income_source_id?: string
  created_at: string
}

export interface GithubRepo {
  name: string
  stars: number
  forks: number
  lastCommit: string
  language: string
  description: string
}

export interface Milestone {
  id: string
  projectId: string
  title: string
  completed: boolean
  dueDate?: string
}

export interface AIInsight {
  id: string
  projectId: string
  summary: string
  confidence: 'High' | 'Medium' | 'Low'
  source: string
}

export interface ProjectFormData {
  title: string
  description: string
  phase: ProjectPhase
  github_url: string
  live_url: string
  next_action: string
  blocker: string
}
