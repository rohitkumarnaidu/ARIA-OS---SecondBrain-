import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Combobox } from './Combobox'

const meta: Meta<typeof Combobox> = {
  title: 'UI/Combobox',
  component: Combobox,
  tags: ['autodocs'],
  argTypes: {
    disabled: { control: 'boolean' },
    placeholder: { control: 'text' },
    searchPlaceholder: { control: 'text' },
    emptyText: { control: 'text' },
  },
}

export default meta
type Story = StoryObj<typeof Combobox>

const languages = [
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'python', label: 'Python' },
  { value: 'rust', label: 'Rust' },
  { value: 'go', label: 'Go' },
  { value: 'java', label: 'Java' },
  { value: 'kotlin', label: 'Kotlin' },
  { value: 'swift', label: 'Swift' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'elixir', label: 'Elixir' },
]

export const Default: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return <Combobox {...args} value={value} onChange={setValue} />
  },
  args: {
    items: languages,
    placeholder: 'Choose a language...',
  },
}

export const Open: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return (
      <div style={{ height: 300 }}>
        <Combobox {...args} value={value} onChange={setValue} />
      </div>
    )
  },
  args: {
    items: languages,
    placeholder: 'Search languages...',
    searchPlaceholder: 'Filter languages...',
  },
}

export const WithSelection: Story = {
  render: (args) => {
    const [value, setValue] = useState('typescript')
    return <Combobox {...args} value={value} onChange={setValue} />
  },
  args: {
    items: languages,
    placeholder: 'Choose a language...',
  },
}

export const Disabled: Story = {
  args: {
    items: languages,
    placeholder: 'Disabled',
    disabled: true,
    value: 'rust',
  },
}

export const EmptyResults: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return (
      <div style={{ height: 200 }}>
        <Combobox {...args} value={value} onChange={setValue} />
      </div>
    )
  },
  args: {
    items: [],
    placeholder: 'No items available',
    emptyText: 'No options found.',
  },
}

export const ManyItems: Story = {
  render: (args) => {
    const [value, setValue] = useState('')
    return <Combobox {...args} value={value} onChange={setValue} />
  },
  args: {
    items: Array.from({ length: 100 }, (_, i) => ({
      value: `item-${i}`,
      label: `Item ${i + 1}`,
    })),
    placeholder: 'Scroll through 100 items...',
  },
}
