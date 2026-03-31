'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Send, Loader2, Bot, User, MessageCircle } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export default function ChatPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [mounted, setMounted] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
    if (user) {
      fetchMessages()
    }
  }, [user, authLoading, router])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchMessages = async () => {
    const { data, error } = await supabase
      .from('chat_messages')
      .select('*')
      .order('created_at', { ascending: true })
      .limit(50)
    
    if (!error && data) {
      setMessages(data)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return
    
    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    // Add user message to UI immediately
    const tempUserMsg: Message = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMsg])

    try {
      // Call backend API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      })

      const data = await response.json()

      // Add assistant response
      const assistantMsg: Message = {
        id: 'assistant-' + Date.now(),
        role: 'assistant',
        content: data.response || "I'm here to help! Try connecting the backend to enable AI responses.",
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMsg])

      // Save to database
      await supabase.from('chat_messages').insert([
        { role: 'user', content: userMessage },
        { role: 'assistant', content: assistantMsg.content }
      ])
    } catch (error) {
      // If API fails, show demo response
      const demoResponse = getDemoResponse(userMessage)
      const assistantMsg: Message = {
        id: 'demo-' + Date.now(),
        role: 'assistant',
        content: demoResponse,
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMsg])
    }

    setLoading(false)
  }

  const getDemoResponse = (message: string): string => {
    const lower = message.toLowerCase()
    
    if (lower.includes('task') || lower.includes('todo')) {
      return "I can help you manage tasks! Go to the Tasks page to add, view, or complete tasks. Would you like me to create a task for you?"
    }
    if (lower.includes('goal') || lower.includes('roadmap')) {
      return "Goals help you plan your path to success. Check the Goals page to create and track your goals. What do you want to achieve?"
    }
    if (lower.includes('course') || lower.includes('learn')) {
      return "Track your learning progress in the Courses section. Add courses from Udemy, Coursera, NPTEL, or YouTube with deadlines to stay on track!"
    }
    if (lower.includes('idea') || lower.includes('startup')) {
      return "Capture your startup ideas in the Ideas vault! I'll help you track and validate them. What's your latest idea?"
    }
    if (lower.includes('help')) {
      return "I'm ARIA, your AI assistant! I can help with tasks, goals, courses, ideas, and more. Connect the backend to unlock full AI capabilities. What do you need help with?"
    }
    
    return "I'm here to help you stay productive! Ask me about tasks, goals, courses, ideas, or anything else. Connect the backend to enable full AI responses!"
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!mounted || authLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin w-8 h-8 text-accent-primary" />
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-text-primary">Chat with ARIA</h1>
        <p className="text-text-secondary">Your personal AI assistant</p>
      </div>

      {/* Messages */}
      <div className="flex-1 bg-background-card border border-border rounded-xl p-4 overflow-y-auto mb-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-full bg-accent-primary/20 flex items-center justify-center mb-4">
              <Bot size={32} className="text-accent-primary" />
            </div>
            <h2 className="text-xl font-semibold text-text-primary mb-2">Hi, I'm ARIA!</h2>
            <p className="text-text-secondary max-w-md">
              Your personal AI assistant. Ask me about tasks, goals, courses, ideas, or anything else.
              Connect the backend to enable full AI capabilities!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map(msg => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-2xl px-4 py-2 ${
                    msg.role === 'user'
                      ? 'bg-accent-primary text-white'
                      : 'bg-background-elevated text-text-primary'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {msg.role === 'assistant' ? (
                      <Bot size={14} className="text-accent-primary" />
                    ) : (
                      <User size={14} className="text-white" />
                    )}
                    <span className="text-xs opacity-70">
                      {msg.role === 'assistant' ? 'ARIA' : 'You'}
                    </span>
                  </div>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-background-elevated rounded-2xl px-4 py-2">
                  <div className="flex items-center gap-2">
                    <Bot size={14} className="text-accent-primary" />
                    <span className="text-sm text-text-secondary">Thinking...</span>
                    <Loader2 className="animate-spin w-4 h-4" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Ask ARIA anything..."
          className="flex-1 bg-background-card border border-border rounded-xl px-4 py-3 text-text-primary placeholder:text-text-muted focus:border-accent-primary"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="bg-accent-primary text-white px-6 rounded-xl hover:bg-accent-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 className="animate-spin" /> : <Send size={20} />}
        </button>
      </div>
    </div>
  )
}