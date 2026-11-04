// Isolated bundled facade; node:buffer stays external and resolves in the guest.
import * as querystring from './prototype.mjs';
import { querystringChecks, prototypeOnlyChecks } from './checks.mjs';
let calls = 0;
export async function run() {
  try {
    return JSON.stringify({ calls: ++calls, namespaceIdentity: (await Promise.resolve(querystring)) === querystring,
      cases: querystringChecks(querystring), profile: prototypeOnlyChecks(querystring) });
  } catch (error) { return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } }); }
}
