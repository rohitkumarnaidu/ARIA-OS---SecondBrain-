import type { Meta, StoryObj } from '@storybook/react'
import ThreeBackground from './ThreeBackground'

const meta: Meta<typeof ThreeBackground> = {
  title: 'Components/ThreeBackground',
  component: ThreeBackground,
  tags: ['autodocs'],
  parameters: {
    backgrounds: { default: 'dark' },
    layout: 'fullscreen',
  },
}

export default meta
type Story = StoryObj<typeof ThreeBackground>

export const Default: Story = {
  args: { className: 'w-full h-[400px]' },
}

export const Fullscreen: Story = {
  args: { className: 'fixed inset-0' },
}

export const Small: Story = {
  args: { className: 'w-[300px] h-[200px] rounded-xl overflow-hidden' },
  parameters: { layout: 'centered' },
}
