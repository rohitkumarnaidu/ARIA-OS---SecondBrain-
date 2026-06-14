'use client'

import { useState, useRef, useEffect } from 'react'
import { Search, Bell, User, LogOut } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function Navbar() {
  const router = useRouter()
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/')
  }

  return (
    <header
      className="h-16 bg-background-card border-b border-border fixed top-0 right-0 left-60 z-40"
      role="banner"
    >
      <div className="h-full px-6 flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" size={18} aria-hidden="true" />
            <input
              type="text"
              placeholder="Search tasks, goals, ideas..."
              className="w-full bg-background-input border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-colors"
              aria-label="Search across all modules"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button
            className="p-2.5 hover:bg-background-elevated rounded-lg transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
            aria-label="Notifications"
          >
            <Bell size={20} className="text-text-secondary" aria-hidden="true" />
          </button>

          {/* User dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center gap-2 p-2 hover:bg-background-elevated rounded-lg transition-colors min-h-[44px]"
              aria-expanded={showDropdown}
              aria-haspopup="true"
              aria-label="User menu"
            >
              <div className="w-8 h-8 bg-accent-primary rounded-full flex items-center justify-center">
                <User size={16} className="text-white" aria-hidden="true" />
              </div>
            </button>

            {showDropdown && (
              <div
                className="absolute right-0 mt-2 w-48 bg-background-elevated border border-border rounded-lg shadow-lg py-1 z-50"
                role="menu"
                aria-label="User options"
              >
                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-text-secondary hover:bg-background-card hover:text-text-primary min-h-[44px]"
                  role="menuitem"
                >
                  <LogOut size={16} aria-hidden="true" />
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
