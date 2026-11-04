// Proposed core m0.11; Events m0.10 and stream/web m0.9 retained; new native/hosts pending.
import bufferDefault, * as buffer from 'node:buffer';
import childDefault, * as child from 'node:child_process';
import pathDefault, * as path from 'node:path';
import posixDefault, * as posix from 'node:path/posix';
import win32Default, * as win32 from 'node:path/win32';
import Events, * as events from 'node:events';
import * as decoder from 'node:string_decoder';
import * as assertion from 'node:assert';
import * as strictAssertion from 'node:assert/strict';
import * as querystring from 'node:querystring';
import * as util from 'node:util';
import * as utilTypes from 'node:util/types';
import * as sys from 'node:sys';
import * as streamWeb from 'node:stream/web';
import { run as runStreamWeb } from '../foundation-stream-web/production-candidate/native-component.mjs';
import { createIncomingHandler } from '../wasmcloud/http.mjs';
import { runChecks as runBufferAndEntropy } from '../entropy/http.mjs';
import { run as runPath } from '../foundation-path/component.mjs';
import { run as runEvents } from '../foundation-events/native-component.mjs';
import { run as runStringDecoder } from '../foundation-string-decoder/native-component.mjs';
import { run as runAssert } from '../foundation-assert/native-component.mjs';
import { run as runQuerystring } from '../foundation-querystring/native-component.mjs';
import { run as runUtil } from '../foundation-util/native-component.mjs';

const bareIds = ['buffer', 'child_process', 'path', 'path/posix', 'path/win32', 'events', 'string_decoder', 'assert', 'assert/strict', 'querystring', 'util', 'util/types', 'sys', 'stream/web'];
const canonical = [buffer, child, path, posix, win32, events, decoder, assertion, strictAssertion, querystring, util, utilTypes, sys, streamWeb];
const defaults = [bufferDefault, childDefault, pathDefault, posixDefault, win32Default, Events, decoder.default, assertion.default, strictAssertion.default, querystring.default, util.default, utilTypes.default, sys.default, streamWeb.default];
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
  const newDeferred = [];
  for (const [operation, invoke] of [
    ['string_decoder.encoding', () => new loaded[6].StringDecoder('ascii')],
    ['assert.deepStrictEqual', () => loaded[7].deepStrictEqual({}, {})],
    ['assert.CallTracker', () => new loaded[8].CallTracker()],
    ['querystring.unescapeBuffer.nonstring', () => loaded[9].unescapeBuffer(undefined)],
    ['util.inspect', () => loaded[10].inspect({})],
    ['util/types.isProxy', () => new loaded[11].isProxy()],
    ['sys.callbackify', () => loaded[12].callbackify(() => {})],
    ['stream/web.CompressionStream', () => new loaded[13].CompressionStream('gzip')],
    ['stream/web.DecompressionStream', () => loaded[13].DecompressionStream('gzip')],
  ]) {
    let code; try { invoke(); } catch (error) { code = error.code; }
    check(code === 'ERR_SM_NODE_UNSUPPORTED', 'new deferred operation: '+operation);
    newDeferred.push({ operation, code });
  }
  return { newDeferred, phase: 'deployed', firstDeployedCall, canonicalStaticLoaded: true, computedBareImports: true,
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
  const decoderReport = JSON.parse(runStringDecoder());
  const assertReport = JSON.parse(await runAssert());
  const querystringReport = JSON.parse(await runQuerystring());
  const utilReport = JSON.parse(await runUtil());
  for (const [name, result] of [['stringDecoder', decoderReport], ['assert', assertReport], ['querystring', querystringReport], ['util', utilReport]]) {
    check(!result.failure, name+': '+JSON.stringify(result.failure));
    check(result.calls === current, 'foundation call state: '+name);
  }
  const streamWebReport = JSON.parse(await runStreamWeb());
  check(!streamWebReport.failure && streamWebReport.passed && streamWebReport.calls === current, 'stream/web: '+JSON.stringify(streamWebReport.failure));
  report.foundations = { schema: 4, calls: current, aliases, path: pathReport, events: eventReport,
    stringDecoder: decoderReport, assert: assertReport, querystring: querystringReport, util: utilReport, streamWeb: streamWebReport };
  return JSON.stringify(report);
}
export const incomingHandler = createIncomingHandler(runJointChecks);
