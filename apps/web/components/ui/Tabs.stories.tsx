import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Tabs } from './Tabs'

const meta: Meta<typeof Tabs> = {
  title: 'UI/Tabs',
  component: Tabs,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof Tabs>

const twoTabs = [
  { value: 'tab1', label: 'Overview' },
  { value: 'tab2', label: 'Details' },
]

const threeTabs = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'archived', label: 'Archived' },
]

const fiveTabs = [
  { value: 'overview', label: 'Overview' },
  { value: 'tasks', label: 'Tasks' },
  { value: 'notes', label: 'Notes' },
  { value: 'files', label: 'Files' },
  { value: 'activity', label: 'Activity' },
]

export const TwoTabs: Story = {
  render: (args) => {
    const [value, setValue] = useState('tab1')
    return <Tabs {...args} value={value} onChange={setValue} />
  },
  args: {
    tabs: twoTabs,
  },
}

export const ThreeTabs: Story = {
  render: (args) => {
    const [value, setValue] = useState('active')
    return <Tabs {...args} value={value} onChange={setValue} />
  },
  args: {
    tabs: threeTabs,
  },
}

export const FiveTabs: Story = {
  render: (args) => {
    const [value, setValue] = useState('overview')
    return <Tabs {...args} value={value} onChange={setValue} />
  },
  args: {
    tabs: fiveTabs,
  },
}

export const LastActive: Story = {
  render: (args) => {
    const [value, setValue] = useState('activity')
    return <Tabs {...args} value={value} onChange={setValue} />
  },
  args: {
    tabs: fiveTabs,
  },
}

export const SingleTab: Story = {
  render: (args) => {
    const [value, setValue] = useState('only')
    return <Tabs {...args} value={value} onChange={setValue} />
  },
  args: {
    tabs: [{ value: 'only', label: 'Solo' }],
  },
}

export const LongLabels: Story = {
  render: (args) => {
    const [value, setValue] = useState('first')
    return <Tabs {...args} value={value} onChange={setValue} />
  },
  args: {
    tabs: [
      { value: 'first', label: 'Productivity & Efficiency' },
      { value: 'second', label: 'Analytics Dashboard' },
      { value: 'third', label: 'User Management' },
    ],
  },
}
