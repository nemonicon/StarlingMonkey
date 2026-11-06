// DATA only: reads the retained Node oracle; synthesizes labeled guest records.
// Never imports the fixture or node:crypto and never invokes a crypto operation.
import { readFile } from 'node:fs/promises';
import { CONTRACT as C } from './contract.mjs';
import { HashHmacDataError, compareHashHmacReturn, compareHashHmacSequence, parseHashHmacRaw, validateHashHmacNodeOracle } from './comparator.mjs';
const refs = JSON.parse(await readFile(new URL('./references.json', import.meta.url), 'utf8'));
const fixtureManifest = JSON.parse(await readFile(refs.fixtureManifest.path, 'utf8'));
const frames = (await readFile(refs.nodeOracleStdout.path, 'utf8')).trimEnd().split('\n').map(x => JSON.parse(x));
const nodeRawStrings = frames.slice(1).map(x => x.observed.value);
const oracle = validateHashHmacNodeOracle(nodeRawStrings, { fixtureManifest });
const clone = x => JSON.parse(JSON.stringify(x));
const require = (v, m) => { if (!v) throw new Error(m); };
function syntheticNative(ordinal) {
  const r = clone(oracle.records[ordinal - 1]); r.calls = ordinal;
  r.namespaceInspection.defaultFrozen = true;
  for (const d of r.namespaceInspection.namespaceDescriptors) if (d.key.type === 'string') d.value = { type: ['default', 'constants', 'webcrypto', 'subtle'].includes(d.key.value) ? 'object' : 'function', functionName: ['default', 'constants', 'webcrypto', 'subtle'].includes(d.key.value) ? null : d.key.value, opaque: true, fullOpaqueValueClaim: false };
  const named = r.namespaceInspection.namespaceDescriptors.filter(x => x.key.type === 'string' && x.key.value !== 'default');
  r.namespaceInspection.defaultDescriptors = named.map(x => ({ ...x, enumerable: true, configurable: false, writable: false }));
  for (const name of ['prng', 'rng', 'pseudoRandomBytes']) r.namespaceInspection.defaultDescriptors.push({ ...clone(named.find(x => x.key.value === 'randomBytes')), key: { type: 'string', value: name }, enumerable: false, configurable: false, writable: false });
  r.namespaceInspection.defaultDescriptors.push({ key: { type: 'string', value: 'fips' }, kind: 'accessor', enumerable: false, configurable: false, writable: null, value: null, getter: 'function', setter: 'undefined' });
  r.providerAndConstants.ownDescriptors = C.constantNames.map(name => ({ key: { type: 'string', value: name }, kind: 'data', enumerable: true, configurable: false, writable: false, value: { type: 'number', value: C.nativeConstants[name] }, getter: 'undefined', setter: 'undefined' }));
  r.providerAndConstants.opensslVersionNumber = { type: 'number', value: C.nativeConstants.OPENSSL_VERSION_NUMBER };
  for (const p of r.profilePolicy) {
    const result = { kind: 'throw', error: { type: 'object', name: p.id.startsWith('invalid-') ? 'TypeError' : 'Error', code: C.profileErrors[p.id], message: 'SYNTHETIC native-profile refusal', originalIdentityClaim: false } };
    if (p.id === 'invalid-receiver') p.actual = result;
    else p.actual = { outcome: result, cleanup: ['unsupported-input-encoding-hex', 'unsupported-output-encoding-base64'].includes(p.id) ? { attempted: true, kind: 'return', observed: { type: 'string', value: C.knownHashVectors[0].expectedHex } } : { attempted: false } };
  }
  return r;
}
const positive = C.guestCallOrdinals.map(syntheticNative), raw = x => JSON.stringify(x);
const whole = compareHashHmacSequence({ nodeRawStrings, guestRawStrings: positive.map(raw), fixtureManifest });
require(whole.summary.acceptedRecordComparisons === 140 && whole.summary.separateNativePolicyChecks === 56, 'complete synthetic schedule');
let checks = 2; const negativeCases = [];
const accepted = (r, id) => r.nodeComparable.find(x => x.id === id).value;
function negative(name, mutate) {
  const r = clone(positive[0]); mutate(r); let refused = false;
  try { compareHashHmacReturn(raw(r), { expectedCallOrdinal: 1, nodeAcceptedRecords: oracle.acceptedByOrdinal[0], fixtureManifest }); }
  catch (e) { require(e instanceof HashHmacDataError, 'precise validation error for ' + name); refused = true; }
  require(refused, 'negative accepted: ' + name); negativeCases.push(name); checks++;
}
negative('missing positive', r => r.nodeComparable.pop());
negative('duplicate positive', r => { r.nodeComparable[1] = clone(r.nodeComparable[0]); });
negative('reordered positive', r => { [r.nodeComparable[0], r.nodeComparable[1]] = [r.nodeComparable[1], r.nodeComparable[0]]; });
negative('unexpected fixture throw', r => { r.nodeComparable[0] = { id: C.positiveIds[0], unexpectedFixtureThrow: { type: 'null', value: null } }; });
negative('extra positive field', r => { r.nodeComparable[0].value.extra = false; });
negative('truncated digest', r => { accepted(r, 'hash-ascii-abc').actual.outcome.observed.value = 'ba78'; });
negative('wrong full digest', r => { accepted(r, 'hash-ascii-abc').actual.outcome.observed.value = '00'.repeat(32); });
negative('failed consuming operation', r => { accepted(r, 'hash-empty').actual.outcome = clone(r.profilePolicy[0].actual.outcome); });
negative('accepted cleanup attempted', r => { accepted(r, 'hash-empty').actual.cleanup = { attempted: true, kind: 'return', observed: { type: 'string', value: '00'.repeat(32) } }; });
negative('boundary chunk mismatch', r => { accepted(r, 'hash-block-64').partitioned.outcome.observed.value = '00'.repeat(32); });
negative('window sentinel mutation', r => { accepted(r, 'hash-nonzero-window-copy').bufferSentinelsPreserved = false; });
negative('key snapshot lost', r => { accepted(r, 'hmac-key-window-snapshot').callerUnchangedAfterCreate = false; });
negative('output ownership lost', r => { accepted(r, 'hash-output-ownership').priorStableAfterSecond = false; });
negative('wrong output type', r => { accepted(r, 'hash-output-ownership').first.outcome.observed.type = 'Uint8Array'; });
negative('wrong byte value type', r => { accepted(r, 'hash-output-ownership').first.outcome.observed.bytes = '32'; });
negative('finalized hash returned', r => { accepted(r, 'terminal-hash').terminal.repeated = { kind: 'return', observed: { type: 'string', value: '' } }; });
negative('Hmac second digest became throw', r => { accepted(r, 'terminal-hmac').terminal.repeatedHex = clone(accepted(r, 'terminal-hmac').terminal.updateAfter); });
negative('empty Hmac buffer not empty', r => { accepted(r, 'terminal-hmac').terminal.repeatedBuffer.observed.bytes = 1; accepted(r, 'terminal-hmac').terminal.repeatedBuffer.observed.hex = '00'; });
negative('finalized error code missing', r => { accepted(r, 'terminal-hash').terminal.repeated.error.code = null; });
negative('native unsupported accepted like Node', r => { r.profilePolicy[0].actual = clone(oracle.records[0].profilePolicy[0].actual); });
negative('native invalid receiver copied Node nullcode', r => { r.profilePolicy[7].actual = clone(oracle.records[0].profilePolicy[7].actual); });
negative('profile wrong code', r => { r.profilePolicy[3].actual.outcome.error.code = 'OTHER'; });
negative('profile missing case', r => { r.profilePolicy.pop(); });
negative('profile cleanup null', r => { r.profilePolicy[4].actual.cleanup = null; });
negative('profile cleanup throw', r => { r.profilePolicy[4].actual.cleanup = { attempted: true, ...clone(r.profilePolicy[0].actual.outcome) }; });
negative('profile hex cleanup digest wrong', r => { r.profilePolicy[4].actual.cleanup.observed.value = '00'.repeat(32); });
negative('profile base64 cleanup omitted', r => { r.profilePolicy[5].actual.cleanup = { attempted: false }; });
negative('algorithm toString invoked', r => { r.profilePolicy[6].algorithmConversions = 1; });
negative('alias false', r => { r.aliases.bareDefaultObjectSame = false; });
negative('alias wrong type', r => { r.aliases.namedDefaultHashSame = 'true'; });
negative('missing namespace', r => { r.namespaceInspection.actualNames.pop(); });
negative('named callable undefined', r => { r.namespaceInspection.namespaceDescriptors.find(x => x.key.value === 'Cipher').value = { type: 'undefined', value: null }; });
negative('default lost freeze', r => { r.namespaceInspection.defaultFrozen = false; });
negative('default function blank object', r => { r.namespaceInspection.defaultDescriptors.find(x => x.key.value === 'createHash').value = { type: 'object', functionName: null, opaque: true, fullOpaqueValueClaim: false }; });
negative('extra descriptor field', r => { r.namespaceInspection.defaultDescriptors[0].ignored = true; });
negative('missing native constant', r => { r.providerAndConstants.ownDescriptors.pop(); });
negative('native constant wrong value type', r => { r.providerAndConstants.ownDescriptors[0].value.value = '805306640'; });
negative('Node provider number substituted for guest header', r => { r.providerAndConstants.ownDescriptors[0].value.value = 805306608; });
negative('provider identity claimed', r => { r.providerAndConstants.providerRuntimeIdentityObserved = true; });
negative('wrong call ordinal', r => { r.calls = 3; });
negative('string call ordinal', r => { r.calls = '1'; });
negative('native snapshot proof invented', r => { r.limits.liveEvpSnapshotAdmission = true; });
negative('extra top-level ignored field', r => { r.ignored = false; });
function rawNegative(name, text) {
  let refused = false; try { parseHashHmacRaw(text); } catch (e) { require(e instanceof HashHmacDataError, name + ' precise error'); refused = true; }
  require(refused, name + ' refused'); negativeCases.push(name); checks++;
}
rawNegative('duplicate ordinal key', raw(positive[0]).replace('"calls":1', '"calls":1,"calls":1'));
rawNegative('escaped duplicate key', '{"a":1,"\\u0061":2}');
rawNegative('nonfinite JSON number', '{"a":1e309}');
rawNegative('trailing JSON bytes', raw(positive[0]) + 'false');
rawNegative('truncated raw JSON', raw(positive[0]).slice(0, -1));
rawNegative('oversize raw string', ' '.repeat(262145));
for (const [name, options] of [
  ['six guest strings', { guestRawStrings: positive.slice(0, 6).map(raw) }],
  ['two Node oracle strings', { nodeRawStrings: nodeRawStrings.slice(0, 2) }],
  ['sparse Node oracle strings', { nodeRawStrings: new Array(3) }],
  ['null fixture manifest', { fixtureManifest: null }],
  ['fresh ordinal not normalized', { guestRawStrings: positive.map((r, i) => raw(i === 4 ? { ...r, calls: 2 } : r)) }],
  ['whole same-ordinal diagnostics differ', { guestRawStrings: positive.map((r, i) => raw(i === 4 ? { ...r, namespaceInspection: { ...r.namespaceInspection, namespaceObjectsSame: !r.namespaceInspection.namespaceObjectsSame } } : r)) }],
]) {
  let refused = false; try { compareHashHmacSequence({ nodeRawStrings, guestRawStrings: positive.map(raw), fixtureManifest, ...options }); } catch (e) { require(e instanceof HashHmacDataError, name + ' precise error'); refused = true; }
  require(refused, name); negativeCases.push(name); checks++;
}
const differentMessage = clone(positive[0]); accepted(differentMessage, 'terminal-hash').terminal.repeated.error.message = 'Complete native diagnostic message retained separately';
const tolerant = compareHashHmacReturn(raw(differentMessage), { expectedCallOrdinal: 1, nodeAcceptedRecords: oracle.acceptedByOrdinal[0], fixtureManifest });
require(tolerant.record.nodeComparable[18].value.terminal.repeated.error.message === 'Complete native diagnostic message retained separately' && tolerant.comparison.errorDiagnostics.some(x => x.guestMessage === 'Complete native diagnostic message retained separately'), 'only explicit diagnostic message tolerance retains full text'); checks++;
require(oracle.records[0].profilePolicy.slice(0, 6).every(x => x.actual.outcome.kind === 'return') && oracle.records[0].profilePolicy[7].actual.error.code === null, 'actual stock Node policy differences remain'); checks++;
let getterCalls = 0; const accessor = clone(oracle.acceptedByOrdinal[0]); Object.defineProperty(accessor[0], 'value', { enumerable: true, get() { getterCalls++; return {}; } });
try { compareHashHmacReturn(raw(positive[0]), { expectedCallOrdinal: 1, nodeAcceptedRecords: accessor, fixtureManifest }); throw new Error('accessor accepted'); } catch (e) { require(e instanceof HashHmacDataError && getterCalls === 0, 'DATA getters never invoked'); checks++; }
process.stdout.write(JSON.stringify({ schemaVersion: 1, passed: true, checks, negativeCases, acceptedDataSource: 'Actual retained Node22 oracle3 strings', guestInputs: 'SYNTHETIC DATA ONLY; not actual native observations', actualGuestStrings: null, sourceFixtureImported: false, newNodeOracleInvoked: false, hostOrGuestCryptoExecuted: false, componentOrGuestExecuted: false, syntheticSequenceSummary: whole.summary }) + '\n');
