import type { Meta, StoryObj } from '@storybook/react'
import { LoadingScreen } from './LoadingScreen'

const meta = {
  title: 'UI/LoadingScreen',
  component: LoadingScreen,
  parameters: { layout: 'fullscreen' },
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['page', 'card', 'list', 'detail'] },
    count: { control: 'number', min: 1, max: 20 },
  },
} satisfies Meta<typeof LoadingScreen>

export default meta
type Story = StoryObj<typeof meta>

export const PageLoading: Story = {
  args: { variant: 'page' },
}

export const CardLoading: Story = {
  args: { variant: 'card' },
}

export const ListLoading: Story = {
  args: { variant: 'list', count: 5 },
}

export const DetailLoading: Story = {
  args: { variant: 'detail' },
}

export const ListWithCustomCount: Story = {
  args: { variant: 'list', count: 10 },
}

export const WithCustomLabel: Story = {
  args: { variant: 'page', label: 'Loading dashboard data...' },
}

export const SingleListRow: Story = {
  args: { variant: 'list', count: 1 },
}

export const LongList: Story = {
  args: { variant: 'list', count: 15 },
}
