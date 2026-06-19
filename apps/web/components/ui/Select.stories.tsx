import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Select } from './Select'

const meta: Meta<typeof Select> = {
  title: 'UI/Select',
  component: Select,
  tags: ['autodocs'],
  argTypes: {
    searchable: { control: 'boolean' },
    disabled: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof Select>

const defaultOptions = [
  { value: 'react', label: 'React' },
  { value: 'vue', label: 'Vue' },
  { value: 'svelte', label: 'Svelte' },
  { value: 'angular', label: 'Angular' },
  { value: 'solid', label: 'Solid' },
  { value: 'qwik', label: 'Qwik' },
]

export const Default: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return <Select {...args} value={value} onChange={setValue} />
  },
  args: {
    options: defaultOptions,
    placeholder: 'Select a framework...',
  },
}

export const WithSelection: Story = {
  render: (args) => {
    const [value, setValue] = useState('react')
    return <Select {...args} value={value} onChange={setValue} />
  },
  args: {
    options: defaultOptions,
    placeholder: 'Select a framework...',
  },
}

export const Searchable: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return <Select {...args} value={value} onChange={setValue} />
  },
  args: {
    options: defaultOptions,
    placeholder: 'Search and select...',
    searchable: true,
  },
}

export const NonSearchable: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return <Select {...args} value={value} onChange={setValue} />
  },
  args: {
    options: defaultOptions,
    placeholder: 'Select (no search)',
    searchable: false,
  },
}

export const Disabled: Story = {
  args: {
    options: defaultOptions,
    placeholder: 'Disabled select',
    disabled: true,
    value: 'react',
  },
}

export const ManyOptions: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return <Select {...args} value={value} onChange={setValue} />
  },
  args: {
    options: Array.from({ length: 50 }, (_, i) => ({
      value: `option-${i}`,
      label: `Option ${i + 1}`,
    })),
    placeholder: 'Scroll through many options...',
  },
}
