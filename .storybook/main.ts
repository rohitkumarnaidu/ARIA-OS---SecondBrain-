import { defineConfig, type StorybookConfig } from '@storybook/nextjs'

const config: StorybookConfig = {
  stories: ['../apps/web/components/**/*.stories.@(ts|tsx)', '../apps/web/app/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
    '@storybook/addon-coverage',
  ],
  framework: {
    name: '@storybook/nextjs',
    options: {},
  },
  staticDirs: ['../apps/web/public'],
  docs: {
    autodocs: 'tag',
  },
}

export default config
