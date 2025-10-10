import { NextResponse } from 'next/server';
import { getLatestEvents } from '@/lib/dao/events';

export const dynamic = 'force-dynamic';

type RouteContext = {
  params: Promise<{ limit: string }>;
};

export async function GET(_request: Request, context: RouteContext) {
  try {
    const { limit } = await context.params;
    const parsedLimit = Number.parseInt(limit, 10);

    if (Number.isNaN(parsedLimit) || parsedLimit <= 0) {
      return NextResponse.json(
        { success: false, error: 'Limit must be a positive integer' },
        { status: 400 },
      );
    }

    const events = await getLatestEvents(parsedLimit);
    return NextResponse.json({
      success: true,
      count: events.length,
      events,
    });
  } catch (error) {
    console.error('[api/events/latest] Failed to fetch events', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch events' },
      { status: 500 },
    );
  }
}
