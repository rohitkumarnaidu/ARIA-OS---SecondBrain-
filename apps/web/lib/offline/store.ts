import { create } from 'zustand'

interface OfflineState {
  isOnline: boolean
  pendingMutations: number
  failedMutations: number
  lastSyncAt: string | null
  syncInProgress: boolean
  lastSyncError: string | null
  setOnline: (online: boolean) => void
  setPendingMutations: (count: number) => void
  setFailedMutations: (count: number) => void
  setLastSyncAt: (timestamp: string | null) => void
  setSyncInProgress: (inProgress: boolean) => void
  setSyncError: (error: string | null) => void
  reset: () => void
}

const initialState = {
  isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  pendingMutations: 0,
  failedMutations: 0,
  lastSyncAt: null as string | null,
  syncInProgress: false,
  lastSyncError: null as string | null,
}

export const useOfflineStore = create<OfflineState>((set) => ({
  ...initialState,
  setOnline: (online) => set({ isOnline: online }),
  setPendingMutations: (count) => set({ pendingMutations: count }),
  setFailedMutations: (count) => set({ failedMutations: count }),
  setLastSyncAt: (timestamp) => set({ lastSyncAt: timestamp }),
  setSyncInProgress: (inProgress) => set({ syncInProgress: inProgress }),
  setSyncError: (error) => set({ lastSyncError: error }),
  reset: () => set(initialState),
}))

export type { OfflineState }