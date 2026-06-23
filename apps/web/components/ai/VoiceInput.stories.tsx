import type { Meta, StoryObj } from '@storybook/react'
import { VoiceInput } from './VoiceInput'

const meta: Meta<typeof VoiceInput> = {
  title: 'AI/VoiceInput',
  component: VoiceInput,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof VoiceInput>

export const Enabled: Story = {
  args: {
    onTranscript: (text: string) => console.log('Transcript:', text),
    disabled: false,
  },
}

export const Disabled: Story = {
  args: {
    onTranscript: () => {},
    disabled: true,
  },
}
