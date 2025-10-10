import { startScrapingLoop } from '@/lib/scraper/scrape';

async function main() {
  const abortController = new AbortController();

  const shutdown = () => {
    console.info('[scraper] Received shutdown signal, exiting...');
    abortController.abort();
  };

  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);

  await startScrapingLoop({ signal: abortController.signal });
}

main().catch((error) => {
  console.error('[scraper] Fatal error', error);
  process.exit(1);
});
