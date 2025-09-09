'use client'

import { motion } from 'framer-motion'

type Props = {
  as?: keyof JSX.IntrinsicElements
  delay?: number
  y?: number
  children: React.ReactNode
  className?: string
}

export function Reveal({ as: Tag = 'div', delay = 0, y = 12, children, className }: Props) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '0px 0px -80px 0px' }}
      transition={{ duration: 0.24, ease: [0.2, 0.8, 0.2, 1], delay }}
    >
      {children}
    </motion.div>
  )
}

