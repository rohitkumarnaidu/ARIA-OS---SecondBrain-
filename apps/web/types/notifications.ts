import type { AppNotification as CanonicalNotification } from '@/lib/types'

export type NotificationCategory = CanonicalNotification['category']
export type NotificationPriority = CanonicalNotification['priority']
export type { CanonicalNotification as AppNotification }
