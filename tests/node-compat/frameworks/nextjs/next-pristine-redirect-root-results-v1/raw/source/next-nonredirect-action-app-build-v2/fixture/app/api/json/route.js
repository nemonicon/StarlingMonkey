export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export function GET(request) {
  return Response.json({ marker: 'NEXT_JSON_GET', query: new URL(request.url).searchParams.get('q') ?? '' });
}
export async function POST(request) {
  const text = await request.text();
  if (text.length > 4096) return Response.json({ marker: 'NEXT_JSON_TOO_LARGE' }, { status: 413 });
  let input;
  try { input = JSON.parse(text); } catch { return Response.json({ marker: 'NEXT_JSON_BAD_INPUT' }, { status: 400 }); }
  return Response.json({ marker: 'NEXT_JSON_POST', value: typeof input.value === 'string' ? input.value : null });
}
