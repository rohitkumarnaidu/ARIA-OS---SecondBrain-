import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConfidenceBadge } from '@/components/ai/ConfidenceBadge'

describe('ConfidenceBadge', () => {
  it('shows green for >=85', () => {
    render(<ConfidenceBadge value={90} label="High" />)
    expect(screen.getByText('90%')).toBeInTheDocument()
    expect(screen.getByText('High')).toBeInTheDocument()
    expect(screen.getByText('Confidence: 90% - High confidence')).toBeInTheDocument()
  })

  it('shows amber for 60-84', () => {
    render(<ConfidenceBadge value={72} label="Medium" />)
    expect(screen.getByText('72%')).toBeInTheDocument()
    expect(screen.getByText('Medium')).toBeInTheDocument()
    expect(screen.getByText('Confidence: 72% - Medium confidence')).toBeInTheDocument()
  })

  it('shows red for <60', () => {
    render(<ConfidenceBadge value={45} label="Low" />)
    expect(screen.getByText('45%')).toBeInTheDocument()
    expect(screen.getByText('Low')).toBeInTheDocument()
    expect(screen.getByText('Confidence: 45% - Low confidence')).toBeInTheDocument()
  })

  it('renders without label', () => {
    render(<ConfidenceBadge value={88} />)
    expect(screen.getByText('88%')).toBeInTheDocument()
    expect(screen.getByText('Confidence: 88% - High confidence')).toBeInTheDocument()
  })

  it('clamps value to 0-100 range', () => {
    render(<ConfidenceBadge value={150} />)
    expect(screen.getByText('100%')).toBeInTheDocument()
  })

  it('clamps value below 0', () => {
    render(<ConfidenceBadge value={-10} />)
    expect(screen.getByText('0%')).toBeInTheDocument()
  })
})
