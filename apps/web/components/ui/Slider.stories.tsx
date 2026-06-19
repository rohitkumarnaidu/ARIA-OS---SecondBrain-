import { useState } from 'react'
import type { Meta, StoryObj } from '@storybook/react'
import { Slider } from './Slider'

const meta: Meta<typeof Slider> = {
  title: 'UI/Slider',
  component: Slider,
  tags: ['autodocs'],
  argTypes: {
    value: { control: { type: 'number', min: 0, max: 100 } },
    min: { control: 'number' },
    max: { control: 'number' },
    step: { control: 'number' },
    disabled: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof Slider>

export const Default: Story = {
  args: { value: 50, onChange: () => {}, min: 0, max: 100 },
}

export const Zero: Story = {
  args: { value: 0, onChange: () => {}, min: 0, max: 100 },
}

export const Full: Story = {
  args: { value: 100, onChange: () => {}, min: 0, max: 100 },
}

export const CustomRange: Story = {
  args: { value: 25, onChange: () => {}, min: -50, max: 50 },
}

export const CustomStep: Story = {
  args: { value: 30, onChange: () => {}, min: 0, max: 100, step: 10 },
}

export const Disabled: Story = {
  args: { value: 40, onChange: () => {}, min: 0, max: 100, disabled: true },
}

export const NarrowRange: Story = {
  args: { value: 5, onChange: () => {}, min: 0, max: 10 },
}
