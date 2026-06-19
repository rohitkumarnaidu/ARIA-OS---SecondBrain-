import '@/app/globals.css'
import type { Metadata } from 'next'
import { Syne, DM_Sans, JetBrains_Mono } from 'next/font/google'
import { Toaster } from 'sonner'
import { ThemeProvider } from '@/components/theme'
import { SkipLink } from '@/components/layout/SkipLink'

const syne = Syne({
  subsets: ['latin'],
  variable: '--font-syne',
  display: 'swap',
})

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-dm-sans',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'ARIA OS | Your Second Brain',
  description: 'Personal AI productivity system for BTech CSE students',
  manifest: '/manifest.json',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${syne.variable} ${dmSans.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{
          __html: `(function(){try{var t=localStorage.getItem('aria-theme')||'dark',a=localStorage.getItem('aria-accent')||'indigo',c=localStorage.getItem('aria-contrast');document.documentElement.classList.add(t);document.documentElement.setAttribute('data-accent',a);if(c==='high')document.documentElement.classList.add('high-contrast')}catch(e){}})()`
        }} />
      </head>
      <body className="font-body antialiased">
        <SkipLink />
        <ThemeProvider>
          {children}
        </ThemeProvider>
        <footer role="contentinfo" className="sr-only">
          <p>ARIA OS Second Brain — version 2.4.0-stable</p>
        </footer>
        <Toaster
          position="bottom-right"
          duration={4000}
          toastOptions={{
            style: {
              background: 'var(--surface-primary)',
              color: 'var(--foreground)',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              fontSize: '14px',
            },
          }}
        />
      </body>
    </html>
  )
}
