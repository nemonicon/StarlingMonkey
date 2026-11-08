'use client';
import { useState } from 'react';
export default function Counter() {
  const [count, setCount] = useState(0);
  return <section><p data-testid="counter-value">NEXT_CLIENT_COUNT:{count}</p><button data-testid="counter-increment" onClick={() => setCount(value => value + 1)}>Increment</button></section>;
}
