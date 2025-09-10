# LedgerFlow

## Enterprise Invoice Simulation Engine

LedgerFlow is a powerful desktop application built with Tauri, Svelte, and TypeScript that simulates invoice generation and financial flows for businesses. It helps financial teams model different invoicing strategies and understand their impact on cash flow and revenue.

## Core Features

- **Invoice Simulation**: Generate realistic invoices based on configurable parameters
- **Revenue Forecasting**: Model revenue distribution over time with customizable parameters
- **Template Support**: Support for multiple invoice types (Standard, GST, VAT)
- **Data Visualization**: View invoice metrics and trends through interactive charts
- **Real-time Preview**: See sample invoices as they would appear in production

## Technology Stack

- **Frontend**: Svelte + TypeScript + Tailwind CSS
- **Desktop Runtime**: Tauri (Rust-based)
- **Simulation Engine**: TypeScript with strong typing

## Getting Started

### Prerequisites

- Node.js 16+
- Rust (for Tauri)
- pnpm (recommended)

### Installation

```bash
# Install dependencies
pnpm install

# Start the development server
pnpm dev

# Build for production
pnpm build
```

## Simulation Engine

The core simulation engine (`simulation_engine.ts`) powers the invoice generation logic. It allows for:

- Configurable invoice generation based on date ranges
- Revenue distribution algorithms
- Template-specific tax calculations
- Customer and product data generation

## Project Structure

- `/src/lib/simulation_engine.ts` - Core simulation logic
- `/src/lib/simulation_store.ts` - Svelte store for simulation state
- `/src/routes` - SvelteKit routes and UI components
- `/src-tauri` - Rust-based desktop shell

## License

MIT
