import type { Meta, StoryObj } from '@storybook/react'
import { StreamingText } from './StreamingText'

const meta: Meta<typeof StreamingText> = {
  title: 'AI/StreamingText',
  component: StreamingText,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof StreamingText>

const loremIpsum = 'Artificial intelligence is transforming how we work, learn, and create. By leveraging machine learning algorithms, we can automate repetitive tasks and uncover hidden patterns in data.'

export const Idle: Story = {
  args: {
    text: loremIpsum,
    isStreaming: false,
  },
}

export const Streaming: Story = {
  args: {
    text: loremIpsum,
    isStreaming: true,
    speed: 30,
  },
}

export const Complete: Story = {
  args: {
    text: loremIpsum,
    isStreaming: false,
    speed: 0,
  },
}

export const SlowStream: Story = {
  args: {
    text: 'This text appears character by character at a slow pace for dramatic effect.',
    isStreaming: true,
    speed: 80,
  },
}

export const FastStream: Story = {
  args: {
    text: 'Fast streaming for quick responses.',
    isStreaming: true,
    speed: 10,
  },
}

export const ShortText: Story = {
  args: {
    text: 'Done.',
    isStreaming: false,
  },
}
