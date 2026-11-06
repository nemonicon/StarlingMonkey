import React from 'react';
import { renderToReadableStream } from 'react-dom/server.edge';
export async function run() {
  const stream = await renderToReadableStream(React.createElement('p', { id: 'wasm-ssr' }, 'Hello from real ReactDOM'));
  const reader = stream.getReader(), decoder = new TextDecoder();
  let html = '', bytes = 0;
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      bytes += value.byteLength;
      if (bytes > 1024 * 1024) throw new Error('SSR probe output exceeds complete one MiB bound');
      html += decoder.decode(value, { stream: true });
    }
    html += decoder.decode();
  } finally { reader.releaseLock(); }
  return JSON.stringify({ library: 'react-dom/server.edge', html, bytes });
}
