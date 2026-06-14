import { Loader2 } from 'lucide-react'

export default function DashboardLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background-dark">
      <div className="relative">
        <div className="w-12 h-12 rounded-xl border-2 border-accent-primary/30 animate-pulse-glow" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    </div>
  )
}
