import React from 'react'

export const metadata = {
  title: 'Styleguide | TripChoice',
  description: 'Design tokens and utilities showcase',
}

function Swatch({ name, className }: { name: string; className: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className={`w-10 h-10 rounded-lg border border-cloud/20 ${className}`} />
      <span className="text-sm text-slate">{name}</span>
    </div>
  )
}

export default function StyleguidePage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <h1 className="font-display text-h2 text-ink mb-8">Styleguide</h1>

      {/* Colors */}
      <section className="mb-12">
        <h2 className="font-semibold text-ink mb-4">Colors</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <Swatch name="Ink" className="bg-ink" />
          <Swatch name="Surface" className="bg-surface" />
          <Swatch name="Slate" className="bg-slate" />
          <Swatch name="Cloud" className="bg-cloud" />
          <Swatch name="Accent / Cool" className="bg-accent-cool" />
          <Swatch name="Accent / Warm" className="bg-accent-warm" />
          <Swatch name="Accent / Midnight" className="bg-accent-midnight" />
          <Swatch name="Accent / Gold" className="bg-accent-gold" />
        </div>
      </section>

      {/* Typography */}
      <section className="mb-12">
        <h2 className="font-semibold text-ink mb-4">Typography</h2>
        <div className="space-y-4">
          <div className="font-display text-h1-desk">Heading H1 Desktop</div>
          <div className="font-display text-h1-mob">Heading H1 Mobile</div>
          <div className="font-display text-h1-small">Heading H1 Small</div>
          <div className="font-display text-h2">Heading H2</div>
          <div className="font-display text-h3">Heading H3</div>
          <div className="font-display text-tile-title">Editorial Tile Title (22px)</div>
          <div className="text-body text-slate">Body text – Inter 16px/1.6</div>
          <div className="text-small text-slate">Small text – 14px</div>
          <div className="text-meta text-cloud">Meta text – 12px</div>
        </div>
      </section>

      {/* Spacing */}
      <section className="mb-12">
        <h2 className="font-semibold text-ink mb-4">Spacing (8pt)</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-4"><div className="w-s8 h-3 bg-cloud/50 rounded" /><span className="text-sm text-slate">s8 = 8px</span></div>
          <div className="flex items-center gap-4"><div className="w-s16 h-3 bg-cloud/50 rounded" /><span className="text-sm text-slate">s16 = 16px</span></div>
          <div className="flex items-center gap-4"><div className="w-s24 h-3 bg-cloud/50 rounded" /><span className="text-sm text-slate">s24 = 24px</span></div>
          <div className="flex items-center gap-4"><div className="w-s32 h-3 bg-cloud/50 rounded" /><span className="text-sm text-slate">s32 = 32px</span></div>
          <div className="flex items-center gap-4"><div className="w-s48 h-3 bg-cloud/50 rounded" /><span className="text-sm text-slate">s48 = 48px</span></div>
          <div className="flex items-center gap-4"><div className="w-s64 h-3 bg-cloud/50 rounded" /><span className="text-sm text-slate">s64 = 64px</span></div>
          <div className="flex items-center gap-4"><div className="w-s96 h-3 bg-cloud/50 rounded" /><span className="text-sm text-slate">s96 = 96px</span></div>
        </div>
      </section>

      {/* Elevation */}
      <section className="mb-12">
        <h2 className="font-semibold text-ink mb-4">Elevation</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-white shadow-e1 border border-cloud/20">shadow-e1</div>
          <div className="p-6 rounded-2xl bg-white shadow-e2 border border-cloud/20">shadow-e2</div>
          <div className="p-6 rounded-2xl bg-white shadow-e3 border border-cloud/20">shadow-e3</div>
        </div>
      </section>

      {/* Utilities */}
      <section className="mb-12">
        <h2 className="font-semibold text-ink mb-4">Utilities</h2>
        <div className="space-y-4">
          <div className="p-6 rounded-2xl border border-cloud/20 bg-surface glass-header">.glass-header</div>
          <div className="p-6 rounded-2xl border border-cloud/20 cinematic-gradient text-white">.cinematic-gradient</div>
          <div className="relative p-6 rounded-2xl border border-cloud/20 overflow-hidden">
            Grain overlay
            <div className="grain-overlay" />
          </div>
        </div>
      </section>
    </div>
  )
}

