import { describe, it, expect } from 'vitest'
import {
  pageSlide,
  scaleBounce,
  rotateIn,
  counter,
  progressFill,
  notificationSlide,
  tooltipFade,
  modalBackdrop,
  modalContent,
  emptyState,
  highlight,
} from '@/lib/motion/animations'

describe('pageSlide', () => {
  it('uses initial/animate/exit with x offsets', () => {
    expect(pageSlide.initial).toEqual({ opacity: 0, x: 30 })
    expect(pageSlide.animate).toHaveProperty('x', 0)
    expect(pageSlide.exit).toHaveProperty('x', -30)
  })
})

describe('scaleBounce', () => {
  it('uses hidden/visible/exit with scale', () => {
    expect(scaleBounce.hidden).toEqual({ opacity: 0, scale: 0.8 })
    expect(scaleBounce.visible).toHaveProperty('scale', 1)
    expect(scaleBounce.exit).toHaveProperty('scale', 0.8)
  })

  it('visible uses spring transition', () => {
    expect(scaleBounce.visible.transition).toHaveProperty('type', 'spring')
  })
})

describe('rotateIn', () => {
  it('starts rotated and scaled down', () => {
    expect(rotateIn.hidden).toEqual({ opacity: 0, rotate: -10, scale: 0.9 })
    expect(rotateIn.visible).toHaveProperty('rotate', 0)
  })

  it('visible uses spring transition', () => {
    expect(rotateIn.visible.transition).toHaveProperty('type', 'spring')
  })
})

describe('counter', () => {
  it('uses initial/animate with y offset', () => {
    expect(counter.initial).toEqual({ y: 20, opacity: 0 })
    expect(counter.animate).toHaveProperty('y', 0)
  })
})

describe('progressFill', () => {
  it('is a Transition with duration and ease', () => {
    expect(progressFill.duration).toBe(0.8)
    expect(progressFill.ease).toEqual([0.16, 1, 0.3, 1])
  })
})

describe('notificationSlide', () => {
  it('slides in from right', () => {
    expect(notificationSlide.initial).toEqual({ x: 100, opacity: 0 })
    expect(notificationSlide.animate).toHaveProperty('x', 0)
    expect(notificationSlide.exit).toHaveProperty('x', 100)
  })

  it('animate uses spring', () => {
    expect(notificationSlide.animate.transition).toHaveProperty('type', 'spring')
  })
})

describe('tooltipFade', () => {
  it('uses hidden/visible/exit with scale and y', () => {
    expect(tooltipFade.hidden).toEqual({ opacity: 0, y: 4, scale: 0.95 })
    expect(tooltipFade.visible).toEqual({ opacity: 1, y: 0, scale: 1, transition: { duration: 0.15 } })
    expect(tooltipFade.exit).toEqual({ opacity: 0, y: 4, scale: 0.95, transition: { duration: 0.1 } })
  })
})

describe('modalBackdrop', () => {
  it('fades in and out', () => {
    expect(modalBackdrop.hidden).toEqual({ opacity: 0 })
    expect(modalBackdrop.visible).toEqual({ opacity: 1, transition: { duration: 0.2 } })
    expect(modalBackdrop.exit).toEqual({ opacity: 0, transition: { duration: 0.15 } })
  })
})

describe('modalContent', () => {
  it('uses hidden/visible/exit with scale and y', () => {
    expect(modalContent.hidden).toEqual({ opacity: 0, scale: 0.95, y: 20 })
    expect(modalContent.visible).toHaveProperty('y', 0)
    expect(modalContent.visible).toHaveProperty('scale', 1)
    expect(modalContent.exit).toHaveProperty('scale', 0.95)
  })

  it('visible uses spring', () => {
    expect(modalContent.visible.transition).toHaveProperty('type', 'spring')
    expect(modalContent.visible.transition).toHaveProperty('stiffness', 400)
  })
})

describe('emptyState', () => {
  it('uses hidden/visible with scale', () => {
    expect(emptyState.hidden).toEqual({ opacity: 0, scale: 0.9 })
    expect(emptyState.visible).toHaveProperty('scale', 1)
  })

  it('visible has spring with delay', () => {
    expect(emptyState.visible.transition).toHaveProperty('type', 'spring')
    expect(emptyState.visible.transition).toHaveProperty('delay', 0.1)
  })
})

describe('highlight', () => {
  it('uses initial/animate with backgroundColor', () => {
    expect(highlight.initial).toEqual({ backgroundColor: 'transparent' })
    expect(highlight.animate).toHaveProperty('backgroundColor', 'rgba(99, 102, 241, 0.15)')
  })
})

describe('all 11 composable animations', () => {
  const animations = [
    ['pageSlide', pageSlide],
    ['scaleBounce', scaleBounce],
    ['rotateIn', rotateIn],
    ['counter', counter],
    ['progressFill', progressFill],
    ['notificationSlide', notificationSlide],
    ['tooltipFade', tooltipFade],
    ['modalBackdrop', modalBackdrop],
    ['modalContent', modalContent],
    ['emptyState', emptyState],
    ['highlight', highlight],
  ] as const

  for (const [name, anim] of animations) {
    it(`${name} is defined`, () => {
      expect(anim).toBeDefined()
    })
  }
})
