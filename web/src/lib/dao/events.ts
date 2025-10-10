import { subHours } from 'date-fns';
import prisma from '@/lib/db';

type SerializedEvent = {
  id: number;
  title: string;
  location: string;
  channel: string;
  status: string;
  datetimeIso: string;
  datetimeReadable: string;
};

export async function getAllEvents(): Promise<SerializedEvent[]> {
  const events = await prisma.event.findMany({
    orderBy: { datetime: 'desc' },
  });

  return events.map(serializeEvent);
}

export async function getLatestEvents(limit: number): Promise<SerializedEvent[]> {
  const events = await prisma.event.findMany({
    orderBy: { datetime: 'desc' },
    take: limit,
  });

  return events.map(serializeEvent);
}

export async function getEventStats() {
  const [totalEvents, statusCountsRaw, recentCount] = await Promise.all([
    prisma.event.count(),
    prisma.event.groupBy({
      by: ['status'],
      _count: { status: true },
    }),
    prisma.event.count({
      where: {
        datetime: {
          gte: subHours(new Date(), 24),
        },
      },
    }),
  ]);

  const statusBreakdown = statusCountsRaw.reduce<Record<string, number>>(
    (acc, item) => {
      acc[item.status] = item._count.status;
      return acc;
    },
    {},
  );

  return {
    totalEvents,
    statusBreakdown,
    recent24h: recentCount,
  };
}

function serializeEvent(event: {
  id: number;
  title: string;
  location: string;
  datetime: Date;
  channel: string;
  status: string;
}): SerializedEvent {
  return {
    id: event.id,
    title: event.title,
    location: event.location,
    channel: event.channel,
    status: event.status,
    datetimeIso: event.datetime.toISOString(),
    datetimeReadable: event.datetime.toLocaleString('en-US', {
      dateStyle: 'long',
      timeStyle: 'short',
    }),
  };
}
