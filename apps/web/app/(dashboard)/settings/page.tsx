'use client'

import { PageHeader } from '@/components/ui/PageHeader'
import { SettingsPage } from '@/components/settings/SettingsPage'

export default function SettingsPageRoute(): JSX.Element {
  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Settings"
        description="Configure your AI, appearance, notifications, and system preferences"
      />
      <SettingsPage />
    </div>
  )
}
