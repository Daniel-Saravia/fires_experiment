import { performance } from 'node:perf_hooks';
import { chromium, firefox, webkit, type BrowserType } from 'playwright';
import { load, type Cheerio } from 'cheerio';
import type { AnyNode } from 'domhandler';
import { parse } from 'date-fns';
import prisma from '@/lib/db';
import { Prisma } from '@/generated/prisma';

const SCRAPE_URL =
  'https://mapportal.phoenix.gov/pfd/apps/dashboards/60bc91a9f225469fb0194b9e9ff623e2';
const SCRAPE_INTERVAL = Number(process.env.SCRAPER_INTERVAL_SECONDS ?? 600);
const BROWSER_NAME = (process.env.FIRE_SCRAPER_BROWSER ?? 'firefox').toLowerCase();

type SupportedBrowser = 'chromium' | 'firefox' | 'webkit';

type EventPayload = {
  title: string;
  location: string;
  datetime: Date;
  channel: string;
  status: string;
};

export type ScrapeResult = {
  inserted: number;
  duplicates: number;
  processed: number;
};

const DATE_FORMATS = [
  'MM/dd/yyyy, hh:mm a',
  'MM/dd/yyyy hh:mm a',
  'MM-dd-yyyy, hh:mm a',
  'MM-dd-yyyy hh:mm a',
  'yyyy-MM-dd HH:mm:ss',
  'yyyy-MM-dd HH:mm',
];

function getBrowser(): BrowserType {
  const fallback: Record<SupportedBrowser, BrowserType> = {
    chromium,
    firefox,
    webkit,
  };

  if ((Object.keys(fallback) as SupportedBrowser[]).includes(BROWSER_NAME as SupportedBrowser)) {
    return fallback[BROWSER_NAME as SupportedBrowser];
  }

  console.warn(
    `[scraper] Unknown FIRE_SCRAPER_BROWSER "${BROWSER_NAME}", defaulting to Firefox.`,
  );
  return firefox;
}

function parseDateTime(value: string) {
  for (const format of DATE_FORMATS) {
    const parsed = parse(value, format, new Date());
    if (!Number.isNaN(parsed.getTime())) {
      return parsed;
    }
  }

  console.warn(`[scraper] Failed to parse datetime "${value}"`);
  return null;
}

function toEvent(row: Cheerio<AnyNode>): EventPayload | null {
  const cells = row.find('td');
  if (cells.length < 5) {
    return null;
  }

  const title = cells.eq(0).text().trim();
  const location = cells.eq(1).text().trim();
  const datetimeRaw = cells.eq(2).text().trim();
  const channel = cells.eq(3).text().trim();
  const status = cells.eq(4).text().trim();

  if (!title || !datetimeRaw) {
    return null;
  }

  const datetime = parseDateTime(datetimeRaw);
  if (!datetime) {
    return null;
  }

  return {
    title,
    location,
    datetime,
    channel,
    status,
  };
}

export async function scrapeOnce(): Promise<ScrapeResult> {
  const browserType = getBrowser();
  const browser = await browserType.launch({ headless: true });
  const context = await browser.newContext({
    javaScriptEnabled: true,
    locale: 'en-US',
  });
  const page = await context.newPage();

  let inserted = 0;
  let duplicates = 0;
  let processed = 0;
  const pendingEvents: EventPayload[] = [];

  try {
    await page.route('**/*.{png,jpg,jpeg,gif,svg}', (route) => route.abort());
    await page.route('**/*.{mp4,mp3,webm}', (route) => route.abort());

    await page.goto(SCRAPE_URL, { waitUntil: 'domcontentloaded', timeout: 45_000 });
    await page.waitForSelector('.external-html', { timeout: 30_000 });
    await page.waitForTimeout(2_000);

    const html = await page.content();
    const $ = load(html);

    $('.external-html').each((_, div) => {
      const rows = $(div).find('table tr');
      rows.each((__, row) => {
        const event = toEvent($(row));
        if (event) {
          processed += 1;
          pendingEvents.push(event);
        }
      });
    });

    for (const event of pendingEvents) {
      try {
        await prisma.event.create({ data: event });
        inserted += 1;
      } catch (error) {
        if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2002') {
          duplicates += 1;
        } else {
          throw error;
        }
      }
    }

    return { inserted, duplicates, processed };
  } finally {
    await page.close();
    await context.close();
    await browser.close();
  }
}

export async function startScrapingLoop(options: { signal?: AbortSignal } = {}) {
  const { signal } = options;

  while (!signal?.aborted) {
    const start = performance.now();
    try {
      const { inserted, duplicates, processed } = await scrapeOnce();
      console.info(
        `[scraper] Scrape complete: processed=${processed}, inserted=${inserted}, duplicates=${duplicates}`,
      );
    } catch (error) {
      console.error('[scraper] Scrape failed', error);
    }

    const elapsed = (performance.now() - start) / 1000;
    const sleepFor = Math.max(0, SCRAPE_INTERVAL - elapsed);
    if (sleepFor > 0) {
      await waitForSeconds(sleepFor, signal);
    }
  }
}

function waitForSeconds(seconds: number, signal?: AbortSignal) {
  return new Promise<void>((resolve) => {
    if (signal?.aborted) {
      resolve();
      return;
    }

    const timeout = setTimeout(resolve, seconds * 1000);
    if (signal) {
      signal.addEventListener(
        'abort',
        () => {
          clearTimeout(timeout);
          resolve();
        },
        { once: true },
      );
    }
  });
}
