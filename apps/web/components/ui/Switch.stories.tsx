import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Switch } from './Switch'

const meta: Meta<typeof Switch> = {
  title: 'UI/Switch',
  component: Switch,
  tags: ['autodocs'],
  argTypes: {
    disabled: { control: 'boolean' },
    label: { control: 'text' },
    checked: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof Switch>

export const Off: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(false)
    return <Switch {...args} checked={checked} onChange={setChecked} />
  },
  args: {
    label: 'Notifications',
  },
}

export const On: Story = {
  render: (args) => {
    const [checked, setChecked] = useState(true)
    return <Switch {...args} checked={checked} onChange={setChecked} />
  },
  args: {
    label: 'Dark mode',
  },
}

export const Disabled: Story = {
  args: {
    checked: false,
    disabled: true,
    label: 'Disabled switch',
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
    return <Switch {...args} checked={checked} onChange={setChecked} />
  },
  args: {},
}
