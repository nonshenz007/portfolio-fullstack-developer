describe('Flash Sale', () => {
  beforeEach(() => {
    // Mock flash sale API response
    cy.intercept('GET', '**/flash_sales*', {
      statusCode: 200,
      body: {
        data: [
          {
            id: 'diwali-sale-2024',
            name: 'Diwali Festival Sale',
            packages: ['goa-weekend-001', 'kerala-backwaters-002'],
            discount_percent: 15,
            start_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
            end_at: new Date(Date.now() + 3600000).toISOString(), // 1 hour from now
            seat_cap: 50
          }
        ]
      }
    }).as('getFlashSales')

    cy.visit('/')
  })

  it('flash_sale_countdown_and_price_discount_works', () => {
    // Verify flash sale ribbon is visible
    cy.get('[data-testid="flash-sale-ribbon"]').should('be.visible')
    cy.contains('FLASH SALE').should('be.visible')
    cy.contains('15% OFF').should('be.visible')
    cy.contains('Diwali Festival Sale').should('be.visible')

    // Verify countdown is running
    cy.get('[data-testid="countdown"]').should('be.visible')
    cy.get('[data-testid="countdown"]').should('contain', '59') // Should show minutes

    // Navigate to Goa package (included in flash sale)
    cy.visit('/packages/goa-beach-weekend')

    // Verify discount is applied
    cy.get('[data-testid="price-breakdown"]').should('contain', 'Flash sale discount applied')
    cy.get('[data-testid="discount-amount"]').should('contain', '-15%')
  })

  it('flash_sale_not_applied_to_excluded_packages', () => {
    // Navigate to Dubai package (not in flash sale)
    cy.visit('/packages/dubai-luxury-experience')

    // Verify no flash sale discount
    cy.get('[data-testid="price-breakdown"]').should('not.contain', 'Flash sale discount applied')
    cy.get('[data-testid="flash-sale-ribbon"]').should('not.exist')
  })

  it('flash_sale_ribbon_updates_countdown', () => {
    // Wait for countdown to update
    cy.wait(2000)

    // Verify countdown has decreased
    cy.get('[data-testid="countdown"]').then(($countdown) => {
      const initialTime = $countdown.text()

      cy.wait(2000)

      cy.get('[data-testid="countdown"]').should(($updatedCountdown) => {
        expect($updatedCountdown.text()).not.to.equal(initialTime)
      })
    })
  })

  it('flash_sale_disappears_after_expiry', () => {
    // Mock expired flash sale
    cy.intercept('GET', '**/flash_sales*', {
      statusCode: 200,
      body: {
        data: [
          {
            id: 'expired-sale',
            name: 'Expired Sale',
            packages: ['goa-weekend-001'],
            discount_percent: 20,
            start_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
            end_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago (expired)
            seat_cap: 50
          }
        ]
      }
    }).as('getExpiredFlashSales')

    cy.reload()

    // Verify flash sale ribbon is not visible
    cy.get('[data-testid="flash-sale-ribbon"]').should('not.exist')

    // Verify no discount on package
    cy.visit('/packages/goa-beach-weekend')
    cy.get('[data-testid="price-breakdown"]').should('not.contain', 'Flash sale discount applied')
  })
})
