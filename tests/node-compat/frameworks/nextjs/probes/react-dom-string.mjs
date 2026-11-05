import React from 'react';
import { renderToString } from 'react-dom/server';
export function run() {
  const html = renderToString(React.createElement('p', { id: 'wasm-ssr' }, 'Hello from real ReactDOM'));
  return JSON.stringify({ library: 'react-dom/server', html });
}
