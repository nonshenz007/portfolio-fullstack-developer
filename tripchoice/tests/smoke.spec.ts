import { test, expect } from '@playwright/test'

test.describe('TripChoice Smoke Tests', () => {
  test('should save personalization, filter international packages, and click WhatsApp', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/')
    
    // Wait for page to load
    await page.waitForLoadState('networkidle')
    
    // Step 1: Save personalization
    // Look for personalize button or auto-opened modal
    const personalizeButton = page.locator('button:has-text("Personalize")')
    const hiButton = page.locator('button[text*="Hi "]')
    
    // If personalize modal is not auto-opened, click the button
    if (await personalizeButton.isVisible()) {
      await personalizeButton.click()
    }
    
    // Fill out personalization form
    await page.fill('input[placeholder*="What should we call you"]', 'Test User')
    
    // Select persona if dropdown is available
    const personaSelect = page.locator('[data-testid="persona-select"], select:has(option:text("Explorer"))')
    if (await personaSelect.isVisible()) {
      await personaSelect.selectOption('Explorer')
    }
    
    // Select vibe if dropdown is available
    const vibeSelect = page.locator('[data-testid="vibe-select"], select:has(option:text("Chill"))')
    if (await vibeSelect.isVisible()) {
      await vibeSelect.selectOption('Chill')
    }
    
    // Select city if dropdown is available
    const citySelect = page.locator('[data-testid="city-select"], select:has(option:text("Mumbai"))')
    if (await citySelect.isVisible()) {
      await citySelect.selectOption('Mumbai')
    }
    
    // Save preferences
    await page.click('button:has-text("Save preferences")')
    
    // Wait for modal to close and check if name appears in header
    await page.waitForTimeout(2000)
    await expect(page.locator('button:has-text("Hi Test User")')).toBeVisible({ timeout: 5000 })
    
    // Step 2: Navigate to explore page and filter international packages
    await page.goto('/explore')
    await page.waitForLoadState('networkidle')
    
    // Click International filter
    const internationalButton = page.locator('button:has-text("International")')
    await internationalButton.click()
    
    // Wait for packages to load and verify international packages are shown
    await page.waitForTimeout(1000)
    
    // Check that at least one package is visible
    const packageCards = page.locator('[data-testid="package-card"], .package-card, [class*="package"]')
    await expect(packageCards.first()).toBeVisible({ timeout: 10000 })
    
    // Step 3: Open a package and click WhatsApp
    // Click on the first package card or "View details" button
    const firstPackage = packageCards.first()
    const viewDetailsButton = firstPackage.locator('button:has-text("View details"), a:has-text("View details")')
    
    if (await viewDetailsButton.isVisible()) {
      await viewDetailsButton.click()
    } else {
      await firstPackage.click()
    }
    
    // Wait for package page to load
    await page.waitForLoadState('networkidle')
    
    // Look for WhatsApp button and click it
    const whatsappButton = page.locator('button:has-text("WhatsApp"), button:has-text("Enquire")')
    await expect(whatsappButton.first()).toBeVisible({ timeout: 10000 })
    
    // Click WhatsApp button (this will open a new tab/window)
    const [newPage] = await Promise.all([
      page.waitForEvent('popup'),
      whatsappButton.first().click()
    ])
    
    // Verify WhatsApp URL
    expect(newPage.url()).toContain('wa.me')
    await newPage.close()
    
    console.log('✅ Smoke test completed successfully!')
  })
  
  test('should load homepage and show packages', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Check that the page title contains TripChoice
    await expect(page).toHaveTitle(/TripChoice/)
    
    // Check that packages are visible
    const packages = page.locator('[data-testid="package-card"], .package-card, [class*="package"]')
    await expect(packages.first()).toBeVisible({ timeout: 10000 })
    
    console.log('✅ Homepage loads successfully with packages!')
  })
  
  test('should navigate to explore page', async ({ page }) => {
    await page.goto('/explore')
    await page.waitForLoadState('networkidle')
    
    // Check that filters are visible
    const searchInput = page.locator('input[placeholder*="Search"], input[type="search"]')
    await expect(searchInput).toBeVisible({ timeout: 5000 })
    
    // Check that domestic/international toggle is visible
    const domesticButton = page.locator('button:has-text("Domestic")')
    const internationalButton = page.locator('button:has-text("International")')
    
    await expect(domesticButton).toBeVisible()
    await expect(internationalButton).toBeVisible()
    
    console.log('✅ Explore page loads successfully with filters!')
  })
})