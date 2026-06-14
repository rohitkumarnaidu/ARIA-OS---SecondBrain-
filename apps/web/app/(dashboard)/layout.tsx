import { Sidebar, Navbar, OfflineBanner, SkipLink } from '@/components/layout'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <SkipLink />
      <Sidebar />
      <div className="flex-1 ml-60">
        <OfflineBanner />
        <Navbar />
        <main id="main-content" className="pt-20 px-6 pb-6" tabIndex={-1}>
          {children}
        </main>
      </div>
    </div>
  )
}
