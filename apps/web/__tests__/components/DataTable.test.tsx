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
})
