'use client'

export function MobileCTAFooter() {
  const handleCallbackClick = () => {
    const form = document.querySelector('form') as HTMLFormElement
    if (form) {
      const submitButton = form.querySelector('button[type="submit"]') as HTMLButtonElement
      if (submitButton) {
        submitButton.click()
      }
    }
  }

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 bg-surface/95 backdrop-blur border-t border-cloud/20 p-3 flex gap-2 md:hidden safe-area-bottom">
      <a href="https://wa.me/919447003974" className="flex-1 px-5 py-3 rounded-full border border-accent-cool/40 text-accent-cool text-center font-medium">
        WhatsApp
      </a>
      <button
        onClick={handleCallbackClick}
        className="flex-1 px-5 py-3 rounded-full bg-accent-warm text-white text-center font-semibold hover:bg-accent-warm/90 transition-colors"
      >
        Request callback
      </button>
    </div>
  )
}
