"use client"

import { motion, useScroll, useTransform, useReducedMotion } from 'framer-motion'

export function SectionTitleReveal({ children }: { children: React.ReactNode }) {
  const reduce = useReducedMotion()
  const { scrollYProgress } = useScroll()
  // Fade in as the page scrolls a bit past the hero
  const y = useTransform(scrollYProgress, [0, 0.15], [12, 0])
  const opacity = useTransform(scrollYProgress, [0, 0.15], [0, 1])

  // Respect reduced motion by not animating (framer will just apply values as-is)
  if (reduce) return <div>{children}</div>
  return (
    <motion.div style={{ y, opacity }}>
      {children}
    </motion.div>
  )
}
