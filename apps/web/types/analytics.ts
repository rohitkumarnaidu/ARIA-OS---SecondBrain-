export interface DeepAnalysisReport {
  id: string
  title: string
  createdAt: string
  type: 'weekly' | 'monthly' | 'insight'
  summary: string
}

export interface KPIMetric {
  label: string
  value: string
  icon: React.ElementType
  trend: 'up' | 'down' | 'neutral'
  trendValue?: string
  sparklineData: { value: number }[]
}

export interface HeatmapCell {
  day: string
  hour: number
  value: number
}

export interface SkillDimension {
  skill: string
  value: number
  fullMark: number
}

export interface ReportFilter {
  metrics: string[]
  dateRange: { start: string; end: string }
}
