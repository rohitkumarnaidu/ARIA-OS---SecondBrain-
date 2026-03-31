import Sidebar from '@/components/Sidebar'
import Navbar from '@/components/Navbar'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 ml-60">
        <Navbar />
        <main className="pt-20 px-6 pb-6">
          {children}
        </main>
      </div>
    </div>
  )
}