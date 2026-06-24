import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DataTable } from '@/components/ui/DataTable'
import { createColumnHelper } from '@tanstack/react-table'

interface TestRow {
  id: string
  name: string
  email: string
}

const columnHelper = createColumnHelper<TestRow>()

const columns = [
  columnHelper.accessor('name', { header: 'Name' }),
  columnHelper.accessor('email', { header: 'Email' }),
]

const data: TestRow[] = [
  { id: '1', name: 'Alice', email: 'alice@test.com' },
  { id: '2', name: 'Bob', email: 'bob@test.com' },
]

describe('DataTable', () => {
  it('renders column headers', () => {
    render(<DataTable columns={columns} data={data} />)
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
  })

  it('renders data rows', () => {
    render(<DataTable columns={columns} data={data} />)
    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
  })

  it('renders empty state', () => {
    render(<DataTable columns={columns} data={[]} />)
    expect(screen.getByText('No results found')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<DataTable columns={columns} data={data} className="custom" />)
    expect(container.firstChild).toHaveClass('custom')
  })

  describe('Edge Cases', () => {
    it('renders with single row', () => {
      render(<DataTable columns={columns} data={[data[0]]} />)
      expect(screen.getByText('Alice')).toBeInTheDocument()
      expect(screen.queryByText('Bob')).not.toBeInTheDocument()
    })

    it('renders with many rows', () => {
      const manyRows = Array.from({ length: 50 }, (_, i) => ({
        id: String(i), name: `User ${i}`, email: `user${i}@test.com`,
      }))
      render(<DataTable columns={columns} data={manyRows} pageSize={50} />)
      expect(screen.getByText('User 0')).toBeInTheDocument()
      expect(screen.getByText('User 49')).toBeInTheDocument()
    })

    it('has accessible table role', () => {
      render(<DataTable columns={columns} data={data} />)
      expect(screen.getByRole('table')).toBeInTheDocument()
    })

    it('renders with long cell content', () => {
      const longData = [{ id: '1', name: 'L'.repeat(100), email: 'long@test.com' }]
      render(<DataTable columns={columns} data={longData} />)
      const cell = screen.getByText('L'.repeat(100))
      expect(cell).toBeInTheDocument()
    })

    it('empty state has role="status" or appropriate messaging', () => {
      render(<DataTable columns={columns} data={[]} />)
      expect(screen.getByText('No results found')).toBeInTheDocument()
    })
  })
})
