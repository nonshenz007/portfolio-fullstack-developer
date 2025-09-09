# Components Usage

This document summarizes how to use key components and utilities.

- Header (`src/components/header.tsx`):
  - Glass header with 12px blur via `.glass-header` (Tailwind utility).
  - Hides logo on `/`; shows compact logo (28–36px) on other routes.
  - Right side: "Explore" link (cool accent) and Personalize/Hi {name} chip.
  - Focus rings: 2px cool; tap targets ≥44px.

- EditorialTile (`src/components/EditorialTile.tsx`):
  - 4:3 fixed-ratio images using `SafeImage` with `ratio="4:3"`.
  - Rounded-2xl corners, `shadow-e2` base → `shadow-e3` on hover.
  - Caption: Fraunces 22px (`text-tile-title`), metadata with pin/clock/pax icons.
  - Hover reveal with transport tabs, View details, WhatsApp.

- Explore Filters (`src/components/explore-filters.tsx`):
  - Desktop: sticky 240px left rail; Mobile: sheet + trigger.
  - Controls: search, Domestic/International toggle, theme chips, budget ranges.
  - Consumed by `ExploreGrid` which maps state to API filters.

- Footer (`src/components/Footer.tsx`):
  - Surface background with subtle `cloud/10` top border.
  - Slate primary text, Cloud secondary (meta) text.
  - Typography: headings `text-small`, meta `text-meta`.

- Utilities (Tailwind plugin):
  - `.glass-header` (12px blur), `.cinematic-gradient` (cool→ink overlay), `.grain-overlay`.
  - Elevation tokens: `shadow-e1`, `shadow-e2`, `shadow-e3` and alias `.elevation-e*`.

- Tokens (`tailwind.config.js`):
  - Colors: ink, surface, slate, cloud, accent.{cool,warm,midnight,gold}.
  - Font sizes: `text-h1-desk`, `text-h1-mob`, `text-h1-small`, `text-h2`, `text-h3`, `text-tile-title`, `text-body`, `text-small`, `text-meta`.
  - Spacing: `s8`…`s96` (usable in width/height e.g., `w-s48`).

