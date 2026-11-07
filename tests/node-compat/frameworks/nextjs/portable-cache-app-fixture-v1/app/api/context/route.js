import { cookies, headers } from 'next/headers';
import { NextResponse } from 'next/server';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export async function GET() {
  const [cookieStore, headerStore] = await Promise.all([cookies(), headers()]);
  const response = NextResponse.json({ marker: 'NEXT_CONTEXT', cookie: cookieStore.get('fixture_token')?.value ?? null, header: headerStore.get('x-fixture-probe') });
  response.cookies.set('fixture_reply', 'set', { httpOnly: true, sameSite: 'lax', path: '/' });
  response.headers.set('x-fixture-response', 'context-ok');
  return response;
}
