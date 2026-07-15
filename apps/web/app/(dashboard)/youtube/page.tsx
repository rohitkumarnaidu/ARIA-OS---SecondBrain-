'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useYoutubeStore } from '@/lib/stores'
import { showError } from '@/lib/toast'
import { Plus, Youtube, Trash2, Play, X, ExternalLink } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { createLogger } from '@/lib/utils/logger'

export default function YouTubePage() {
  const { user, loading: authLoading } = useAuth()
  const { items: videos, loading, error, fetch, create, update, remove } = useYoutubeStore()
  const logger = createLogger('YoutubePage')
  const [showAddModal, setShowAddModal] = useState(false)
  const [mounted, setMounted] = useState(false)

  const [newVideo, setNewVideo] = useState({ url: '', title: '' })

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (user) fetch()
  }, [user, fetch])

  useEffect(() => {
    if (error) showError(error)
  }, [error])

  const handleAddVideo = async () => {
    if (!newVideo.url.trim()) return
    const videoId = extractVideoId(newVideo.url)
    const title = newVideo.title || `Video ${videos.length + 1}`
    logger.info('Adding video', { title, videoId })

    try {
      await create({
        url: newVideo.url,
        title: title,
        thumbnail_url: videoId ? `https://img.youtube.com/vi/${videoId}/mqdefault.jpg` : undefined,
        status: 'pending',
      })
      logger.info('Video added successfully', { title })
      setNewVideo({ url: '', title: '' })
      setShowAddModal(false)
    } catch (err) {
      logger.error('Failed to add video', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const extractVideoId = (url: string) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)/)
    return match ? match[1] : null
  }

  const handleDelete = async (id: string) => {
    logger.info('Deleting video', { id })
    try {
      await remove(id)
      logger.info('Video deleted successfully', { id })
    } catch (err) {
      logger.error('Failed to delete video', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const handleUpdateStatus = async (id: string, status: string) => {
    logger.info('Updating video status', { id, status })
    try {
      await update(id, { status })
      logger.info('Video status updated successfully', { id, status })
    } catch (err) {
      logger.error('Failed to update video status', { error: err instanceof Error ? err.message : String(err) })
    }
  }

  const pendingVideos = videos.filter(v => v.status === 'pending')
  const watchedVideos = videos.filter(v => v.status === 'watched')

  if (!mounted) return <div className="min-h-screen bg-[var(--bg-page)]" />
  if (authLoading || loading) return (
    <div className="flex items-center justify-center h-64" role="status" aria-label="Loading">
      <div className="animate-pulse-glow w-12 h-12 border-2 border-accent-primary border-t-transparent rounded-full" />
      <span className="sr-only">Loading...</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-text-primary text-gradient">YouTube Vault</h1>
          <p className="text-text-secondary">Save and track your learning videos</p>
        </div>
        <Button variant="primary" className="flex items-center gap-2" onClick={() => setShowAddModal(true)}>
          <Plus size={20} /> Add Video
        </Button>
      </motion.div>

      <div className="grid grid-cols-3 gap-4">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="card border border-border rounded-xl p-4"
        >
          <div className="text-2xl font-bold text-text-primary">{pendingVideos.length}</div>
          <div className="text-text-secondary text-sm">To Watch</div>
        </motion.div>
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="card border border-border rounded-xl p-4"
        >
          <div className="text-2xl font-bold text-text-primary">{watchedVideos.length}</div>
          <div className="text-text-secondary text-sm">Watched</div>
        </motion.div>
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="card border border-border rounded-xl p-4"
        >
          <div className="text-2xl font-bold text-text-primary">{videos.length}</div>
          <div className="text-text-secondary text-sm">Total Saved</div>
        </motion.div>
      </div>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <AnimatePresence>
          {videos.map((video, index) => (
            <motion.div
              key={video.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ delay: index * 0.1 }}
              className="bg-background-card border border-border rounded-xl overflow-hidden"
            >
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
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>

      {videos.length === 0 && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Youtube size={48} className="text-text-muted mx-auto mb-3" />
          <p className="text-text-secondary">No videos saved yet</p>
        </motion.div>
      )}

      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-background-card border border-border rounded-xl p-6 w-full max-w-md"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-text-primary">Add YouTube Video</h2>
                <button onClick={() => setShowAddModal(false)}><X size={24} className="text-text-muted" /></button>
              </div>
              <div className="space-y-4">
                <div><label htmlFor="video-url" className="block text-text-secondary text-sm mb-1">YouTube URL *</label><input id="video-url" type="url" value={newVideo.url} onChange={e => setNewVideo({ ...newVideo, url: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="https://youtube.com/watch?v=..." /></div>
                <div><label htmlFor="video-title" className="block text-text-secondary text-sm mb-1">Title</label><input id="video-title" type="text" value={newVideo.title} onChange={e => setNewVideo({ ...newVideo, title: e.target.value })} className="w-full bg-background-dark border border-border rounded-lg px-4 py-2 text-text-primary" placeholder="Video title" /></div>
                <button onClick={handleAddVideo} className="w-full bg-accent-primary text-white py-2 rounded-lg hover:bg-accent-primary/90">Save Video</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}