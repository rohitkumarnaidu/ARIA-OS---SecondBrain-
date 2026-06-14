import { create } from 'zustand'
import { supabase } from './supabase'

export interface User {
  id: string
  name?: string
  email?: string
  avatar_url?: string
  college?: string
  year?: number
  skills?: string[]
  bio?: string
  daily_routine?: any
  opportunity_preferences?: any
}

interface UserStore {
  user: User | null
  loading: boolean
  error: string | null
  signIn: () => Promise<void>
  signOut: () => Promise<void>
  fetchUser: () => Promise<void>
}

export const useUserStore = create<UserStore>((set, get) => ({
  user: null,
  loading: false,
  error: null,

  signIn: async () => {
    set({ loading: true, error: null })
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/dashboard`,
        },
      })
      if (error) throw error
      set({ loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  signOut: async () => {
    set({ loading: true, error: null })
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      set({ user: null, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },

  fetchUser: async () => {
    set({ loading: true, error: null })
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        const { data } = await supabase
          .from('users')
          .select('*')
          .eq('id', user.id)
          .single()
        
        set({ user: data || { id: user.id, email: user.email }, loading: false })
      } else {
        set({ user: null, loading: false })
      }
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },
}))