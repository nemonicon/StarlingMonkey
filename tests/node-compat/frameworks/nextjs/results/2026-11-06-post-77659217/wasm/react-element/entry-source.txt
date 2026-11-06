import React from 'react';
export function run() {
  const element = React.createElement('p', { id: 'wasm-react' }, 'Hello from real React');
  return JSON.stringify({ library: 'react', type: element.type, key: element.key,
    id: element.props.id, children: element.props.children, elementObject: typeof element === 'object' });
}
