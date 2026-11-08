import { unstable_cache } from 'next/cache';
import callbackGeneration from './callback-generation.cjs';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const cached = unstable_cache(async () => ({ marker: 'NEXT_CACHE_VALUE', generation: callbackGeneration.nextCallbackGeneration() }), ['next-runtime-fixture-v1'], { revalidate: 3600, tags: ['next-runtime-fixture-v1'] });
export async function GET() { return Response.json(await cached()); }
