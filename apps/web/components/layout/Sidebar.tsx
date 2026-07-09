'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'
import {
  LayoutDashboard, CheckSquare, BookOpen, Youtube,
  FileText, Lightbulb, Target, Radar, Wallet,
  FolderKanban, GraduationCap, Moon, Clock, MessageCircle, Zap,
} from 'lucide-react'

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare },
  { name: 'Courses', href: '/courses', icon: BookOpen },
  { name: 'YouTube', href: '/youtube', icon: Youtube },
  { name: 'Resources', href: '/resources', icon: FileText },
  { name: 'Ideas', href: '/ideas', icon: Lightbulb },
  { name: 'Goals', href: '/goals', icon: Target },
  { name: 'Opportunities', href: '/opportunities', icon: Radar },
  { name: 'Income', href: '/income', icon: Wallet },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Academics', href: '/academics', icon: GraduationCap },
  { name: 'Habits', href: '/habits', icon: Moon },
  { name: 'Sleep', href: '/sleep', icon: Moon },
  { name: 'Time', href: '/time', icon: Clock },
  { name: 'Chat', href: '/chat', icon: MessageCircle },
  { name: 'Automation', href: '/automation', icon: Zap },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside
      className="w-60 h-screen bg-background-card border-r border-border fixed left-0 top-0 overflow-y-auto z-30"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="p-4">
        <Link href="/dashboard" className="block mb-6">
          <h1 className="text-xl font-bold text-accent-primary">Second Brain OS</h1>
        </Link>

        <nav aria-label="Module navigation">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={clsx(
                      'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors min-h-[44px]',
                      isActive
                        ? 'bg-accent-primary/10 text-accent-primary'
                        : 'text-text-secondary hover:bg-background-elevated hover:text-text-primary',
                    )}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <Icon size={20} aria-hidden="true" />
                    <span className="text-sm font-medium">{item.name}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
      </div>
    </aside>
  )
}
