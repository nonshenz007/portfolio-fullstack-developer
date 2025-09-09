"use client"

import { useMemo, useState } from 'react'
import { buildWhatsAppLink } from '@/lib/whatsapp'

type FormState = {
  name: string
  countryCode: string
  phone: string
  email: string
  origin: string
  dest: string
  dates: string
  pax: string
  notes: string
  quickCallback: boolean
  preferredTime: string
}

const initialState: FormState = {
  name: '',
  countryCode: '+91',
  phone: '',
  email: '',
  origin: '',
  dest: '',
  dates: '',
  pax: '2',
  notes: '',
  quickCallback: true,
  preferredTime: '',
}

export function ContactForm() {
  const [form, setForm] = useState<FormState>(initialState)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  const isValidPhone = useMemo(() => /^[0-9]{7,15}$/.test(form.phone.replace(/\s|-/g, '')), [form.phone])

  function validate() {
    const e: Record<string, string> = {}
    if (!isValidPhone) e.phone = 'Enter a valid phone number'
    if (!form.countryCode) e.countryCode = 'Select code'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const waLink = useMemo(() => {
    return buildWhatsAppLink({
      name: form.name,
      phone: `${form.countryCode} ${form.phone}`.trim(),
      origin: form.origin,
      dest: form.dest,
      dates: form.dates,
      pax: form.pax,
      notes: form.notes,
      utm: { source: 'contact', medium: 'cta', campaign: 'concierge' },
    })
  }, [form])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    setTimeout(() => {
      setSubmitting(false)
      setDone(true)
    }, 900)
  }

  if (done) {
    return (
      <div className="rounded-2xl border border-cloud/30 bg-surface p-6 shadow-e2">
        <div className="flex items-center gap-3 mb-2">
          <span className="w-2 h-2 rounded-full bg-accent-cool animate-pulse" aria-hidden />
          <div className="text-slate">Assigned to a concierge</div>
        </div>
        <h3 className="font-display text-2xl text-ink mb-3">You’re in good hands.</h3>
        <p className="text-slate mb-4">We’ll call you shortly. Prefer WhatsApp?</p>
        <div className="flex gap-3">
          <a href={waLink} target="_blank" className="px-5 py-3 rounded-full border border-accent-cool/40 text-accent-cool hover:bg-accent-cool/5 focus-ring">Open WhatsApp</a>
          <a href="tel:+919447003974" className="px-5 py-3 rounded-full bg-ink text-surface hover:bg-ink/90 focus-ring">Call now</a>
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={onSubmit} className="rounded-2xl border border-cloud/30 bg-surface p-6 shadow-e2">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Phone first */}
        <div className="md:col-span-2">
          <label className="block text-slate mb-2">Phone</label>
          <div className="flex gap-2">
            <select
              value={form.countryCode}
              onChange={(e) => setForm((f) => ({ ...f, countryCode: e.target.value }))}
              className="w-28 h-14 px-3 rounded-xl border border-cloud/30 bg-surface text-ink focus-ring"
              aria-label="Country code"
            >
              {['+91', '+1', '+44', '+61', '+971'].map((code) => (
                <option key={code} value={code}>{code}</option>
              ))}
            </select>
            <input
              value={form.phone}
              onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
              className={`flex-1 h-14 px-4 rounded-xl border bg-surface text-ink focus-ring ${errors.phone ? 'border-cloud/60' : 'border-cloud/30'}`}
              placeholder="Your number"
              inputMode="tel"
              aria-invalid={!!errors.phone}
            />
          </div>
          {errors.phone && <p className="mt-2 text-slate text-sm">{errors.phone}</p>}
        </div>

        <div>
          <label className="block text-slate mb-2">Name</label>
          <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} className="w-full h-14 px-4 rounded-xl border border-cloud/30 bg-surface text-ink focus-ring" placeholder="Your name" />
        </div>
        <div>
          <label className="block text-slate mb-2">Email</label>
          <input value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} className="w-full h-14 px-4 rounded-xl border border-cloud/30 bg-surface text-ink focus-ring" placeholder="name@email.com" inputMode="email" />
        </div>

        <div>
          <label className="block text-slate mb-2">Origin city</label>
          <input value={form.origin} onChange={(e) => setForm((f) => ({ ...f, origin: e.target.value }))} className="w-full h-14 px-4 rounded-xl border border-cloud/30 bg-surface text-ink focus-ring" placeholder="e.g., Mumbai" />
        </div>
        <div>
          <label className="block text-slate mb-2">Destination</label>
          <input value={form.dest} onChange={(e) => setForm((f) => ({ ...f, dest: e.target.value }))} className="w-full h-14 px-4 rounded-xl border border-cloud/30 bg-surface text-ink focus-ring" placeholder="e.g., Kashmir" />
        </div>

        <div>
          <label className="block text-slate mb-2">Dates</label>
          <input value={form.dates} onChange={(e) => setForm((f) => ({ ...f, dates: e.target.value }))} className="w-full h-14 px-4 rounded-xl border border-cloud/30 bg-surface text-ink focus-ring" placeholder="e.g., 12–18 Oct" />
        </div>
        <div>
          <label className="block text-slate mb-2">Pax</label>
          <input value={form.pax} onChange={(e) => setForm((f) => ({ ...f, pax: e.target.value }))} className="w-full h-14 px-4 rounded-xl border border-cloud/30 bg-surface text-ink focus-ring" placeholder="e.g., 2" inputMode="numeric" />
        </div>

        <div className="md:col-span-2">
          <label className="block text-slate mb-2">Notes</label>
          <textarea value={form.notes} onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))} className="w-full min-h-[120px] px-4 py-3 rounded-xl border border-cloud/30 bg-surface text-ink focus-ring" placeholder="Anything we should know?" />
        </div>

        <div className="md:col-span-2 flex items-center justify-between rounded-xl border border-cloud/30 p-4">
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={form.quickCallback} onChange={(e) => setForm((f) => ({ ...f, quickCallback: e.target.checked }))} className="h-5 w-5 rounded border-cloud/40 text-accent-cool focus-ring" />
            <span className="text-ink">Get a callback in 15 min</span>
          </label>
          {form.quickCallback && (
            <input
              type="time"
              aria-label="Preferred time"
              value={form.preferredTime}
              onChange={(e) => setForm((f) => ({ ...f, preferredTime: e.target.value }))}
              className="h-12 px-3 rounded-md border border-cloud/30 bg-surface text-ink focus-ring"
            />
          )}
        </div>
      </div>

      <div className="mt-5 flex gap-3 flex-wrap">
        <button type="submit" disabled={submitting} className="px-6 py-3 rounded-full bg-accent-warm text-white font-semibold hover:bg-accent-warm/90 disabled:opacity-60 focus-ring">{submitting ? 'Assigning to a concierge…' : 'Request callback'}</button>
        <a href={waLink} target="_blank" className="px-6 py-3 rounded-full border border-accent-cool/40 text-accent-cool hover:bg-accent-cool/5 focus-ring">WhatsApp now</a>
      </div>
    </form>
  )
}

