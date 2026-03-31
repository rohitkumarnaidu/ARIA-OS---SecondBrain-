'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, CheckSquare, BookOpen, Youtube, 
  FileText, Lightbulb, Target, Radar, Wallet, 
  FolderKanban, GraduationCap, Moon, Clock, MessageCircle
} from 'lucide-react'
import clsx from 'clsx'

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
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-60 h-screen bg-background-card border-r border-border fixed left-0 top-0 overflow-y-auto">
      <div className="p-4">
        <h1 className="text-xl font-bold text-accent-primary mb-6">Second Brain OS</h1>
        
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                  isActive
                    ? 'bg-accent-primary/10 text-accent-primary'
                    : 'text-text-secondary hover:bg-background-elevated hover:text-text-primary'
                )}
              >
                <Icon size={20} />
                <span className="text-sm font-medium">{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}