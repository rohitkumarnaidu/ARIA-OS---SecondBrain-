export type VideoStatus = 'to_watch' | 'watching' | 'watched'
export type ViewMode = 'grid' | 'list'

export interface YouTubeVideo {
  id: string
  title: string
  url: string
  thumbnail?: string
  channel: string
  duration?: string
  tags: string[]
  status: VideoStatus
  statusChangedAt: string
  collectionId?: string
  notes?: string
  created_at: string
}

export interface VideoCollection {
  id: string
  name: string
  videoIds: string[]
}
