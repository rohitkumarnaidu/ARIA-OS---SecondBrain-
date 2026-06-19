import { describe, it, expect } from 'vitest'
import { cn } from '@/components/ui/utils'

describe('cn', () => {
  it('merges class names correctly', () => {
    expect(cn('px-4', 'py-2')).toBe('px-4 py-2')
    expect(cn('btn', 'btn-primary')).toBe('btn btn-primary')
  })

  it('handles conditional class objects', () => {
    expect(cn('base', { 'is-active': true, 'is-hidden': false })).toBe('base is-active')
  })

  it('handles undefined and null values', () => {
    expect(cn('px-4', undefined, null, 'py-2')).toBe('px-4 py-2')
    expect(cn(undefined, null)).toBe('')
  })

  it('resolves Tailwind conflicts (last class wins)', () => {
    expect(cn('px-4', 'px-6')).toBe('px-4 px-6')
    expect(cn('text-red-500', 'text-blue-500')).toBe('text-red-500 text-blue-500')
  })
})
