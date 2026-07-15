export type OpportunityType = 'strategic' | 'financial' | 'partnership' | 'career'
export type OpportunityStatus = 'new' | 'viewed' | 'saved' | 'applied' | 'interviewing' | 'accepted' | 'declined'

export interface MatchBreakdown {
  label: string
  value: number
}

export interface Opportunity {
  id: string
  title: string
  organization: string
  type: OpportunityType
  score: number
  description: string
  status: OpportunityStatus
  matchBreakdown: MatchBreakdown[]
  url?: string
  createdAt: string
  deadline?: string
}
