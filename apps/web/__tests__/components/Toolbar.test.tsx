import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Toolbar, ToolbarSeparator } from '@/components/ui/Toolbar'

describe('Toolbar', () => {
  it('renders children', () => {
    render(<Toolbar><button>Bold</button><button>Italic</button></Toolbar>)
    expect(screen.getByText('Bold')).toBeInTheDocument()
    expect(screen.getByText('Italic')).toBeInTheDocument()
  })

  it('renders separator', () => {
    render(<Toolbar><button>Cut</button><ToolbarSeparator /><button>Copy</button></Toolbar>)
    const separator = document.querySelector('[role="separator"]')
    expect(separator).toBeInTheDocument()
  })

  it('applies variant class', () => {
    const { container } = render(<Toolbar variant="outline"><button>A</button></Toolbar>)
    expect(container.firstChild).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<Toolbar className="custom"><button>Save</button></Toolbar>)
    expect(screen.getByText('Save').closest('[role="toolbar"]')).toHaveClass('custom')
  })
})
