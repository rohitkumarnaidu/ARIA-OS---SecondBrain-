import { WifiOff } from 'lucide-react'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Offline — ARIA OS',
  description: 'You are currently offline',
}

export default function OfflinePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-background-page px-4">
      <div className="flex flex-col items-center gap-6 text-center max-w-md">
        <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-accent-primary/10">
          <WifiOff className="h-10 w-10 text-accent-primary" />
        </div>
        <h1 className="text-2xl font-bold text-text-primary font-display">
          You&apos;re Offline
        </h1>
        <p className="text-text-secondary">
          Don&apos;t worry — your cached data is still available. Some features may be limited until you reconnect.
        </p>
        <div className="mt-4 flex flex-col gap-3 text-left w-full rounded-xl border border-border bg-background-card p-4">
          <h2 className="text-sm font-semibold text-text-primary">What you can do offline:</h2>
          <ul className="flex flex-col gap-2 text-sm text-text-secondary">
            <li className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-accent-neon" />
              View cached tasks and notes
            </li>
            <li className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-accent-neon" />
              Browse previously loaded data
            </li>
            <li className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-accent-neon" />
              Edit cached items (syncs when online)
            </li>
          </ul>
        </div>
      </div>
    </main>
  )
}
