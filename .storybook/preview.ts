import type { Preview } from '@storybook/react'
import '../apps/web/styles/globals.css'

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#0A0B0F' },
        { name: 'light', value: '#F8FAFC' },
      ],
    },
    layout: 'centered',
  },
  tags: ['autodocs'],
}

export default preview
