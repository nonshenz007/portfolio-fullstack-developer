'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'

interface ThemeContextType {
  isDarkMode: boolean
  toggleDarkMode: () => void
  setDarkMode: (isDark: boolean) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: React.ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)

    // Load theme preference
    const savedTheme = localStorage.getItem('tripchoice_dark_mode')
    let shouldBeDark = false

    if (savedTheme) {
      shouldBeDark = savedTheme === 'true'
    } else {
      // Check system preference
      shouldBeDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    }

    setIsDarkMode(shouldBeDark)
    document.documentElement.classList.toggle('dark', shouldBeDark)

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e: MediaQueryListEvent) => {
      // Only auto-switch if user hasn't manually set a preference
      const savedTheme = localStorage.getItem('tripchoice_dark_mode')
      if (!savedTheme) {
        const newIsDark = e.matches
        setIsDarkMode(newIsDark)
        document.documentElement.classList.toggle('dark', newIsDark)
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode
    setIsDarkMode(newDarkMode)
    localStorage.setItem('tripchoice_dark_mode', newDarkMode.toString())
    document.documentElement.classList.toggle('dark', newDarkMode)
  }

  const setDarkMode = (isDark: boolean) => {
    setIsDarkMode(isDark)
    localStorage.setItem('tripchoice_dark_mode', isDark.toString())
    document.documentElement.classList.toggle('dark', isDark)
  }

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return <>{children}</>
  }

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode, setDarkMode }}>
      {children}
    </ThemeContext.Provider>
  )
}
