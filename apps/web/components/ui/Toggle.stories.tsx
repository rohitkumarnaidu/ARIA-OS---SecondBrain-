import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Toggle } from './Toggle'

const meta: Meta<typeof Toggle> = {
  title: 'UI/Toggle',
  component: Toggle,
  tags: ['autodocs'],
  argTypes: {
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    disabled: { control: 'boolean' },
    label: { control: 'text' },
  },
}

export default meta
type Story = StoryObj<typeof Toggle>

export const Off: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(false)
    return <Toggle {...args} checked={checked} onChange={setChecked} />
  },
  args: {
    label: 'Toggle me',
  },
}

export const On: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(true)
    return <Toggle {...args} checked={checked} onChange={setChecked} />
  },
  args: {
    label: 'Active toggle',
  },
}

export const Small: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(false)
    return <Toggle {...args} checked={checked} onChange={setChecked} />
  },
  args: {
    size: 'sm',
    label: 'Small toggle',
  },
}

export const Medium: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(true)
    return <Toggle {...args} checked={checked} onChange={setChecked} />
  },
  args: {
    size: 'md',
    label: 'Medium toggle',
  },
}

export const Large: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(true)
    return <Toggle {...args} checked={checked} onChange={setChecked} />
  },
  args: {
    size: 'lg',
    label: 'Large toggle',
  },
}

export const Disabled: Story = {
  args: {
    checked: false,
    disabled: true,
    label: 'Disabled',
  },
}

export const DisabledOn: Story = {
  args: {
    checked: true,
    disabled: true,
    label: 'Disabled (on)',
  },
}

export const WithoutLabel: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(false)
    return <Toggle {...args} checked={checked} onChange={setChecked} />
  },
  args: {},
}
