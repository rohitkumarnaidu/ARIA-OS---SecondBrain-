import type { Meta, StoryObj } from '@storybook/react'
import { DataTable, type ColumnDef } from './DataTable'

const columns: ColumnDef<{ id?: string }>[] = [
  { header: 'Name', accessorKey: 'name', enableSorting: true },
  { header: 'Email', accessorKey: 'email', enableSorting: true },
  { header: 'Role', accessorKey: 'role', enableSorting: true },
  {
    header: 'Status',
    accessorKey: 'status',
    enableSorting: true,
    cell: ({ value }) => (
      <span style={{ color: value === 'active' ? 'var(--accent-neon)' : 'var(--accent-warning)' }}>
        {String(value)}
      </span>
    ),
  },
]

const data: { id?: string; name: string; email: string; role: string; status: string }[] = [
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
  title: 'Components/DataTable',
  component: DataTable,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
  },
}

export default meta
type Story = StoryObj<typeof DataTable>

export const Default: Story = {
  args: { columns, data, pageSize: 10 },
}

export const WithSelection: Story = {
  args: { columns, data, pageSize: 10, enableSelection: true },
}

export const WithFiltering: Story = {
  args: { columns, data, pageSize: 10, enableFiltering: true },
}

export const WithExport: Story = {
  args: { columns, data, pageSize: 10, enableFiltering: true, enableExport: true },
}

export const Empty: Story = {
  args: { columns, data: [], pageSize: 10 },
}

export const Loading: Story = {
  args: { columns, data: [], pageSize: 10, loading: true },
}

export const Error: Story = {
  args: { columns, data: [], pageSize: 10, error: 'Failed to load data' },
}

export const SingleRow: Story = {
  args: {
    columns,
    data: data.slice(0, 1),
    pageSize: 10,
  },
}

export const WithRowClick: Story = {
  args: { columns, data, pageSize: 10, onRowClick: (row) => console.log('Clicked:', row) },
}

export const DatagridVariant: Story = {
  args: { columns, data: data.slice(0, 5), pageSize: 10, variant: 'datagrid' },
}
