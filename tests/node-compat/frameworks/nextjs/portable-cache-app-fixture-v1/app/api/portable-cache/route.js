import { unstable_cache, revalidateTag } from 'next/cache';
import { randomBytes } from 'node:crypto';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const cached = unstable_cache(
  async () => ({
    marker: 'NEXT_PORTABLE_CACHE_VALUE',
    nonce: randomBytes(32).toString('hex'),
  }),
  ['portable-fetch-v1'],
  { revalidate: 3600, tags: ['portable-fetch-v1'] },
);

export async function GET() {
  return Response.json(await cached());
}

export async function POST() {
  revalidateTag('portable-fetch-v1', { expire: 0 });
  return Response.json({
    marker: 'NEXT_PORTABLE_CACHE_REVALIDATED',
    tag: 'portable-fetch-v1',
  });
}
