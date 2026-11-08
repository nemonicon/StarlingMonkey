'use client';

import { useActionState } from 'react';
import { returnActionValue } from './actions.js';

export default function ActionValueForm() {
  const [value, submit, pending] = useActionState(returnActionValue, '');
  return <form action={submit} data-testid="action-value-form">
    <label>Value <input name="value" required maxLength={64} pattern="[a-z0-9-]+" /></label>
    <button type="submit" data-testid="action-value-submit" disabled={pending}>Submit value</button>
    <p data-testid="action-value-result">{value}</p>
  </form>;
}
