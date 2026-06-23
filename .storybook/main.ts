import type { StorybookConfig } from '@storybook/nextjs'

const config: StorybookConfig = {
  stories: ['../apps/web/components/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
    '@storybook/addon-viewport',
  ],
  framework: { name: '@storybook/nextjs', options: {} },
  staticDirs: ['../apps/web/public'],
  docs: { autodocs: 'tag' },
}

export default config
