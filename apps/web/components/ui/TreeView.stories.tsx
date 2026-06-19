import type { Meta, StoryObj } from '@storybook/react'
import { TreeView, type TreeItem } from './TreeView'
import { FileText, Folder, Image, Settings, Terminal } from 'lucide-react'

const nestedItems: TreeItem[] = [
  {
    id: 'src',
    label: 'src',
    icon: <Folder size={14} />,
    children: [
      {
        id: 'components',
        label: 'components',
        icon: <Folder size={14} />,
        children: [
          { id: 'button', label: 'Button.tsx', icon: <FileText size={14} /> },
          { id: 'card', label: 'Card.tsx', icon: <FileText size={14} /> },
          { id: 'modal', label: 'Modal.tsx', icon: <FileText size={14} /> },
        ],
      },
      {
        id: 'hooks',
        label: 'hooks',
        icon: <Folder size={14} />,
        children: [
          { id: 'use-auth', label: 'useAuth.ts', icon: <FileText size={14} /> },
          { id: 'use-fetch', label: 'useFetch.ts', icon: <FileText size={14} /> },
        ],
      },
      { id: 'main', label: 'main.tsx', icon: <FileText size={14} /> },
    ],
  },
  {
    id: 'public',
    label: 'public',
    icon: <Folder size={14} />,
    children: [
      { id: 'logo', label: 'logo.svg', icon: <Image size={14} /> },
      { id: 'favicon', label: 'favicon.ico', icon: <Image size={14} /> },
    ],
  },
  {
    id: 'config',
    label: 'config',
    icon: <Settings size={14} />,
    children: [
      { id: 'tsconfig', label: 'tsconfig.json', icon: <FileText size={14} />, disabled: true },
      { id: 'package', label: 'package.json', icon: <FileText size={14} /> },
    ],
  },
  {
    id: 'readme',
    label: 'README.md',
    icon: <FileText size={14} />,
  },
]

const meta: Meta<typeof TreeView> = {
  title: 'UI/TreeView',
  component: TreeView,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof TreeView>

export const Default: Story = {
  args: { items: nestedItems, onSelect: (item) => console.log('Selected:', item) },
}

export const Expanded: Story = {
  args: {
    items: nestedItems,
    defaultExpandedIds: ['src', 'components', 'public'],
    onSelect: (item) => console.log('Selected:', item),
  },
}

export const SingleLevel: Story = {
  args: {
    items: [
      { id: '1', label: 'Item 1', icon: <FileText size={14} /> },
      { id: '2', label: 'Item 2', icon: <FileText size={14} /> },
      { id: '3', label: 'Item 3', icon: <FileText size={14} /> },
    ],
  },
}

export const WithDisabledItems: Story = {
  args: {
    items: [
      {
        id: 'project',
        label: 'Project',
        icon: <Folder size={14} />,
        children: [
          { id: 'readme', label: 'README.md', icon: <FileText size={14} /> },
          { id: 'license', label: 'LICENSE', icon: <FileText size={14} />, disabled: true },
          { id: 'todo', label: 'TODO.md', icon: <FileText size={14} />, disabled: true },
        ],
      },
      {
        id: 'archive',
        label: 'Archive (read-only)',
        icon: <Folder size={14} />,
        disabled: true,
        children: [
          { id: 'old1', label: 'v1.0 notes.md', icon: <FileText size={14} /> },
        ],
      },
    ],
    defaultExpandedIds: ['project'],
  },
}

export const DeeplyNested: Story = {
  args: {
    items: [
      {
        id: 'a',
        label: 'Root',
        icon: <Terminal size={14} />,
        children: [
          {
            id: 'b',
            label: 'Level 2',
            icon: <Folder size={14} />,
            children: [
              {
                id: 'c',
                label: 'Level 3',
                icon: <Folder size={14} />,
                children: [
                  { id: 'd', label: 'deep-file.ts', icon: <FileText size={14} /> },
                ],
              },
            ],
          },
        ],
      },
    ],
    defaultExpandedIds: ['a', 'b', 'c'],
  },
}
