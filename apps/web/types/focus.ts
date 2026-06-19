export type FocusSessionStatus = 'idle' | 'running' | 'paused' | 'completed'
export type FocusPhase = 'work' | 'break'

export interface FocusSessionConfig {
  workMinutes: number
  breakMinutes: number
  objective: string
  tags: string[]
}

export interface FocusSession {
  id: string
  config: FocusSessionConfig
  status: FocusSessionStatus
  remainingSeconds: number
  cyclesCompleted: number
  startedAt: string | null
}
