import type { Transition } from 'framer-motion'

export const spring: Transition = {
  type: 'spring',
  stiffness: 300,
  damping: 30,
}

export const springGentle: Transition = {
  type: 'spring',
  stiffness: 200,
  damping: 25,
}

export const springBouncy: Transition = {
  type: 'spring',
  stiffness: 400,
  damping: 20,
}

export const tween: Transition = {
  type: 'tween',
  duration: 0.3,
  ease: [0.4, 0, 0.2, 1],
}

export const tweenFast: Transition = {
  type: 'tween',
  duration: 0.15,
  ease: [0.4, 0, 0.2, 1],
}

export const tweenSlow: Transition = {
  type: 'tween',
  duration: 0.5,
  ease: [0.16, 1, 0.3, 1],
}

export const layoutSpring: Transition = {
  layout: { type: 'spring', stiffness: 350, damping: 30 },
}
