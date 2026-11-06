import { NextRequest, NextResponse } from 'next/server';
export async function run() {
  const request = new NextRequest('https://example.test/hello?name=wasm', { headers: { 'x-probe': 'next-wasm' } });
  const response = NextResponse.json({ path: request.nextUrl.pathname, name: request.nextUrl.searchParams.get('name') });
  response.cookies.set('probe', 'wasm');
  return JSON.stringify({ library: 'next/server', path: request.nextUrl.pathname,
    requestHeader: request.headers.get('x-probe'), status: response.status,
    contentType: response.headers.get('content-type'), body: await response.text(),
    cookie: response.cookies.get('probe')?.value });
}
