import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
// Deliberate separate compatibility probe, never a polyfill or silent fallback.
export async function GET() {
  const text = await readFile(path.join(process.cwd(), 'fixtures', 'message.txt'), 'utf8');
  return Response.json({ marker: 'NEXT_FS_CRYPTO', text, sha256: createHash('sha256').update(text).digest('hex') });
}
