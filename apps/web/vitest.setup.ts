import '@testing-library/jest-dom/vitest'
import { vi } from 'vitest'

vi.mock('framer-motion', async () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const actual = await vi.importActual<Record<string, any>>('framer-motion')
  return {
    ...actual,
    motion: {
      div: (props: Record<string, unknown>) => {
        const { initial, animate, exit, transition, variants, custom, layout, whileHover, whileTap, ...rest } = props
        return actual.motion.div(rest)
      },
      span: (props: Record<string, unknown>) => {
        const { initial, animate, exit, transition, variants, custom, layout, whileHover, whileTap, ...rest } = props
        return actual.motion.span(rest)
      },
      button: (props: Record<string, unknown>) => {
        const { initial, animate, exit, transition, variants, custom, layout, whileHover, whileTap, ...rest } = props
        return actual.motion.button(rest)
      },
    },
    AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
  }
})
