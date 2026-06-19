// Duration presets (milliseconds)
export const DURATION = {
  fast: 150,
  normal: 200,
  slow: 300,
  slower: 500,
  slowest: 1000,
} as const

// Framer Motion specific durations
export const MOTION_DURATION = {
  fast: 0.15,
  normal: 0.2,
  slow: 0.3,
  slower: 0.5,
  slowest: 1,
} as const

// Easing curve presets (cubic-bezier)
export const EASING = {
  default: [0.4, 0, 0.2, 1] as const,
  in: [0.4, 0, 1, 1] as const,
  out: [0, 0, 0.2, 1] as const,
  bounce: [0.68, -0.55, 0.265, 1.55] as const,
  elastic: [0.68, -0.6, 0.32, 1.6] as const,
  smooth: [0.16, 1, 0.3, 1] as const,
} as const

// Stagger configuration
export const STAGGER = {
  fast: { staggerChildren: 0.04, delayChildren: 0.05 },
  normal: { staggerChildren: 0.08, delayChildren: 0.1 },
  slow: { staggerChildren: 0.12, delayChildren: 0.15 },
} as const
