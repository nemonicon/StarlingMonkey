import bufferDefault, * as buffer from 'node:buffer';
import childDefault, * as child from 'node:child_process';
import pathDefault, * as path from 'node:path';
import posixDefault, * as posix from 'node:path/posix';
import win32Default, * as win32 from 'node:path/win32';
import Events, * as events from 'node:events';
import { createIncomingHandler } from '../wasmcloud/http.mjs';
import { runChecks as runBufferAndEntropy } from '../entropy/http.mjs';
import { run as runPath } from '../foundation-path/component.mjs';
import { run as runEvents } from '../foundation-events/native-component.mjs';

const bareIds = ['buffer', 'child_process', 'path', 'path/posix', 'path/win32', 'events'];
const canonical = [buffer, child, path, posix, win32, events];
const defaults = [bufferDefault, childDefault, pathDefault, posixDefault, win32Default, Events];
const loaded = [];
let calls = 0;
function check(value, message) { if (!value) throw new Error(message); }
async function dynamicAliases(firstDeployedCall) {
  const aliases = [];
  for (let i = 0; i < bareIds.length; i++) {
    const id = bareIds[i];
    // A computed import preserves the raw bare id. Literal imports would be
    // canonicalized by the bundler and fail to test the deployed loader path.
    const namespace = await import(id);
    const again = await import(id);
    check(namespace === again, 'dynamic bare module cache: '+id);
    if (firstDeployedCall) loaded[i] = namespace;
    else check(loaded[i] === namespace, 'retained module cache: '+id);
    const names = Object.keys(canonical[i]).sort();
    check(JSON.stringify(Object.keys(namespace).sort()) === JSON.stringify(names), 'dynamic exports: '+id);
    check(names.every(name => namespace[name] === canonical[i][name]), 'dynamic shared export values: '+id);
    check(namespace.default === defaults[i], 'dynamic default identity: '+id);
    check(namespace.then === undefined && namespace.missing === undefined, 'safe namespace inspection: '+id);
    check((await Promise.resolve(namespace)) === namespace, 'namespace is not thenable: '+id);
    aliases.push({ id, exportCount: names.length, namespaceType: typeof namespace, defaultType: typeof namespace.default,
      cache: true, exportValues: true, defaultIdentity: true, thenType: typeof namespace.then,
      canonicalNamespaceSame: namespace === canonical[i] });
  }
  const bareEvents = loaded[5]; let rejectedCall, rejectedConstruction;
  try { bareEvents.once(); } catch (error) { rejectedCall = error.code; }
  try { new bareEvents.EventEmitterAsyncResource(); } catch (error) { rejectedConstruction = error.code; }
  check(rejectedCall === 'ERR_SM_NODE_UNSUPPORTED' && rejectedConstruction === rejectedCall, 'dynamic deferred operations');
  check(loaded[0].Buffer === globalThis.Buffer && loaded[5].EventEmitter === Events, 'dynamic constructor identities');
  return { phase: 'deployed', firstDeployedCall, canonicalStaticLoaded: true, computedBareImports: true,
    aliases, rejectedCall, rejectedConstruction, typedConstants: {
      pathSep: typeof loaded[2].sep, eventErrorMonitor: typeof bareEvents.errorMonitor,
      captureRejections: typeof bareEvents.captureRejections, defaultMaxListeners: typeof bareEvents.defaultMaxListeners,
    } };
}
async function runJointChecks() {
  const current = ++calls;
  // Execute before the check modules run. No bare import occurs at top level.
  const aliases = await dynamicAliases(current === 1);
  const report = JSON.parse(await runBufferAndEntropy());
  const pathReport = JSON.parse(runPath());
  const eventReport = JSON.parse(await runEvents());
  check(!pathReport.failure && !eventReport.failure, JSON.stringify({path:pathReport.failure,events:eventReport.failure}));
  check(pathReport.calls === current && eventReport.calls === current && eventReport.snapshotTicks === current + 1, 'foundation component state');
  report.foundations = { schema: 1, calls: current, aliases, path: pathReport, events: eventReport };
  return JSON.stringify(report);
}
export const incomingHandler = createIncomingHandler(runJointChecks);
