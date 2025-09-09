describe('Personalization Modal', () => {
  beforeEach(() => {
    cy.visit('/')
    // Clear localStorage to ensure clean state
    cy.clearLocalStorage()
  })

  it('personalization_modal_saves_name_and_updates_greeting', () => {
    // Open personalization modal
    cy.get('[data-testid="personalization-button"]').click()

    // Verify modal is open
    cy.get('[role="dialog"]').should('be.visible')
    cy.contains('Personalize Your Experience').should('be.visible')

    // Fill out the form
    cy.get('#name').type('John Doe')
    cy.contains('Couple').click()
    cy.contains('Adventure').click()
    cy.get('#homeCity').type('Mumbai')

    // Submit the form
    cy.get('button[type="submit"]').click()

    // Verify modal closes
    cy.get('[role="dialog"]').should('not.exist')

    // Verify greeting updates
    cy.contains('Hi John Doe!').should('be.visible')

    // Verify data persists in localStorage
    cy.window().then((win) => {
      const stored = JSON.parse(win.localStorage.getItem('tripchoice_personalization') || '{}')
      expect(stored.name).to.equal('John Doe')
      expect(stored.persona).to.equal('couple')
      expect(stored.vibe).to.equal('adventure')
      expect(stored.homeCity).to.equal('Mumbai')
    })

    // Reload page and verify persistence
    cy.reload()
    cy.contains('Hi John Doe!').should('be.visible')
  })

  it('personalization_modal_validates_required_fields', () => {
    // Open modal
    cy.get('[data-testid="personalization-button"]').click()

    // Try to submit empty form
    cy.get('button[type="submit"]').click()

    // Verify validation errors
    cy.contains('Name is required').should('be.visible')
    cy.contains('Please select a persona').should('be.visible')
    cy.contains('Please select a vibe').should('be.visible')
    cy.contains('Home city is required').should('be.visible')
  })

  it('personalization_modal_handles_settings_button_after_save', () => {
    // First save personalization
    cy.get('[data-testid="personalization-button"]').click()
    cy.get('#name').type('Jane Smith')
    cy.contains('Solo Traveler').click()
    cy.contains('Relaxation').click()
    cy.get('#homeCity').type('Delhi')
    cy.get('button[type="submit"]').click()

    // Click settings button again
    cy.get('[data-testid="personalization-button"]').click()

    // Verify form is pre-filled
    cy.get('#name').should('have.value', 'Jane Smith')
    cy.get('#homeCity').should('have.value', 'Delhi')
  })
})
