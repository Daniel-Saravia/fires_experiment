import { NextResponse } from 'next/server';
import { getAllEvents } from '@/lib/dao/events';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const events = await getAllEvents();
    return NextResponse.json({
      success: true,
      count: events.length,
      events,
    });
  } catch (error) {
    console.error('[api/events] Failed to fetch events', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch events' },
      { status: 500 },
    );
  }
}
