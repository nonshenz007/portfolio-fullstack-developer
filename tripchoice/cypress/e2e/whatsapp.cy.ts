describe('WhatsApp Integration', () => {
  beforeEach(() => {
    cy.visit('/packages/goa-beach-weekend')
  })

  it('whatsapp_cta_contains_package_and_params', () => {
    // Select travel options
    cy.get('[data-testid="variant-tab-flight"]').click()
    cy.contains('Premium Flight').click()

    // Select date and pax
    cy.get('input[type="date"]').type('2024-12-25')
    cy.get('select').select('3')

    // Click WhatsApp CTA
    cy.get('[data-testid="whatsapp-cta"]').invoke('attr', 'href').then((href) => {
      // Verify WhatsApp URL structure
      expect(href).to.include('wa.me')
      expect(href).to.include('919876543210') // WhatsApp number

      // Decode the message and verify content
      const url = new URL(href!)
      const message = decodeURIComponent(url.searchParams.get('text') || '')

      expect(message).to.include('Goa Beach Weekend Getaway')
      expect(message).to.include('Premium Flight')
      expect(message).to.include('25')
      expect(message).to.include('3 people')
    })
  })

  it('whatsapp_cta_works_from_home_page', () => {
    cy.visit('/')

    // Click WhatsApp CTA
    cy.get('[data-testid="whatsapp-cta"]').invoke('attr', 'href').then((href) => {
      expect(href).to.include('wa.me')
      expect(href).to.include('919876543210')
    })
  })

  it('whatsapp_cta_minimizes_and_restores', () => {
    // Minimize CTA
    cy.get('[data-testid="whatsapp-cta-minimize"]').click()

    // Verify minimized state
    cy.get('[data-testid="whatsapp-cta"]').should('not.be.visible')
    cy.get('[data-testid="whatsapp-cta-minimized"]').should('be.visible')

    // Restore CTA
    cy.get('[data-testid="whatsapp-cta-minimized"]').click()

    // Verify restored state
    cy.get('[data-testid="whatsapp-cta"]').should('be.visible')
    cy.get('[data-testid="whatsapp-cta-minimized"]').should('not.exist')
  })
})
