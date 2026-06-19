import type { Meta, StoryObj } from '@storybook/react'
import { useState, useCallback } from 'react'
import { FileUpload } from './FileUpload'

const meta: Meta<typeof FileUpload> = {
  title: 'UI/FileUpload',
  component: FileUpload,
  tags: ['autodocs'],
  argTypes: {
    accept: { control: 'text' },
    multiple: { control: 'boolean' },
    maxSize: { control: 'number' },
    maxFiles: { control: 'number' },
  },
}

export default meta
type Story = StoryObj<typeof FileUpload>

const DefaultRenderer = (args: any) => {
  const [files, setFiles] = useState<File[]>([])
  const handleFiles = useCallback((incoming: File[]) => {
    setFiles(incoming)
  }, [])
  return (
    <div style={{ width: 400 }}>
      <FileUpload {...args} onFiles={handleFiles} />
      {files.length > 0 && (
        <p className="mt-2 text-xs" style={{ color: 'var(--text-tertiary)' }}>
          {files.length} file(s) selected
        </p>
      )}
    </div>
  )
}

export const Default: Story = {
  render: DefaultRenderer,
  args: {},
}

export const SingleFile: Story = {
  render: DefaultRenderer,
  args: {
    multiple: false,
  },
}

export const ImagesOnly: Story = {
  render: DefaultRenderer,
  args: {
    accept: 'image/png, image/jpeg, image/webp',
    multiple: true,
  },
}

export const WithSizeLimit: Story = {
  render: DefaultRenderer,
  args: {
    maxSize: 1 * 1024 * 1024,
    accept: '.pdf,.doc,.docx',
  },
}

export const MaxTwoFiles: Story = {
  render: DefaultRenderer,
  args: {
    maxFiles: 2,
    multiple: true,
  },
}

export const AllRestrictions: Story = {
  render: DefaultRenderer,
  args: {
    accept: 'image/*',
    maxSize: 5 * 1024 * 1024,
    maxFiles: 3,
    multiple: true,
  },
}
