import type { Meta, StoryObj } from '@storybook/react'
import { Spinner } from './Spinner'

const meta = {
  title: 'UI/Spinner',
  component: Spinner,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    size: { control: 'number', min: 8, max: 64 },
  },
} satisfies Meta<typeof Spinner>

export default meta
type Story = StoryObj<typeof meta>

export const Small: Story = {
  args: { size: 16 },
}

export const Medium: Story = {
  args: { size: 24 },
}

export const Large: Story = {
  args: { size: 48 },
}

export const WithLabel: Story = {
  render: (args) => (
    <div className="flex items-center gap-3">
      <Spinner {...args} />
      <span className="text-sm text-text-secondary font-body">Loading...</span>
    </div>
  ),
  args: { size: 20 },
}

export const CenteredFullPage: Story = {
  render: (args) => (
    <div className="flex flex-col items-center justify-center gap-4 p-12 min-h-[200px]">
      <Spinner {...args} />
      <p className="text-sm text-text-secondary font-body">Please wait while we load your content</p>
    </div>
  ),
  args: { size: 32 },
}

export const Inline: Story = {
  render: (args) => (
    <span className="inline-flex items-center gap-2 text-sm text-text-secondary font-body">
      <Spinner {...args} />
      Saving...
    </span>
  ),
  args: { size: 14 },
}

export const ButtonSpinner: Story = {
  render: (args) => (
    <button
      disabled
      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-accent-primary text-white text-sm font-medium font-body opacity-70"
    >
      <Spinner {...args} />
      Processing
    </button>
  ),
  args: { size: 16 },
}
