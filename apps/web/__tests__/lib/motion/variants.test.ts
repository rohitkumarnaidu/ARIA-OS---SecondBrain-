import { describe, it, expect } from 'vitest'
import {
  fadeIn,
  fadeInUp,
  fadeInDown,
  fadeInLeft,
  fadeInRight,
  scaleIn,
  slideUp,
  stagger,
  staggerFast,
  listItem,
  cardHover,
  expandCollapse,
  pageTransition,
} from '@/lib/motion/variants'

describe('fadeIn', () => {
  it('has hidden, visible, and exit states', () => {
    expect(fadeIn.hidden).toEqual({ opacity: 0 })
    expect(fadeIn.visible).toHaveProperty('opacity', 1)
    expect(fadeIn.exit).toHaveProperty('opacity', 0)
  })
})

describe('fadeInUp', () => {
  it('starts below and ends at origin', () => {
    expect(fadeInUp.hidden).toHaveProperty('y', 20)
    expect(fadeInUp.visible).toHaveProperty('y', 0)
    expect(fadeInUp.exit).toHaveProperty('y', -10)
  })
})

describe('fadeInDown', () => {
  it('starts above and ends at origin', () => {
    expect(fadeInDown.hidden).toHaveProperty('y', -20)
    expect(fadeInDown.visible).toHaveProperty('y', 0)
    expect(fadeInDown.exit).toHaveProperty('y', 10)
  })
})

describe('fadeInLeft', () => {
  it('starts left and ends at origin', () => {
    expect(fadeInLeft.hidden).toHaveProperty('x', -20)
    expect(fadeInLeft.visible).toHaveProperty('x', 0)
    expect(fadeInLeft.exit).toHaveProperty('x', 20)
  })
})

describe('fadeInRight', () => {
  it('starts right and ends at origin', () => {
    expect(fadeInRight.hidden).toHaveProperty('x', 20)
    expect(fadeInRight.visible).toHaveProperty('x', 0)
    expect(fadeInRight.exit).toHaveProperty('x', -20)
  })
})

describe('scaleIn', () => {
  it('scales from 0.95 to 1', () => {
    expect(scaleIn.hidden).toEqual({ opacity: 0, scale: 0.95 })
    expect(scaleIn.visible).toHaveProperty('scale', 1)
    expect(scaleIn.exit).toHaveProperty('scale', 0.95)
  })
})

describe('slideUp', () => {
  it('slides up from y=40', () => {
    expect(slideUp.hidden).toHaveProperty('y', 40)
    expect(slideUp.visible).toHaveProperty('y', 0)
    expect(slideUp.exit).toHaveProperty('y', 20)
  })

  it('visible has custom ease curve', () => {
    expect(slideUp.visible.transition.ease).toEqual([0.16, 1, 0.3, 1])
  })
})

describe('stagger', () => {
  it('has staggerChildren and delayChildren', () => {
    expect(stagger.visible.transition).toHaveProperty('staggerChildren', 0.08)
    expect(stagger.visible.transition).toHaveProperty('delayChildren', 0.1)
  })

  it('exit reverses stagger', () => {
    expect(stagger.exit.transition).toHaveProperty('staggerDirection', -1)
  })
})

describe('staggerFast', () => {
  it('has faster stagger timings', () => {
    expect(staggerFast.visible.transition.staggerChildren).toBe(0.04)
    expect(staggerFast.visible.transition.delayChildren).toBe(0.05)
  })
})

describe('listItem', () => {
  it('has hidden/visible/exit with x offsets', () => {
    expect(listItem.hidden).toEqual({ opacity: 0, x: -10 })
    expect(listItem.visible).toEqual({ opacity: 1, x: 0 })
    expect(listItem.exit).toEqual({ opacity: 0, x: 10 })
  })
})

describe('cardHover', () => {
  it('has rest, hover, tap states', () => {
    expect(cardHover.rest).toHaveProperty('scale', 1)
    expect(cardHover.hover).toHaveProperty('scale', 1.02)
    expect(cardHover.tap).toHaveProperty('scale', 0.98)
  })

  it('hover has boxShadow', () => {
    expect(cardHover.hover.boxShadow).toBeDefined()
  })
})

describe('expandCollapse', () => {
  it('animates height from 0 to auto', () => {
    expect(expandCollapse.hidden).toHaveProperty('height', 0)
    expect(expandCollapse.visible).toHaveProperty('height', 'auto')
    expect(expandCollapse.exit).toHaveProperty('height', 0)
  })
})

describe('pageTransition', () => {
  it('has initial/animate/exit with y offsets', () => {
    expect(pageTransition.initial).toHaveProperty('y', 20)
    expect(pageTransition.animate).toHaveProperty('y', 0)
    expect(pageTransition.exit).toHaveProperty('y', -10)
  })

  it('animate has custom ease', () => {
    expect(pageTransition.animate.transition.ease).toEqual([0.16, 1, 0.3, 1])
  })
})

describe('all variants', () => {
  const variants = [
    ['fadeIn', fadeIn],
    ['fadeInUp', fadeInUp],
    ['fadeInDown', fadeInDown],
    ['fadeInLeft', fadeInLeft],
    ['fadeInRight', fadeInRight],
    ['scaleIn', scaleIn],
    ['slideUp', slideUp],
    ['stagger', stagger],
    ['staggerFast', staggerFast],
    ['listItem', listItem],
    ['expandCollapse', expandCollapse],
    ['pageTransition', pageTransition],
  ] as const

  for (const [name, variant] of variants) {
    it(`${name} is a valid variant object`, () => {
      expect(variant).toBeTypeOf('object')
      expect(variant).not.toBeNull()
    })
  }
})
