'use client'

import dynamic from 'next/dynamic'
import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { ShellSelector } from '@/components/shell'
import { OfflineBanner } from '@/components/layout'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { useAuth } from '@/hooks/useAuth'
import { useStoreSync } from '@/hooks/useStoreSync'
import { persistSession } from '@/lib/ai/session'

const AIDock = dynamic(() => import('@/components/ai/AIDock').then(m => ({ default: m.AIDock })), { ssr: false })
const AIAssistant = dynamic(() => import('@/components/ai/AIActionConfirm').then(m => ({ default: m.AIActionConfirm })), { ssr: false })

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const { user } = useAuth()
  useStoreSync(user?.id)
  useEffect(() => { persistSession(pathname) }, [pathname])

  return (
    <div className="flex min-h-screen">
      <OfflineBanner />
      <AIDock />
      <ErrorBoundary>
        <ShellSelector>
          {children}
        </ShellSelector>
      </ErrorBoundary>
    </div>
  )
}
