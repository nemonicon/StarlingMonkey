import { headers } from 'next/headers';
export async function run() {
  // This deliberately has no Next request context. An actual context error is
  // a useful observation; no request-global or AsyncLocalStorage shim is added.
  const value = await headers();
  return JSON.stringify({ library: 'next/headers', entries: Array.from(value) });
}
