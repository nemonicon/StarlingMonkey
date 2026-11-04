// This local source module is bundled as guest JS; node:events is NOT installed.
import * as events from './prototype.mjs';
import { eventsChecks } from './checks.mjs';
import { prototypeChecks } from './prototype-checks.mjs';
let calls = 0;
export async function run() {
  try {
  const namespaceIdentity = (await Promise.resolve(events)) === events;
  return JSON.stringify({ calls: ++calls, namespaceIdentity, cases: eventsChecks(events), profile: prototypeChecks(events) });
  } catch (error) { return JSON.stringify({failure:{name:error.name,code:error.code,message:error.message,stack:error.stack}}); }
}
