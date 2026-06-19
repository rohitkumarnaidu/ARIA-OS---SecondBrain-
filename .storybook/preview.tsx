import React from 'react'
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
        { name: 'lighter', value: '#13151A' },
        { name: 'light', value: '#F8FAFC' },
      ],
    },
    layout: 'centered',
    a11y: {
      config: { rules: [{ id: 'color-contrast', enabled: true }] },
    },
  },
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <div style={{ fontFamily: "'DM Sans', sans-serif", padding: '1rem' }}>
        <Story />
      </div>
    ),
  ],
}

export default preview
