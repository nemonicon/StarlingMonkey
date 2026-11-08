import { revalidateTag } from 'next/cache';
export const runtime = 'nodejs';
export async function POST() {
  revalidateTag('next-runtime-fixture-v1', { expire: 0 });
  return Response.json({ marker: 'NEXT_CACHE_REVALIDATED', tag: 'next-runtime-fixture-v1' });
}
