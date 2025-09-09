// Custom Cypress commands for TripChoice testing

declare global {
  namespace Cypress {
    interface Chainable {
      // Personalization commands
      openPersonalizationModal(): Chainable<void>
      fillPersonalizationForm(data: {
        name: string
        persona: string
        vibe: string
        homeCity: string
      }): Chainable<void>

      // Package commands
      searchPackages(query: string): Chainable<void>
      selectPackage(packageSlug: string): Chainable<void>
      selectTravelVariant(type: string, variantName: string): Chainable<void>

      // WhatsApp commands
      checkWhatsAppLink(packageSlug: string): Chainable<void>

      // Filter commands
      applyFilters(filters: {
        themes?: string[]
        destinations?: string[]
        domestic?: boolean
        priceRange?: string
      }): Chainable<void>

      // Flash sale commands
      checkFlashSaleVisible(): Chainable<void>
      verifyFlashSaleDiscount(discountPercent: number): Chainable<void>
    }
  }
}

// Personalization commands
Cypress.Commands.add('openPersonalizationModal', () => {
  cy.get('[data-testid="personalization-button"]').click()
  cy.get('[role="dialog"]').should('be.visible')
})

Cypress.Commands.add('fillPersonalizationForm', (data) => {
  cy.get('#name').clear().type(data.name)
  cy.contains(data.persona).click()
  cy.contains(data.vibe).click()
  cy.get('#homeCity').clear().type(data.homeCity)
  cy.get('button[type="submit"]').click()
})

// Package commands
Cypress.Commands.add('searchPackages', (query) => {
  cy.get('input[placeholder*="search"]').clear().type(query)
  cy.get('button[type="submit"]').click()
})

Cypress.Commands.add('selectPackage', (packageSlug) => {
  cy.get(`[data-testid="package-${packageSlug}"]`).click()
  cy.url().should('include', `/packages/${packageSlug}`)
})

Cypress.Commands.add('selectTravelVariant', (type, variantName) => {
  cy.get(`[data-testid="variant-tab-${type}"]`).click()
  cy.contains(variantName).click()
})

// WhatsApp commands
Cypress.Commands.add('checkWhatsAppLink', (packageSlug) => {
  cy.get('[data-testid="whatsapp-cta"]').should('be.visible').invoke('attr', 'href').should('include', 'wa.me')
})

// Filter commands
Cypress.Commands.add('applyFilters', (filters) => {
  if (filters.themes) {
    filters.themes.forEach(theme => {
      cy.contains(theme).click()
    })
  }

  if (filters.destinations) {
    filters.destinations.forEach(destination => {
      cy.contains(destination).click()
    })
  }

  if (filters.domestic !== undefined) {
    cy.get(`[data-testid="filter-${filters.domestic ? 'domestic' : 'international'}"]`).click()
  }

  if (filters.priceRange) {
    cy.get('select').select(filters.priceRange)
  }
})

// Flash sale commands
Cypress.Commands.add('checkFlashSaleVisible', () => {
  cy.get('[data-testid="flash-sale-ribbon"]').should('be.visible')
})

Cypress.Commands.add('verifyFlashSaleDiscount', (discountPercent) => {
  cy.get('[data-testid="flash-sale-ribbon"]').should('contain', `${discountPercent}%`)
})
