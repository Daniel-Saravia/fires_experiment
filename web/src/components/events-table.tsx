'use client';

import { useEffect, useMemo, useState } from 'react';
import styles from './events-table.module.css';

const REFRESH_INTERVAL_MS = Number(
  process.env.NEXT_PUBLIC_REFRESH_INTERVAL_MS ?? 60_000,
);

export type EventRow = {
  id: number;
  title: string;
  location: string;
  datetimeIso: string;
  datetimeReadable: string;
  channel: string;
  status: string;
};

type EventsTableProps = {
  initialEvents: EventRow[];
  limit?: number;
};

type ApiResponse = {
  success: boolean;
  events: EventRow[];
};

export default function EventsTable({ initialEvents, limit = 50 }: EventsTableProps) {
  const [events, setEvents] = useState<EventRow[]>(initialEvents);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    let timer: NodeJS.Timeout | undefined;
    let isMounted = true;

    const fetchEvents = async () => {
      setIsPolling(true);
      try {
        const response = await fetch(`/api/events/latest/${limit}`, {
          next: { revalidate: 0 },
        });
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        const payload = (await response.json()) as ApiResponse;
        if (payload.success && Array.isArray(payload.events)) {
          if (isMounted) {
            setEvents(payload.events);
            setLastUpdated(new Date());
          }
        }
      } catch (error) {
        console.error('[events-table] Failed to poll for latest events', error);
      } finally {
        if (isMounted) {
          setIsPolling(false);
        }
      }
    };

    const tick = async () => {
      await fetchEvents();
      timer = setTimeout(tick, REFRESH_INTERVAL_MS);
    };

    timer = setTimeout(tick, REFRESH_INTERVAL_MS);

    return () => {
      isMounted = false;
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [limit]);

  const lastUpdatedLabel = useMemo(() => lastUpdated.toLocaleTimeString(), [lastUpdated]);

  return (
    <section className={styles.wrapper}>
      <header className={styles.tableHeader}>
        <h2>Recent Fire Activity</h2>
        <div className={styles.meta}>
          <span>Showing latest {events.length} events</span>
          <span aria-live="polite">
            Updated: {lastUpdatedLabel} {isPolling ? '(refreshing...)' : ''}
          </span>
        </div>
      </header>

      <div className={styles.scrollContainer} role="region" aria-label="Incident feed">
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Location</th>
              <th scope="col">Date / Time</th>
              <th scope="col">Channel</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan={5} className={styles.emptyState}>
                  No events yet. The scraper will populate this table shortly.
                </td>
              </tr>
            ) : (
              events.map((event) => (
                <tr key={event.id}>
                  <td data-title="Title">{event.title}</td>
                  <td data-title="Location">{event.location}</td>
                  <td data-title="Date / Time">
                    <time dateTime={event.datetimeIso}>{event.datetimeReadable}</time>
                  </td>
                  <td data-title="Channel">{event.channel}</td>
                  <td data-title="Status">{event.status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
