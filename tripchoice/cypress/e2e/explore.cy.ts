describe('Explore Page', () => {
  beforeEach(() => {
    cy.visit('/explore')
  })

  it('explore_filters_international_shows_bali_dubai', () => {
    // Click international filter
    cy.contains('International').click()

    // Verify international packages are shown
    cy.contains('Bali Tropical Paradise').should('be.visible')
    cy.contains('Dubai Luxury Experience').should('be.visible')
    cy.contains('Da Nang Vietnam Discovery').should('be.visible')

    // Verify domestic packages are not shown
    cy.contains('Goa Beach Weekend').should('not.exist')
    cy.contains('Kerala Backwaters').should('not.exist')
  })

  it('explore_filters_theme_weekend_shows_relevant_packages', () => {
    // Apply weekend theme filter
    cy.contains('Weekend').click()

    // Verify weekend packages are shown
    cy.contains('Goa Beach Weekend').should('be.visible')

    // Check package has weekend theme badge
    cy.get('[data-testid="package-goa-beach-weekend"]').within(() => {
      cy.contains('Weekend').should('be.visible')
    })
  })

  it('explore_search_functionality_works', () => {
    // Search for specific destination
    cy.get('input[placeholder*="search"]').type('Bali')
    cy.get('button[type="submit"]').click()

    // Verify only Bali package is shown
    cy.contains('Bali Tropical Paradise').should('be.visible')
    cy.contains('Goa Beach Weekend').should('not.exist')
    cy.contains('Dubai Luxury Experience').should('not.exist')
  })

  it('explore_price_filter_works', () => {
    // Apply price filter for under 20k
    cy.get('select').select('10000-20000')

    // Verify only packages in price range are shown
    cy.contains('Goa Beach Weekend').should('be.visible') // ~8.5k
    cy.contains('Kerala Backwaters').should('be.visible') // ~12.5k

    // Higher priced packages should not be shown
    cy.contains('Dubai Luxury Experience').should('not.exist') // ~42k
  })

  it('explore_sort_by_rating_works', () => {
    // Sort by highest rated
    cy.get('select').select('Highest Rated')

    // Verify highest rated packages appear first
    cy.get('[data-testid="package-card"]').first().should('contain', '4.9')
  })

  it('explore_clear_filters_works', () => {
    // Apply multiple filters
    cy.contains('Weekend').click()
    cy.contains('Beach').click()
    cy.get('input[placeholder*="search"]').type('Goa')

    // Verify filtered results
    cy.contains('Goa Beach Weekend').should('be.visible')

    // Clear filters
    cy.contains('Clear All Filters').click()

    // Verify all packages are shown again
    cy.contains('Goa Beach Weekend').should('be.visible')
    cy.contains('Bali Tropical Paradise').should('be.visible')
    cy.contains('Dubai Luxury Experience').should('be.visible')
  })
})
