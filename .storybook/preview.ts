import type { Preview } from '@storybook/react'
import '../apps/web/app/globals.css'

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: { matchers: { color: /(background|color)$/i, date: /Date$/ } },
    backgrounds: { default: 'dark', values: [{ name: 'dark', value: '#0A0B0F' }] },
    viewport: { viewports: { mobile: { name: 'Mobile', styles: { width: '375px', height: '812px' } } } },
    a11y: { config: { rules: [{ id: 'color-contrast', enabled: true }] } },
  },
  decorators: [(Story) => <div className="bg-[#0A0B0F] min-h-screen p-8"><Story /></div>],
  tags: ['autodocs'],
}

export default preview
