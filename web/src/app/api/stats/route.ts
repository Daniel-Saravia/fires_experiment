import { NextResponse } from 'next/server';
import { getEventStats } from '@/lib/dao/events';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const stats = await getEventStats();
    return NextResponse.json({
      success: true,
      ...stats,
    });
  } catch (error) {
    console.error('[api/stats] Failed to fetch stats', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch stats' },
      { status: 500 },
    );
  }
}
