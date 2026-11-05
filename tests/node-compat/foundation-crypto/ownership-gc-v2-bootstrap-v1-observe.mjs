// Root read-only observation of the genuine GC bootstrap API, never guest code.
import assert from 'node:assert/strict';
import {readFile, lstat, mkdir, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
async function checked(row) {
  assert(row && typeof row.path === 'string' && row.path.startsWith('/'));
  const stat = await lstat(row.path);
  assert(stat.isFile() && !stat.isSymbolicLink());
  const bytes = await readFile(row.path);
  assert.equal(bytes.length, row.bytes);
  assert.equal(sha(bytes), row.sha256);
  return bytes;
}
async function descriptor(path) {
  const bytes = await readFile(path);
  return {path, sha256: sha(bytes), bytes: bytes.length};
}

assert.equal(process.version, 'v22.14.0');
assert.deepEqual(process.execArgv, []);
assert.equal(process.argv.length, 3);
const authorityRow = JSON.parse(process.argv[2]);
const authority = JSON.parse(await checked(authorityRow));
assert.equal(authority.state, 'ROOT_APPROVED_CRYPTO_OWNER355_GC_BOOTSTRAP_API_OBSERVATION_V1');
assert.equal(authority.bootstrapApiAllowed, true);
for (const name of ['engineExecuted', 'guestAllowed', 'keyOperationsAllowed', 'gcWorkloadAllowed', 'operationalAdmission']) assert.equal(authority[name], false);
await checked(authority.entry);
await checked(authority.node);
assert.equal(process.execPath, authority.node.path);
const config = JSON.parse(await checked(authority.bootstrapConfig));
assert.equal(config.toolingIndex.sha256, '08ea93796d6e3402467b4296f5e4fd7173f5b649d14983d18038866ba19f9c56');
const index = JSON.parse(await checked(config.toolingIndex));
const root = config.toolingIndex.path.slice(0, -'/index.json'.length);
for (const row of index.files) await checked({...row, path: `${root}/${row.path}`});
const cliTerminal = JSON.parse(await checked(authority.actualCliTerminal));
assert.equal(cliTerminal.rawExitCode, 0);
assert.equal(cliTerminal.allObservedOwnedGroupsGone, true);
assert.deepEqual(cliTerminal.remainingObservedPids, []);
const cliFrame = JSON.parse(await checked(cliTerminal.stdout));
assert.equal(authority.outputRoot, '/private/tmp/starling-node-compat/crypto-owner355-gc-bootstrap-api-v1');
await mkdir(authority.outputRoot, {mode: 0o700});
const {cryptoOwnerGcBootstrapPreflight} = await import(pathToFileURL(`${root}/bootstrap.mjs`).href);
const frame = await cryptoOwnerGcBootstrapPreflight({configDescriptor: authority.bootstrapConfig});
const serializable = JSON.parse(JSON.stringify(frame));
const framePath = `${authority.outputRoot}/frame.json`;
await writeFile(framePath, JSON.stringify(serializable, null, 2) + '\n', {flag: 'wx'});
assert.deepEqual(serializable, cliFrame);
await frame.recheck();
assert.deepEqual(JSON.parse(JSON.stringify(frame)), serializable);
await checked(authorityRow);
await checked(authority.entry);
await checked(authority.bootstrapConfig);
const result = {
  schemaVersion: 1,
  state: 'ROOT_OBSERVED_CRYPTO_OWNER355_GC_BOOTSTRAP_API_PASSED_V1',
  authority: authorityRow,
  bootstrapConfig: authority.bootstrapConfig,
  actualCliTerminal: authority.actualCliTerminal,
  fullFrame: await descriptor(framePath),
  wholeCliFrameEqual: true,
  internalStableRecheckPassed: true,
  explicitRecheckPassed: true,
  bootstrapBodyExecutions: 3,
  engineExecuted: false,
  guestExecuted: false,
  keyOperationsInvoked: false,
  gcWorkloadInvoked: false,
  operationalAdmission: false,
};
const resultPath = `${authority.outputRoot}/result.json`;
await writeFile(resultPath, JSON.stringify(result, null, 2) + '\n', {flag: 'wx'});
console.log(JSON.stringify({result: await descriptor(resultPath), fullFrame: result.fullFrame}));
