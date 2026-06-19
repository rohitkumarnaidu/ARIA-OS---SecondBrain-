import type { Meta, StoryObj } from '@storybook/react'
import { Bold, Italic, Underline, Type, AlignLeft, AlignCenter, AlignRight, Image, Link } from 'lucide-react'
import { Toolbar, ToolbarSeparator } from './Toolbar'
import { Button } from './Button'

const meta: Meta<typeof Toolbar> = {
  title: 'UI/Toolbar',
  component: Toolbar,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['surface', 'ghost'] },
  },
}

export default meta
type Story = StoryObj<typeof Toolbar>

export const Default: Story = {
  args: {
    variant: 'surface',
    children: (
      <>
        <Button variant="ghost" size="sm"><Bold size={16} /></Button>
        <Button variant="ghost" size="sm"><Italic size={16} /></Button>
        <Button variant="ghost" size="sm"><Underline size={16} /></Button>
      </>
    ),
  },
}

export const WithSeparator: Story = {
  args: {
    variant: 'surface',
    children: (
      <>
        <Button variant="ghost" size="sm"><Type size={16} /></Button>
        <ToolbarSeparator />
        <Button variant="ghost" size="sm"><AlignLeft size={16} /></Button>
        <Button variant="ghost" size="sm"><AlignCenter size={16} /></Button>
        <Button variant="ghost" size="sm"><AlignRight size={16} /></Button>
      </>
    ),
  },
}

export const GhostVariant: Story = {
  args: {
    variant: 'ghost',
    children: (
      <>
        <Button variant="ghost" size="sm"><Bold size={16} /></Button>
        <Button variant="ghost" size="sm"><Italic size={16} /></Button>
        <Button variant="ghost" size="sm"><Underline size={16} /></Button>
      </>
    ),
  },
}

export const WithOverflow: Story = {
  args: {
    variant: 'surface',
    children: (
      <>
        <Button variant="ghost" size="sm"><Bold size={16} /></Button>
        <Button variant="ghost" size="sm"><Italic size={16} /></Button>
        <Button variant="ghost" size="sm"><Underline size={16} /></Button>
        <ToolbarSeparator />
        <Button variant="ghost" size="sm"><Image size={16} /></Button>
        <Button variant="ghost" size="sm"><Link size={16} /></Button>
        <ToolbarSeparator />
        <Button variant="ghost" size="sm"><Type size={16} /></Button>
      </>
    ),
  },
}

export const Empty: Story = {
  args: {
    variant: 'surface',
    children: undefined,
  },
}
