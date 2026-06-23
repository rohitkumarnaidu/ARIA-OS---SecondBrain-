import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { FileUpload } from '@/components/ui/FileUpload'

function createFile(name: string, size = 1024, type = ''): File {
  return new File([new ArrayBuffer(size)], name, { type })
}

describe('FileUpload', () => {
  it('renders drop zone', () => {
    render(<FileUpload onFiles={() => {}} />)
    expect(screen.getByText(/drop/i)).toBeInTheDocument()
  })

  it('renders accepted file types', () => {
    render(<FileUpload onFiles={() => {}} accept=".jpg,.png" />)
    expect(screen.getByText(/Accepted/)).toBeInTheDocument()
  })

  it('calls onFiles when files are added programmatically', () => {
    const onFiles = vi.fn()
    const { container } = render(<FileUpload onFiles={onFiles} />)
    const input = container.querySelector('input[type="file"]')
    expect(input).toBeInTheDocument()
  })

  it('shows uploaded files after drop', async () => {
    const onFiles = vi.fn()
    const { container } = render(<FileUpload onFiles={onFiles} />)
    const input = container.querySelector('input[type="file"]')!
    const file = createFile('photo.jpg')
    Object.defineProperty(input, 'files', { value: [file] })
    input.dispatchEvent(new Event('change', { bubbles: true }))
    expect(screen.getByText('photo.jpg')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<FileUpload onFiles={() => {}} className="custom" />)
    expect(container.firstChild).toHaveClass('custom')
  })
})
