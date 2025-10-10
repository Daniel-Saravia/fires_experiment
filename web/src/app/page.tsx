import EventsTable from '@/components/events-table';
import { getEventStats, getLatestEvents } from '@/lib/dao/events';
import styles from './page.module.css';

const LATEST_LIMIT = Number(process.env.NEXT_PUBLIC_EVENTS_LIMIT ?? 50);

export const dynamic = 'force-dynamic';

export default async function Home() {
  const [events, stats] = await Promise.all([
    getLatestEvents(LATEST_LIMIT),
    getEventStats(),
  ]);

  const statusEntries = Object.entries(stats.statusBreakdown).sort(
    (a, b) => b[1] - a[1],
  );

  return (
    <main className={styles.main}>
      <header className={styles.pageHeader}>
        <span className={styles.pill}>Phoenix Fire Dispatch</span>
        <h1 className={styles.title}>Live Fire Incident Feed</h1>
        <p className={styles.subtitle}>
          A continuously updated mirror of the Phoenix Fire Department dashboard. A
          headless browser collects incident activity, stores it for historical analysis,
          and exposes JSON APIs for this interface.
        </p>
      </header>

      <section className={styles.statsGrid}>
        <div className={styles.statCard} role="status">
          <span className={styles.statLabel}>Total incidents tracked</span>
          <span className={styles.statValue}>{stats.totalEvents.toLocaleString()}</span>
        </div>

        <div className={styles.statCard}>
          <span className={styles.statLabel}>Past 24 hours</span>
          <span className={styles.statValue}>{stats.recent24h.toLocaleString()}</span>
        </div>

        <div className={styles.statCard}>
          <span className={styles.statLabel}>Status breakdown</span>
          <div className={styles.statusList}>
            {statusEntries.length === 0 ? (
              <span>No status data yet</span>
            ) : (
              statusEntries.map(([status, count]) => (
                <span key={status}>
                  <span>{status || 'Unknown'}</span>
                  <strong>{count.toLocaleString()}</strong>
                </span>
              ))
            )}
          </div>
        </div>
      </section>

      <EventsTable initialEvents={events} limit={LATEST_LIMIT} />
    </main>
  );
}
