import type { Meta, StoryObj } from '@storybook/react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { ChartContainer } from './ChartContainer'

const meta: Meta<typeof ChartContainer> = {
  title: 'UI/ChartContainer',
  component: ChartContainer,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof ChartContainer>

const chartData = [
  { name: 'Mon', value: 120 },
  { name: 'Tue', value: 200 },
  { name: 'Wed', value: 150 },
  { name: 'Thu', value: 80 },
  { name: 'Fri', value: 70 },
  { name: 'Sat', value: 110 },
  { name: 'Sun', value: 90 },
]

export const Default: Story = {
  args: {
    title: 'Weekly Activity',
    description: 'Hours logged per day',
    height: 250,
    children: (
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="name" stroke="var(--text-tertiary)" fontSize={12} />
        <YAxis stroke="var(--text-tertiary)" fontSize={12} />
        <Bar dataKey="value" fill="var(--accent-primary)" radius={[4, 4, 0, 0]} />
      </BarChart>
    ),
  },
}

export const WithoutLabels: Story = {
  args: {
    height: 200,
    children: (
      <BarChart data={chartData}>
        <Bar dataKey="value" fill="var(--accent-neon)" radius={[4, 4, 0, 0]} />
      </BarChart>
    ),
  },
}

export const Compact: Story = {
  args: {
    title: 'Quick Stats',
    height: 150,
    children: (
      <BarChart data={chartData.slice(0, 3)}>
        <Bar dataKey="value" fill="var(--accent-warning)" radius={[4, 4, 0, 0]} />
      </BarChart>
    ),
  },
}
