import type { Meta, StoryObj } from '@storybook/react'
import { ErrorState } from './ErrorState'

const meta = {
  title: 'UI/ErrorState',
  component: ErrorState,
  parameters: { layout: 'fullscreen' },
  tags: ['autodocs'],
  argTypes: {
    status: { control: 'select', options: [400, 404, 429, 500] },
  },
} satisfies Meta<typeof ErrorState>

export default meta
type Story = StoryObj<typeof meta>

export const ServerError: Story = {
  args: {
    status: 500,
    onRetry: () => alert('Retry clicked'),
  },
}

export const NotFound: Story = {
  args: {
    status: 404,
    resource: 'task',
    onGoBack: () => alert('Go back clicked'),
  },
}

export const RateLimited: Story = {
  args: {
    status: 429,
    resource: 'API',
    onGoBack: () => alert('Go back clicked'),
  },
}

export const BadRequest: Story = {
  args: {
    status: 400,
    onRetry: () => alert('Retry clicked'),
  },
}

export const CustomTitleAndDescription: Story = {
  args: {
    status: 500,
    title: 'Connection Lost',
    description: 'Unable to reach our servers. Please check your internet connection and try again.',
    onRetry: () => alert('Retry clicked'),
  },
}

export const Compact: Story = {
  args: {
    status: 500,
    compact: true,
    onRetry: () => alert('Retry clicked'),
  },
}

export const CompactNotFound: Story = {
  args: {
    status: 404,
    compact: true,
    resource: 'page',
    onGoBack: () => alert('Go back clicked'),
  },
}

export const WithoutActions: Story = {
  args: {
    status: 500,
    title: 'Something went wrong',
  },
}
