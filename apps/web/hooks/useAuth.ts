import { useEffect, useState } from 'react'
import { supabase, isUsingPlaceholders } from '@/lib/supabase'
import { User as SupabaseUser } from '@supabase/supabase-js'

const guestUser = { id: 'guest', email: 'guest@local.dev', app_metadata: {}, user_metadata: {}, aud: 'authenticated', created_at: new Date().toISOString() } as SupabaseUser

export function useAuth() {
  const [user, setUser] = useState<SupabaseUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isUsingPlaceholders) {
      setUser(guestUser)
      setLoading(false)
      return
    }

    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  return { user, loading }
}