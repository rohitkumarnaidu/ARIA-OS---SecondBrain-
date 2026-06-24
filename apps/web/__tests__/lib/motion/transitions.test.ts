import { describe, it, expect } from 'vitest'
import {
  spring,
  springGentle,
  springBouncy,
  tween,
  tweenFast,
  tweenSlow,
  layoutSpring,
} from '@/lib/motion/transitions'

describe('spring', () => {
  it('has type spring with stiffness and damping', () => {
    expect(spring.type).toBe('spring')
    expect(spring.stiffness).toBe(300)
    expect(spring.damping).toBe(30)
  })
})

describe('springGentle', () => {
  it('has lower stiffness and damping', () => {
    expect(springGentle.type).toBe('spring')
    expect(springGentle.stiffness).toBe(200)
    expect(springGentle.damping).toBe(25)
  })

  it('is gentler than default spring', () => {
    expect(springGentle.stiffness).toBeLessThan(spring.stiffness!)
    expect(springGentle.damping).toBeLessThan(spring.damping!)
  })
})

describe('springBouncy', () => {
  it('has higher stiffness and lower damping', () => {
    expect(springBouncy.type).toBe('spring')
    expect(springBouncy.stiffness).toBe(400)
    expect(springBouncy.damping).toBe(20)
  })
})

describe('tween', () => {
  it('has type tween with duration and ease', () => {
    expect(tween.type).toBe('tween')
    expect(tween.duration).toBe(0.3)
    expect(tween.ease).toEqual([0.4, 0, 0.2, 1])
  })
})

describe('tweenFast', () => {
  it('has faster duration', () => {
    expect(tweenFast.type).toBe('tween')
    expect(tweenFast.duration).toBe(0.15)
    expect(tweenFast.ease).toEqual([0.4, 0, 0.2, 1])
  })

  it('is faster than tween', () => {
    expect(tweenFast.duration).toBeLessThan(tween.duration!)
  })
})

describe('tweenSlow', () => {
  it('has slower duration with smooth ease', () => {
    expect(tweenSlow.type).toBe('tween')
    expect(tweenSlow.duration).toBe(0.5)
    expect(tweenSlow.ease).toEqual([0.16, 1, 0.3, 1])
  })
})

describe('layoutSpring', () => {
  it('has layout property with spring config', () => {
    expect(layoutSpring.layout).toBeDefined()
    expect(layoutSpring.layout!.type).toBe('spring')
    expect(layoutSpring.layout!.stiffness).toBe(350)
    expect(layoutSpring.layout!.damping).toBe(30)
  })

  it('layout property has all required spring fields', () => {
    const layout = layoutSpring.layout!
    expect(layout).toHaveProperty('type', 'spring')
    expect(layout).toHaveProperty('stiffness')
    expect(layout).toHaveProperty('damping')
    expect(typeof layout.stiffness).toBe('number')
    expect(typeof layout.damping).toBe('number')
  })
})

describe('all transitions', () => {
  it('type values are within expected range for spring transitions', () => {
    for (const t of [spring, springGentle, springBouncy]) {
      expect(t.stiffness).toBeGreaterThanOrEqual(100)
      expect(t.stiffness).toBeLessThanOrEqual(500)
      expect(t.damping).toBeGreaterThanOrEqual(10)
      expect(t.damping).toBeLessThanOrEqual(50)
    }
  })

  it('tween durations are within expected range', () => {
    for (const t of [tween, tweenFast, tweenSlow]) {
      expect(t.duration).toBeGreaterThanOrEqual(0.1)
      expect(t.duration).toBeLessThanOrEqual(1)
    }
  })

  it('all 7 presets are defined', () => {
    expect(spring).toBeDefined()
    expect(springGentle).toBeDefined()
    expect(springBouncy).toBeDefined()
    expect(tween).toBeDefined()
    expect(tweenFast).toBeDefined()
    expect(tweenSlow).toBeDefined()
    expect(layoutSpring).toBeDefined()
  })
})
