export default function RootLoading() {
  return (
    <div className="min-h-screen bg-background-dark flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-text-secondary text-sm">Loading ARIA OS...</p>
      </div>
    </div>
  )
}
