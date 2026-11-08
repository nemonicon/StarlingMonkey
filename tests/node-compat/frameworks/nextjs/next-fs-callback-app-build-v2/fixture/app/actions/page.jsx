import { submitFixture } from './actions.js';
export default function ActionPage() {
  return <section><h1>NEXT_SERVER_ACTION_FORM</h1><form action={submitFixture} data-testid="server-action"><label>Value <input name="value" defaultValue="fixture-action" maxLength={64} /></label><button type="submit">Submit action</button></form></section>;
}
