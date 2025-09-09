describe('Package Page', () => {
  beforeEach(() => {
    cy.visit('/packages/goa-beach-weekend')
  })

  it('package_variant_change_updates_price', () => {
    // Get initial price
    cy.get('[data-testid="package-price"]').invoke('text').as('initialPrice')

    // Change variant to premium
    cy.get('[data-testid="variant-tab-flight"]').click()
    cy.contains('Premium Flight').click()

    // Verify price has increased
    cy.get('[data-testid="package-price"]').invoke('text').then((newPrice) => {
      cy.get('@initialPrice').then((initialPrice) => {
        expect(parseInt(newPrice.replace(/[^\d]/g, ''))).to.be.greaterThan(
          parseInt((initialPrice as string).replace(/[^\d]/g, ''))
        )
      })
    })
  })

  it('package_itinerary_accordion_expands_and_collapses', () => {
    // Initially collapsed
    cy.contains('Day 1: Arrival in Goa').should('not.be.visible')

    // Expand first day
    cy.contains('Day 1').click()
    cy.contains('Day 1: Arrival in Goa').should('be.visible')
    cy.contains('Arrive at Goa International Airport').should('be.visible')

    // Collapse first day
    cy.contains('Day 1').click()
    cy.contains('Day 1: Arrival in Goa').should('not.be.visible')
  })

  it('package_pax_selection_updates_total_price', () => {
    // Select 4 people
    cy.get('select').select('4')

    // Verify total price calculation
    cy.get('[data-testid="total-price"]').should('be.visible')
  })

  it('package_shows_correct_package_information', () => {
    // Verify package title
    cy.contains('Goa Beach Weekend Getaway').should('be.visible')

    // Verify package details
    cy.contains('Goa, North Goa, South Goa').should('be.visible')
    cy.contains('3 days').should('be.visible')
    cy.contains('2-8 people').should('be.visible')

    // Verify rating
    cy.contains('4.7').should('be.visible')
  })

  it('package_tabs_switch_correctly', () => {
    // Default tab should be itinerary
    cy.contains('Day 1: Arrival in Goa').should('be.visible')

    // Switch to inclusions tab
    cy.contains('What\'s Included').click()
    cy.contains('Airport transfers').should('be.visible')
    cy.contains('3 nights accommodation').should('be.visible')

    // Switch to policies tab
    cy.contains('Policies').click()
    cy.contains('cancellation').should('be.visible')

    // Switch to reviews tab
    cy.contains('Reviews').click()
    cy.contains('Amazing weekend getaway').should('be.visible')
  })

  it('package_back_button_works', () => {
    // Click back button
    cy.contains('Back to Explore').click()

    // Should navigate to explore page
    cy.url().should('include', '/explore')
  })
})
