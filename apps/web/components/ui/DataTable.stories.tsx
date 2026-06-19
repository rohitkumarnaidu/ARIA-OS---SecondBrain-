import type { Meta, StoryObj } from '@storybook/react'
import { type ColumnDef } from '@tanstack/react-table'
import { DataTable } from './DataTable'

interface User {
  id: string
  name: string
  email: string
  role: string
  status: 'active' | 'inactive'
}

const columns: ColumnDef<unknown>[] = [
  { accessorKey: 'name', header: 'Name', enableSorting: true },
  { accessorKey: 'email', header: 'Email', enableSorting: true },
  { accessorKey: 'role', header: 'Role', enableSorting: true },
  {
    accessorKey: 'status',
    header: 'Status',
    enableSorting: true,
    cell: ({ row }) => {
      const original = row.original as { status: string }
      return (
        <span
          style={{
            color: original.status === 'active' ? 'var(--accent-neon)' : 'var(--accent-warning)',
          }}
        >
          {original.status}
        </span>
      )
    },
  },
]

const data: User[] = [
  { id: '1', name: 'Alice Chen', email: 'alice@example.com', role: 'Admin', status: 'active' },
  { id: '2', name: 'Bob Martinez', email: 'bob@example.com', role: 'Editor', status: 'active' },
  { id: '3', name: 'Charlie Kim', email: 'charlie@example.com', role: 'Viewer', status: 'inactive' },
  { id: '4', name: 'Diana Lopez', email: 'diana@example.com', role: 'Editor', status: 'active' },
  { id: '5', name: 'Ethan Park', email: 'ethan@example.com', role: 'Admin', status: 'active' },
  { id: '6', name: 'Fiona Singh', email: 'fiona@example.com', role: 'Viewer', status: 'inactive' },
  { id: '7', name: 'George Brown', email: 'george@example.com', role: 'Editor', status: 'active' },
  { id: '8', name: 'Hannah Lee', email: 'hannah@example.com', role: 'Viewer', status: 'active' },
  { id: '9', name: 'Ivan Taylor', email: 'ivan@example.com', role: 'Admin', status: 'inactive' },
  { id: '10', name: 'Julia White', email: 'julia@example.com', role: 'Editor', status: 'active' },
  { id: '11', name: 'Kevin Patel', email: 'kevin@example.com', role: 'Viewer', status: 'active' },
  { id: '12', name: 'Laura Adams', email: 'laura@example.com', role: 'Editor', status: 'inactive' },
  { id: '13', name: 'Mia Johnson', email: 'mia@example.com', role: 'Admin', status: 'active' },
  { id: '14', name: 'Noah Garcia', email: 'noah@example.com', role: 'Viewer', status: 'active' },
  { id: '15', name: 'Olivia Wilson', email: 'olivia@example.com', role: 'Editor', status: 'active' },
]

const meta: Meta<typeof DataTable> = {
  title: 'UI/DataTable',
  component: DataTable,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof DataTable>

export const Default: Story = {
  args: { columns, data, pageSize: 10 },
}

export const Empty: Story = {
  args: { columns, data: [], pageSize: 10 },
}

export const Searchable: Story = {
  args: { columns, data, pageSize: 10, searchable: true, searchPlaceholder: 'Search users...' },
}

export const WithRowClick: Story = {
  args: { columns, data, pageSize: 10, onRowClick: (row) => console.log('Clicked:', row) },
}

export const SmallPageSize: Story = {
  args: { columns, data, pageSize: 3 },
}

export const SingleRow: Story = {
  args: {
    columns,
    data: [{ id: '1', name: 'Alice Chen', email: 'alice@example.com', role: 'Admin', status: 'active' }],
    pageSize: 10,
  },
}
