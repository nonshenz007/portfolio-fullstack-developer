"use client"

import React, { createContext, useContext, useMemo, useState } from "react"

type CollapsibleContextType = {
  open: boolean
  setOpen: (v: boolean) => void
}

const CollapsibleCtx = createContext<CollapsibleContextType | null>(null)

interface RootProps extends React.HTMLAttributes<HTMLDivElement> {
  open?: boolean
  defaultOpen?: boolean
  onOpenChange?: (open: boolean) => void
}

export function Collapsible({
  open: controlledOpen,
  defaultOpen = false,
  onOpenChange,
  className,
  children,
  ...rest
}: RootProps) {
  const [uncontrolledOpen, setUncontrolledOpen] = useState(defaultOpen)
  const isControlled = typeof controlledOpen === 'boolean'
  const open = isControlled ? controlledOpen! : uncontrolledOpen
  const setOpen = (v: boolean) => {
    if (!isControlled) setUncontrolledOpen(v)
    onOpenChange?.(v)
  }

  const value = useMemo(() => ({ open, setOpen }), [open])

  return (
    <CollapsibleCtx.Provider value={value}>
      <div className={className} {...rest}>
        {children}
      </div>
    </CollapsibleCtx.Provider>
  )
}

interface TriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
}

export function CollapsibleTrigger({ asChild, onClick, children, ...rest }: TriggerProps) {
  const ctx = useContext(CollapsibleCtx)
  if (!ctx) throw new Error('CollapsibleTrigger must be used within <Collapsible>')

  const handleClick: React.MouseEventHandler<HTMLButtonElement> = (e) => {
    onClick?.(e)
    if (!e.defaultPrevented) ctx.setOpen(!ctx.open)
  }

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as any, {
      onClick: (e: any) => {
        if (typeof (children as any).props.onClick === 'function') {
          (children as any).props.onClick(e)
        }
        handleClick(e)
      },
      'aria-expanded': ctx.open,
    })
  }

  return (
    <button aria-expanded={ctx.open} onClick={handleClick} {...rest}>
      {children}
    </button>
  )
}

interface ContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export function CollapsibleContent({ style, children, ...rest }: ContentProps) {
  const ctx = useContext(CollapsibleCtx)
  if (!ctx) throw new Error('CollapsibleContent must be used within <Collapsible>')

  if (!ctx.open) return null
  return (
    <div data-state={ctx.open ? 'open' : 'closed'} {...rest}>
      {children}
    </div>
  )
}
