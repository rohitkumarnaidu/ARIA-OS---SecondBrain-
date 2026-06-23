import type { Meta, StoryObj } from '@storybook/react'
import Navbar from './Navbar'

const meta: Meta<typeof Navbar> = {
  title: 'Components/Navbar',
  component: Navbar,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
    layout: 'fullscreen',
  },
}

export default meta
type Story = StoryObj<typeof Navbar>

export const Default: Story = {}

export const Mobile: Story = {
  parameters: {
    viewport: { defaultViewport: 'mobile1' },
  },
}

export const Tablet: Story = {
  parameters: {
    viewport: { defaultViewport: 'tablet' },
  },
}
