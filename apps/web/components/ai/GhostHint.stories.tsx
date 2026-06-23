import type { Meta, StoryObj } from '@storybook/react'
import { GhostHint } from './GhostHint'

const meta: Meta<typeof GhostHint> = {
  title: 'AI/GhostHint',
  component: GhostHint,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof GhostHint>

export const Visible: Story = {
  args: { text: 'Try "Create a task to review PR by Friday"', state: 'visible', onAccept: () => {}, onDismiss: () => {} },
}

export const Hidden: Story = {
  args: { text: 'Schedule your workout for tomorrow', state: 'hidden' },
}

export const Filled: Story = {
  args: { text: 'Create a task to...', state: 'filled', onAccept: () => {} },
}

export const Dismissed: Story = {
  args: { text: 'You can ask me anything', state: 'dismissed' },
}
