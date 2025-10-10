## Overview

The project now ships with a full-stack **Next.js 14 (App Router) + TypeScript** application that replaces the original Flask/Selenium service. A headless Playwright scraper collects fire incident data on an interval, stores it in SQLite through Prisma, and the React UI renders a live feed with supporting stats.

The legacy Python backend still exists for reference, but the Next.js app is the primary entry point going forward.

## New Tech Stack

- **Next.js 14 / React 18** — App Router with server components for data fetching.
- **TypeScript (strict)** — `tsconfig` is configured with `strict` + path aliases.
- **CSS Modules + `globals.css`** — component-scoped styling plus a small global theme.
- **Playwright** — headless browser automation (defaults to Firefox, configurable via `FIRE_SCRAPER_BROWSER`).
- **Prisma ORM + SQLite** — typed data access with a unique index enforcing deduplication.
- **tsx + concurrently** — run the scraper worker alongside `next dev`.

## Prerequisites

- Node.js 18+ (Playwright and Next.js require modern Node features).
- Python 3.11+ (only for the optional data migration script).
- If you are on NixOS, enable `nix-ld` or export Prisma engine env vars as shown below.

## Initial Setup

```bash
git clone git@github.com:Daniel-Saravia/fires_experiment.git
cd fires_experiment/web
npm install
npx playwright install firefox
```

### Import the existing SQLite data

```bash
npm run db:import
```

This copies `backend/data.db` into `web/dev.db`, removes duplicate rows, and adds the Prisma unique/index constraints. Use `--source` / `--destination` flags if your paths differ.

### Generate the Prisma client

Prisma needs precompiled engines that are not available for Nix by default. Export the engine paths before running any Prisma CLI commands:

```bash
export PRISMA_QUERY_ENGINE_LIBRARY="$(pwd)/node_modules/@prisma/engines/libquery_engine-debian-openssl-1.1.x.so.node"
export PRISMA_SCHEMA_ENGINE_BINARY="$(pwd)/node_modules/@prisma/engines/schema-engine-debian-openssl-1.1.x"
export PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
npx prisma generate
```

> **Tip:** On non-Nix systems you can skip those environment variables and run `npx prisma generate` directly.

## Running the stack

```bash
# In /web
npm run dev:full
```

This launches:

- `next dev` — the React app + API routes (`http://localhost:3000` by default).
- `tsx src/worker/scraper.ts` — the Playwright scraper loop refreshing every 10 minutes.

All configuration is environment-driven. Key variables:

- `FIRE_SCRAPER_BROWSER` — `firefox` (default), `chromium`, or `webkit`.
- `SCRAPER_INTERVAL_SECONDS` — scrape cadence (defaults to 600).
- `NEXT_PUBLIC_EVENTS_LIMIT` — number of rows rendered + polled by the UI.

## API Surface (Next.js)

| Route | Description |
|-------|-------------|
| `/api/events` | Full incident list ordered by newest first. |
| `/api/events/latest/[limit]` | Latest `limit` incidents (used by the UI + polling). |
| `/api/stats` | Aggregate counts (total, per status, last 24h). |

Responses mirror the previous Flask endpoints, now delivered by Next.js route handlers.

## Scraper internals (TypeScript)

- `src/lib/scraper/scrape.ts` — Playwright automation with HTML parsing via Cheerio.
- `src/lib/dao/events.ts` — Prisma data-access helpers and serialization.
- `src/worker/scraper.ts` — long-lived worker that traps `SIGINT/SIGTERM` for graceful shutdowns.

## UI highlights

- `src/app/page.tsx` — server component retrieving stats + initial incidents.
- `src/components/events-table.tsx` — client component that polls `/api/events/latest` for updates.
- Styling handled via `page.module.css`, `events-table.module.css`, and `globals.css`.

## Legacy Python backend

The original Flask/Selenium stack still lives in `backend/` for reference or side-by-side testing. It will be removed once the Next.js app is fully validated against production needs. Until then you can still run it with:

```bash
cd backend
source ../fires/bin/activate
python start.py
```

## Useful npm scripts

- `npm run dev` — Next.js dev server only.
- `npm run scrape` — run the scraper worker once (useful for manual testing).
- `npm run dev:full` — run both dev server and scraper together.
- `npm run db:import` — copy and index the legacy SQLite database.
- `npm run build && npm run start` — production build + server.

## Testing & verification checklist

- `npm run scrape` logs “Scrape complete” with inserted/duplicate counts.
- `/api/events`, `/api/stats` respond with data from the imported SQLite file.
- The homepage renders incidents and updates automatically every 60 seconds.
- Prisma client compiles with `npx prisma generate` using the engine env vars on Nix systems.
