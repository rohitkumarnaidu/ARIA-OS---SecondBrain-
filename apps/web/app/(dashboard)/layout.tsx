'use client'

import { SkipLink } from '@/components/layout'
import { ShellSelector } from '@/components/shell'
import { OfflineBanner } from '@/components/layout'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <SkipLink />
      <OfflineBanner />
      <ErrorBoundary>
        <ShellSelector>
          {children}
        </ShellSelector>
      </ErrorBoundary>
    </div>
  )
}
