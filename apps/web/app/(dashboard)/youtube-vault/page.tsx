'use client'

import { PageHeader } from '@/components/ui/PageHeader'
import { YouTubeVault } from '@/components/youtube-vault/YouTubeVault'

export default function YouTubeVaultPage(): JSX.Element {
  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="YouTube Vault"
        description="Save, organize, and track learning videos"
      />
      <YouTubeVault />
    </div>
  )
}
