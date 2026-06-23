'use client'

import { memo,  useState, useRef, useCallback, type DragEvent, type ChangeEvent  } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, X, File } from 'lucide-react'
import { cn } from './utils'

interface FileUploadProps {
  onFiles: (files: File[]) => void
  accept?: string
  multiple?: boolean
  maxSize?: number
  maxFiles?: number
  className?: string
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const FileUpload = memo(function FileUpload({ onFiles, accept, multiple = true, maxSize, maxFiles, className }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [files, setFiles] = useState<{ file: File; error?: string }[]>([])
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validate = useCallback(
    (incoming: File[]): File[] => {
      const remaining = maxFiles ? maxFiles - files.length : Infinity
      if (remaining <= 0) { setError(`Maximum ${maxFiles} file(s) allowed.`); return [] }
      if (incoming.length > remaining) { setError(`Only ${remaining} more file(s) allowed.`); return incoming.slice(0, remaining) }
      setError(null)
      return incoming.filter((f) => {
        if (maxSize && f.size > maxSize) {
          setFiles((prev) => [...prev, { file: f, error: `File exceeds ${formatSize(maxSize)}` }])
          return false
        }
        return true
      })
    },
    [files.length, maxFiles, maxSize],
  )

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      setIsDragging(false)
      const valid = validate(Array.from(e.dataTransfer.files))
      if (valid.length > 0) {
        setFiles((prev) => {
          const next = [...prev, ...valid.map((file) => ({ file }))]
          onFiles(next.map((f) => f.file))
          return next
        })
      }
    },
    [validate, onFiles],
  )

  const handleInput = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const valid = validate(Array.from(e.target.files ?? []))
      if (valid.length > 0) {
        setFiles((prev) => {
          const next = [...prev, ...valid.map((file) => ({ file }))]
          onFiles(next.map((f) => f.file))
          return next
        })
      }
      e.target.value = ''
    },
    [validate, onFiles],
  )

  const removeFile = useCallback(
    (index: number) => {
      setFiles((prev) => {
        const next = prev.filter((_, i) => i !== index)
        onFiles(next.map((f) => f.file))
        return next
      })
    },
    [onFiles],
  )

  return (
    <div className={cn('space-y-3', className)}>
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={cn(
          'flex flex-col items-center justify-center gap-3 p-8 rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]',
          isDragging
            ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/5'
            : 'border-border hover:border-border-light hover:bg-[var(--glass-heavy)]',
        )}
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); inputRef.current?.click() } }}
        role="button"
        aria-label="Upload files"
      >
        <motion.div
          animate={isDragging ? { scale: 1.1, y: -4 } : { scale: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
        >
          <Upload size={32} style={{ color: isDragging ? 'var(--accent-primary)' : 'var(--text-tertiary)' }} />
        </motion.div>
        <div className="text-center">
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
            {isDragging ? 'Drop files here' : 'Drag & drop files or click to browse'}
          </p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
            {accept ? `Accepted: ${accept}` : 'All files supported'}
            {maxSize && ` · Max: ${formatSize(maxSize)}`}
          </p>
        </div>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleInput}
        className="hidden"
        aria-hidden="true"
      />

      {error && (
        <p className="text-sm" style={{ color: 'var(--accent-error)' }}>{error}</p>
      )}

      <AnimatePresence>
        {files.length > 0 && (
          <motion.ul
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            {files.map((entry, index) => (
              <motion.li
                key={`${entry.file.name}-${index}`}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 8 }}
                className="flex items-center gap-3 px-3 py-2 rounded-lg"
                style={{ background: 'var(--surface-secondary)', border: '1px solid var(--border)' }}
              >
                <File size={16} style={{ color: 'var(--accent-primary)', flexShrink: 0 }} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate" style={{ color: 'var(--text-primary)' }}>{entry.file.name}</p>
                  <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{formatSize(entry.file.size)}</p>
                  {entry.error && (
                    <p className="text-xs" style={{ color: 'var(--accent-error)' }}>{entry.error}</p>
                  )}
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="flex items-center justify-center rounded-md transition-colors hover:bg-[var(--glass-heavy)]"
                  style={{ width: '28px', height: '28px', color: 'var(--text-tertiary)' }}
                  aria-label={`Remove ${entry.file.name}`}
                >
                  <X size={14} />
                </button>
              </motion.li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  )
})

FileUpload.displayName = 'FileUpload'

export { FileUpload }
export type { FileUploadProps }
