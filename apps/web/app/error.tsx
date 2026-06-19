'use client'

import { ModuleError } from '@/components/shared/ModuleError'

export default function RootError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <ModuleError error={error} reset={reset} name="ARIA OS" />
}
