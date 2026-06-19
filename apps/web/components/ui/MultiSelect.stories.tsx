import { useState, useCallback } from 'react'
import type { Meta, StoryObj } from '@storybook/react'
import { MultiSelect } from './MultiSelect'

const meta: Meta<typeof MultiSelect> = {
  title: 'UI/MultiSelect',
  component: MultiSelect,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof MultiSelect>

const sampleItems = [
  { value: 'react', label: 'React' },
  { value: 'vue', label: 'Vue' },
  { value: 'angular', label: 'Angular' },
  { value: 'svelte', label: 'Svelte' },
  { value: 'solid', label: 'Solid' },
  { value: 'qwik', label: 'Qwik' },
  { value: 'next', label: 'Next.js' },
  { value: 'nuxt', label: 'Nuxt' },
]

export const Default: Story = {
  render: (args) => {
    const [values, setValues] = useState<string[]>([])
    return <MultiSelect {...args} items={sampleItems} values={values} onChange={setValues} />
  },
}

export const WithSelection: Story = {
  render: () => {
    const [values, setValues] = useState<string[]>(['react', 'next'])
    return <MultiSelect items={sampleItems} values={values} onChange={setValues} />
  },
}

export const SearchMode: Story = {
  render: () => {
    const [values, setValues] = useState<string[]>([])
    return <MultiSelect items={sampleItems} values={values} onChange={setValues} placeholder="Search frameworks..." />
  },
}

export const MaxLimit: Story = {
  render: () => {
    const [values, setValues] = useState<string[]>(['react'])
    return <MultiSelect items={sampleItems} values={values} onChange={setValues} maxItems={3} placeholder="Select up to 3" />
  },
}

export const EmptyItems: Story = {
  render: () => {
    const [values, setValues] = useState<string[]>([])
    return <MultiSelect items={[]} values={values} onChange={setValues} placeholder="No options" />
  },
}

export const ManySelections: Story = {
  render: () => {
    const [values, setValues] = useState<string[]>(['react', 'vue', 'angular', 'svelte'])
    return <MultiSelect items={sampleItems} values={values} onChange={setValues} />
  },
}
