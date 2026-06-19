import { describe, it, expect, vi } from 'vitest'
import { render, screen, act, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Popover } from '@/components/ui/Popover'

describe('Popover', () => {
  it('opens on trigger click', async () => {
    const user = userEvent.setup()
    render(
      <Popover trigger={<button>Open</button>}>
        <p>Popover content</p>
      </Popover>,
    )
    await user.click(screen.getByText('Open'))
    expect(screen.getByText('Popover content')).toBeInTheDocument()
  })

  it('is closed by default', () => {
    render(
      <Popover trigger={<button>Open</button>}>
        <p>Hidden content</p>
      </Popover>,
    )
    expect(screen.queryByText('Hidden content')).not.toBeInTheDocument()
  })

  it('closes on click outside', async () => {
    const user = userEvent.setup()
    render(
      <Popover trigger={<button>Open</button>}>
        <p>Content</p>
      </Popover>,
    )
    await user.click(screen.getByText('Open'))
    expect(screen.getByText('Content')).toBeInTheDocument()

    fireEvent.mouseDown(document.body)
    expect(screen.queryByText('Content')).not.toBeInTheDocument()
  })

  it('controlled open state', () => {
    const { rerender } = render(
      <Popover trigger={<button>Open</button>} open={true}>
        <p>Content</p>
      </Popover>,
    )
    expect(screen.getByText('Content')).toBeInTheDocument()

    rerender(
      <Popover trigger={<button>Open</button>} open={false}>
        <p>Content</p>
      </Popover>,
    )
    expect(screen.queryByText('Content')).not.toBeInTheDocument()
  })
})
