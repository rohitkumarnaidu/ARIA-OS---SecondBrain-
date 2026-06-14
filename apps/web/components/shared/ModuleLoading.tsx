import { Loader2 } from 'lucide-react'

export function ModuleLoading({ name = 'Page' }: { name?: string }) {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center gap-4" role="status" aria-label={`Loading ${name}`}>
      <div className="relative">
        <div className="w-12 h-12 rounded-xl border-2 border-accent-primary/30 animate-pulse-glow" />
        <div className="absolute inset-0 flex items-center justify-center">
          <Loader2 size={24} className="text-accent-primary animate-spin" />
        </div>
      </div>
      <p className="text-text-tertiary text-sm">Loading {name}...</p>
    </div>
  )
}
