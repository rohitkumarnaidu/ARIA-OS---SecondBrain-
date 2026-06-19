import type { Preview } from '@storybook/nextjs-vite'

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    a11y: {
      test: 'todo',
    },
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#0A0B0F' },
        { name: 'card', value: '#13151A' },
      ],
    },
  },
  globalTypes: {
    theme: {
      name: 'Theme',
      description: 'Global theme for components',
      defaultValue: 'dark',
      toolbar: {
        icon: 'paintbrush',
        items: ['dark'],
        dynamicTitle: true,
      },
    },
  },
  decorators: [
    (Story) => (
      <div style={{
        fontFamily: "'DM Sans', sans-serif",
        background: '#0A0B0F',
        color: '#F1F5F9',
        padding: '24px',
        minHeight: '100vh',
      }}>
        <Story />
      </div>
    ),
  ],
}

export default preview
