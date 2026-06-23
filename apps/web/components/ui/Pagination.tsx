'use client'

import { memo,  useMemo  } from 'react'
import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react'
import { cn } from './utils'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  siblingCount?: number
  className?: string
}

function generatePageNumbers(current: number, total: number, siblings: number): (number | 'ellipsis')[] {
  const totalNumbers = siblings * 2 + 5
  if (total <= totalNumbers) return Array.from({ length: total }, (_, i) => i + 1)

  const leftSibling = Math.max(current - siblings, 1)
  const rightSibling = Math.min(current + siblings, total)
  const showLeftEllipsis = leftSibling > 2
  const showRightEllipsis = rightSibling < total - 1

  if (!showLeftEllipsis && showRightEllipsis) {
    const leftCount = 3 + 2 * siblings
    return [...Array.from({ length: leftCount }, (_, i) => i + 1), 'ellipsis', total]
  }

  if (showLeftEllipsis && !showRightEllipsis) {
    const rightCount = 3 + 2 * siblings
    return [1, 'ellipsis', ...Array.from({ length: rightCount }, (_, i) => total - rightCount + i + 1)]
  }

  return [1, 'ellipsis', ...Array.from({ length: rightSibling - leftSibling + 1 }, (_, i) => leftSibling + i), 'ellipsis', total]
}

const Pagination = memo(function Pagination({ currentPage, totalPages, onPageChange, siblingCount = 1, className }: PaginationProps) {
  const pages = useMemo(() => generatePageNumbers(currentPage, totalPages, siblingCount), [currentPage, totalPages, siblingCount])

  const btnBase = cn(
    'inline-flex items-center justify-center h-9 w-9 rounded-lg text-sm transition-all duration-200',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--background)]',
    'disabled:pointer-events-none disabled:opacity-50',
  )

  return (
    <nav aria-label="Pagination" className={cn('flex items-center gap-1', className)}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className={cn(btnBase, 'text-text-secondary hover:bg-[var(--glass-heavy)]')}
        aria-label="Previous page"
      >
        <ChevronLeft size={16} />
      </button>

      {pages.map((page, idx) =>
        page === 'ellipsis' ? (
          <span key={`ellipsis-${idx}`} className="flex items-center justify-center h-9 w-9 text-text-tertiary">
            <MoreHorizontal size={16} />
          </span>
        ) : (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            disabled={page === currentPage}
            className={cn(
              btnBase,
              page === currentPage
                ? 'bg-[var(--accent-primary)] text-white shadow-glow-sm cursor-default'
                : 'text-text-secondary hover:bg-[var(--glass-heavy)] hover:text-text-primary',
            )}
            aria-label={`Page ${page}`}
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </button>
        ),
      )}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className={cn(btnBase, 'text-text-secondary hover:bg-[var(--glass-heavy)]')}
        aria-label="Next page"
      >
        <ChevronRight size={16} />
      </button>
    </nav>
  )
})

Pagination.displayName = 'Pagination'

export { Pagination }
export type { PaginationProps }
