import { run } from '../../../lib/compat.mjs';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export async function GET() { return Response.json(await run()); }
