'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Youtube, Trash2, Play, X, ExternalLink } from 'lucide-react'

interface Video {
  id: string
  url: string
  title: string
  thumbnail_url?: string
  ai_summary?: string
  status: string
  created_at: string
}

export default function YouTubePage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [newVideo, setNewVideo] = useState({ url: '', title: '' })

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (!authLoading && !user) router.push('/login')
    if (user) fetchVideos()
  }, [user, authLoading, router])

  const fetchVideos = async () => {
    setLoading(true)
    const { data } = await supabase.from('videos').select('*').order('created_at', { ascending: false })
    if (data) setVideos(data)
    setLoading(false)
  }

  const handleAddVideo = async () => {
    if (!newVideo.url.trim()) return
    const videoId = extractVideoId(newVideo.url)
    const title = newVideo.title || `Video ${videos.length + 1}`
    
    await supabase.from('videos').insert({
      url: newVideo.url,
      title: title,
      thumbnail_url: videoId ? `https://img.youtube.com/vi/${videoId}/mqdefault.jpg` : null,
      status: 'pending',
    })
    
    setNewVideo({ url: '', title: '' })
    setShowAddModal(false)
    fetchVideos()
  }

  const extractVideoId = (url: string) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)/)
    return match ? match[1] : null
  }

  const handleDelete = async (id: string) => {
    await supabase.from('videos').delete().eq('id', id)
    setVideos(videos.filter(v => v.id !== id))
  }

  const handleUpdateStatus = async (id: string, status: string) => {
    await supabase.from('videos').update({ status }).eq('id', id)
    setVideos(videos.map(v => v.id === id ? { ...v, status } : v))
  }

  const pendingVideos = videos.filter(v => v.status === 'pending')
  const watchedVideos = videos.filter(v => v.status === 'watched')

  if (!mounted || authLoading || loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">YouTube Vault</h1>
          <p className="text-text-secondary">Save and track your learning videos</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="flex items-center gap-2 bg-accent-primary text-white px-4 py-2 rounded-lg hover:bg-accent-primary/90">
          <Plus size={20} /> Add Video
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{pendingVideos.length}</div><div className="text-text-secondary text-sm">To Watch</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{watchedVideos.length}</div><div className="text-text-secondary text-sm">Watched</div></div>
        <div className="bg-background-card border border-border rounded-xl p-4"><div className="text-2xl font-bold text-text-primary">{videos.length}</div><div className="text-text-secondary text-sm">Total Saved</div></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {videos.map(video => (
          <div key={video.id} className="bg-background-card border border-border rounded-xl overflow-hidden">
            {video.thumbnail_url && <img src={video.thumbnail_url} alt={video.title} className="w-full h-40 object-cover" />}
            <div className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-text-primary font-semibold line-clamp-2">{video.title}</h3>
                <button onClick={() => handleDelete(video.id)}><Trash2 size={16} className="text-accent-error" /></button>
              </div>
              <div className="flex items-center justify-between">
                <span className={`text-xs px-2 py-1 rounded ${video.status === 'watched' ? 'bg-accent-secondary text-white' : 'bg-accent-warning text-black'}`}>{video.status}</span>
                <div className="flex gap-2">
                  <a href={video.url} target="_blank" rel="noopener noreferrer" className="p-1 hover:bg-background-elevated rounded"><ExternalLink size={16} className="text-text-muted" /></a>
                  <button onClick={() => handleUpdateStatus(video.id, video.status === 'watched' ? 'pending' : 'watched')} className="p-1 hover:bg-background-elevated rounded"><Play size={16} className="text-accent-secondary" /></button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {videos.length === 0 && <div className="text-center py-12"><Youtube size={48} className="text-text-muted mx-auto mb-3" /><p className="text-text-secondary">No videos saved yet</p></div>}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Add YouTube Video</h2>
              <button onClick={() => setShowAddModal(false)}><X size={24} className="text-text-muted" /></button>
            </div>
            <div className="space-y-4">
              <div><label className="block text-text-secondary text-sm mb-1">YouTube URL *</label><input type="url" value={newVideo.url} onChange={e => setNewVideo({ ...newVideo, url: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="https://youtube.com/watch?v=..." /></div>
              <div><label className="block text-text-secondary text-sm mb-1">Title</label><input type="text" value={newVideo.title} onChange={e => setNewVideo({ ...newVideo, title: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="Video title" /></div>
              <button onClick={handleAddVideo} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Save Video</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}