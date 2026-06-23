import type { Meta, StoryObj } from '@storybook/react'
import { PageTransition } from './PageTransition'

const meta: Meta<typeof PageTransition> = {
  title: 'Motion/PageTransition',
  component: PageTransition,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof PageTransition>

const content = (
  <div className="p-8 bg-background-card rounded-xl border border-border">
    <h2 className="text-lg font-semibold text-text-primary mb-4">Page Content</h2>
    <p className="text-text-secondary">This content fades in with the page transition animation.</p>
  </div>
)

export const Fade: Story = {
  args: { children: content, variant: 'fade' },
}

export const SlideUp: Story = {
  args: { children: content, variant: 'slideUp' },
}

export const SlideDown: Story = {
  args: { children: content, variant: 'slideDown' },
}

export const Scale: Story = {
  args: { children: content, variant: 'scale' },
}
