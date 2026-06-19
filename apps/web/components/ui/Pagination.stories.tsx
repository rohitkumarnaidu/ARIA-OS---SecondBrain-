import type { Meta, StoryObj } from '@storybook/react'
import { Pagination } from './Pagination'

const meta: Meta<typeof Pagination> = {
  title: 'UI/Pagination',
  component: Pagination,
  tags: ['autodocs'],
  argTypes: {
    currentPage: { control: { type: 'number', min: 1 } },
    totalPages: { control: { type: 'number', min: 1 } },
    siblingCount: { control: { type: 'number', min: 0, max: 3 } },
  },
}

export default meta
type Story = StoryObj<typeof Pagination>

export const FewPages: Story = {
  args: { currentPage: 1, totalPages: 3, onPageChange: () => {} },
}

export const ManyPages: Story = {
  args: { currentPage: 1, totalPages: 20, onPageChange: () => {} },
}

export const WithEllipsis: Story = {
  args: { currentPage: 10, totalPages: 20, onPageChange: () => {} },
}

export const FirstPage: Story = {
  args: { currentPage: 1, totalPages: 10, onPageChange: () => {} },
}

export const LastPage: Story = {
  args: { currentPage: 10, totalPages: 10, onPageChange: () => {} },
}

export const SinglePage: Story = {
  args: { currentPage: 1, totalPages: 1, onPageChange: () => {} },
}

export const WithMoreSiblings: Story = {
  args: { currentPage: 10, totalPages: 20, siblingCount: 2, onPageChange: () => {} },
}

export const EarlyPage: Story = {
  args: { currentPage: 3, totalPages: 20, onPageChange: () => {} },
}

export const LatePage: Story = {
  args: { currentPage: 18, totalPages: 20, onPageChange: () => {} },
}
