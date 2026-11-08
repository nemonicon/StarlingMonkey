import { unstable_cache } from 'next/cache';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
let misses = 0;
const cached = unstable_cache(async () => ({ marker: 'NEXT_CACHE_VALUE', generation: ++misses }), ['next-runtime-fixture-v1'], { revalidate: 3600, tags: ['next-runtime-fixture-v1'] });
export async function GET() { return Response.json(await cached()); }
