import * as events from 'node:events';
import { eventsChecks } from './checks.mjs';
import { nativeEventsChecks } from './native-checks.mjs';
import { prototypeChecks } from './prototype-checks.mjs';
import inspectCommonJS from './native-require.cjs';
const snapshotEmitter = new events.EventEmitter();
let snapshotTicks = 0;
snapshotEmitter.on('tick', () => { snapshotTicks++; });
snapshotEmitter.emit('tick');
let calls = 0;
export async function run() {
  try {
    snapshotEmitter.emit('tick');
    return JSON.stringify({ calls: ++calls, snapshotTicks, namespaceIdentity: (await Promise.resolve(events)) === events,
      cases: eventsChecks(events), nativeCases: nativeEventsChecks(events), profile: prototypeChecks(events, {addAbortListenerSupported:true}), commonJS: inspectCommonJS(events.EventEmitter) });
  } catch (error) { return JSON.stringify({ failure: { name: error.name, code: error.code, message: error.message, stack: error.stack } }); }
}
