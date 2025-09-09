import Image from 'next/image'

const LOGO_DATA = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 240 80'><rect width='100%' height='100%' rx='12' fill='%23071C3C'/><text x='50%' y='58%' font-family='Inter, Arial, sans-serif' font-size='42' font-weight='700' fill='white' text-anchor='middle'>TripChoice</text></svg>"

export function ConciergeCard() {
  return (
    <aside className="rounded-2xl border border-cloud/30 bg-surface p-6 shadow-e2">
      <div className="flex items-center gap-4 mb-5">
        <div className="relative h-14 w-14 rounded-full overflow-hidden bg-cloud/30">
          <Image src={LOGO_DATA} alt="Trip Concierge" fill className="object-cover" unoptimized />
        </div>
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cloud/20 border border-cloud/40 text-ink text-sm">Trip Concierge</div>
          <div className="text-slate text-sm mt-1">Real humans. Honest advice.</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-5">
        <a href="/images/README.md" className="rounded-xl border border-cloud/30 bg-surface px-3 py-3 text-ink hover:bg-cloud/10 focus-ring">Visa checklist</a>
        <a href="/explore" className="rounded-xl border border-cloud/30 bg-surface px-3 py-3 text-ink hover:bg-cloud/10 focus-ring">Popular packages</a>
      </div>

      <div className="flex items-center gap-3 mb-5">
        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-full border border-cloud/30">
          <span className="text-ink">4.9★</span>
        </div>
        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-full border border-cloud/30">
          <span className="text-ink">50k+ travelers</span>
        </div>
      </div>

      <div className="mb-5">
        <div className="text-slate text-sm mb-1">Office hours</div>
        <div className="text-ink">10–6 IST (Mon–Sat)</div>
      </div>

      <div className="space-y-2">
        <a href="tel:+919447003974" className="block rounded-xl border border-cloud/30 px-3 py-3 text-ink hover:bg-cloud/10 focus-ring">+91 94470 03974</a>
        <a href="tel:+914849876543" className="block rounded-xl border border-cloud/30 px-3 py-3 text-ink hover:bg-cloud/10 focus-ring">+91 484 987 6543</a>
      </div>
    </aside>
  )
}
