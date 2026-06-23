import type { Meta, StoryObj } from '@storybook/react'
import { MotionCard } from './MotionCard'

const meta: Meta<typeof MotionCard> = {
  title: 'Motion/MotionCard',
  component: MotionCard,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof MotionCard>

export const Default: Story = {
  args: {
    children: (
      <div className="p-6 bg-background-card rounded-xl border border-border">
        <h3 className="text-lg font-semibold text-text-primary">Interactive Card</h3>
        <p className="text-text-secondary mt-2 text-sm">Hover over me — I respond with a subtle lift and glow.</p>
      </div>
    ),
  },
}

export const SubtleHover: Story = {
  args: {
    children: (
      <div className="p-6 bg-background-card rounded-xl border border-border">
        <h3 className="text-lg font-semibold text-text-primary">Gentle Lift</h3>
        <p className="text-text-secondary mt-2 text-sm">hoverScale=1.01, tapScale=0.99</p>
      </div>
    ),
    hoverScale: 1.01,
    tapScale: 0.99,
  },
}

export const DramaticHover: Story = {
  args: {
    children: (
      <div className="p-6 bg-background-card rounded-xl border border-border">
        <h3 className="text-lg font-semibold text-text-primary">Bold Interaction</h3>
        <p className="text-text-secondary mt-2 text-sm">hoverScale=1.05, tapScale=0.95</p>
      </div>
    ),
    hoverScale: 1.05,
    tapScale: 0.95,
  },
}
