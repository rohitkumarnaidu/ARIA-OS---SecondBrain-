import '@testing-library/jest-dom'
import { vi, beforeAll, afterAll, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

// ─── Module Mocks ────────────────────────────────────────────────────────────

/**
 * framer-motion — replaces all motion.* elements with plain <div> via Proxy + forwardRef.
 * Exit animations stripped to avoid jsdom hangs.
 */
vi.mock('framer-motion', () => {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const React = require('react') as typeof import('react')
  const noop = React.forwardRef<HTMLElement, Record<string, unknown>>(
    (props: Record<string, unknown>, ref: React.Ref<HTMLElement>) => {
      const {
        initial, animate, exit, transition, variants, custom, layout,
        whileHover, whileTap, onAnimationComplete, whileInView, viewport,
        onViewportEnter, onViewportLeave, whileFocus, whileDrag,
        drag, dragConstraints, onDragEnd, layoutId, layoutDependency,
        children, ...rest
      } = props as { children?: React.ReactNode; [key: string]: unknown }
      return React.createElement('div', { ...rest, ref }, children as React.ReactNode)
    },
  )
  noop.displayName = 'motion.div'

  return {
    motion: new Proxy({} as Record<string, typeof noop>, { get: () => noop }),
    AnimatePresence: ({ children }: { children: React.ReactNode }) =>
      React.createElement(React.Fragment, null, children),
    useReducedMotion: () => false,
    useMotionValue: (v: number) => ({
      get: () => v, set: () => {}, onChange: () => {}, destroy: () => {},
    }),
    useTransform: (v: unknown) => v,
    useAnimation: () => ({ start: async () => {}, stop: () => {}, set: () => {} }),
    animate: () => ({}),
    useScroll: () => ({ scrollY: { get: () => 0, onChange: () => {} } }),
  }
})

/**
 * next/navigation — centralized mock so every component test gets predictable stubs
 * for useRouter, usePathname, useSearchParams.
 */
vi.mock('next/navigation', () => {
  const push = vi.fn()
  const replace = vi.fn()
  const back = vi.fn()
  const forward = vi.fn()
  const refresh = vi.fn()
  const prefetch = vi.fn()

  return {
    useRouter: () => ({
      push, replace, back, forward, refresh, prefetch,
      pathname: '/',
      query: {},
      asPath: '/',
    }),
    usePathname: () => '/',
    useSearchParams: () => new URLSearchParams(),
    useParams: () => ({}),
  }
})

/**
 * @radix-ui/react-slot — centralised mock so every component test gets
 * a predictable Slot that handles the Button component's conditional
 * children ({loading && <Loader/>}{!loading && icon && <span/>}{children}).
 *
 * The real Slot uses React.Children.count() === 1 && isValidElement()
 * which fails in jsdom when extra boolean children are present.
 */
vi.mock('@radix-ui/react-slot', () => {
  const React = require('react') as typeof import('react')

  const Slot = React.forwardRef(
    ({ children, ...props }: { children?: React.ReactNode; [key: string]: unknown },
     ref: React.Ref<HTMLElement>) => {
      const childrenArray = React.Children.toArray(children)
      const firstValid = childrenArray.find((c): c is React.ReactElement =>
        React.isValidElement(c))
      if (!firstValid) return React.createElement(React.Fragment, null, children)
      return React.cloneElement(firstValid, { ...props, ref })
    },
  )
  Slot.displayName = 'Slot'

  const Slottable = ({ children }: { children: React.ReactNode }) =>
    React.createElement(React.Fragment, null, children)
  ;(Slottable as Record<string, unknown>).displayName = 'Slottable'

  return { Slot, Slottable, Root: Slot, default: Slot }
})

// ─── jsdom Polyfills ─────────────────────────────────────────────────────────

globalThis.IntersectionObserver = class IntersectionObserver {
  readonly root: Element | Document | null = null
  readonly rootMargin: string = ''
  readonly thresholds: ReadonlyArray<number> = []
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords(): IntersectionObserverEntry[] { return [] }
  unobserve() {}
} as unknown as typeof IntersectionObserver

globalThis.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
} as unknown as typeof ResizeObserver

Element.prototype.scrollIntoView = () => {}

Object.defineProperty(globalThis, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
})

// ─── Lifecycle ───────────────────────────────────────────────────────────────

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})
