'use client'

import { memo, useState, useCallback, useRef } from 'react'
import { Mic, MicOff, Loader2 } from 'lucide-react'

interface VoiceInputProps {
  onTranscript: (text: string) => void
  disabled?: boolean
}

interface SpeechRecognitionEvent {
  results: SpeechRecognitionResultList
}

interface SpeechRecognitionResultList {
  [index: number]: SpeechRecognitionResult
  length: number
}

interface SpeechRecognitionResult {
  [index: number]: SpeechRecognitionAlternative
  length: number
  isFinal?: boolean
}

interface SpeechRecognitionAlternative {
  transcript: string
  confidence: number
}

interface SpeechRecognition extends EventTarget {
  lang: string
  interimResults: boolean
  maxAlternatives: number
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: (() => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition
}

export const VoiceInput = memo(function VoiceInput({ onTranscript, disabled }: VoiceInputProps) {
  const [listening, setListening] = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const recognitionRef = useRef<SpeechRecognition | null>(null)

  const toggle = useCallback(() => {
    if (listening) {
      recognitionRef.current?.stop()
      setListening(false)
      return
    }

    const win = window as unknown as { SpeechRecognition?: SpeechRecognitionConstructor; webkitSpeechRecognition?: SpeechRecognitionConstructor }
    const SpeechRecognitionCtor = win.SpeechRecognition || win.webkitSpeechRecognition
    if (!SpeechRecognitionCtor) {
      onTranscript('[Voice not supported in this browser]')
      return
    }

    const recognition = new SpeechRecognitionCtor()
    recognition.lang = 'en-US'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setTranscribing(true)
      onTranscript(transcript)
      setTimeout(() => setTranscribing(false), 1000)
    }

    recognition.onerror = () => {
      setListening(false)
    }

    recognition.onend = () => {
      setListening(false)
    }

    recognitionRef.current = recognition
    recognition.start()
    setListening(true)
  }, [listening, onTranscript])

  return (
    <button
      onClick={toggle}
      disabled={disabled}
      className={`p-2 rounded-lg transition-all ${
        listening
          ? 'bg-accent-error/20 text-accent-error animate-pulse-glow'
          : transcribing
          ? 'bg-accent-primary/20 text-accent-primary'
          : 'text-text-tertiary hover:text-text-primary hover:bg-background-elevated'
      } disabled:opacity-50`}
      aria-label={listening ? 'Stop recording' : 'Start voice input'}
    >
      {transcribing ? (
        <Loader2 size={16} className="animate-spin" />
      ) : listening ? (
        <MicOff size={16} />
      ) : (
        <Mic size={16} />
      )}
    </button>
  )
})
