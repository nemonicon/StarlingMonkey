import { Suspense } from 'react';
export const dynamic = 'force-dynamic';
async function DelayedContent() {
  await new Promise(resolve => setTimeout(resolve, 30));
  return <p data-testid="stream-ready">NEXT_STREAM_READY</p>;
}
export default function StreamPage() {
  return <section><h1>NEXT_STREAM_SHELL</h1><Suspense fallback={<p data-testid="stream-fallback">NEXT_STREAM_PENDING</p>}><DelayedContent /></Suspense></section>;
}
