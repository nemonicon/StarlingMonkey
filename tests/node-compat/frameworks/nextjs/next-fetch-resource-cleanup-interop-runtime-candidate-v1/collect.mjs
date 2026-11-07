// Dormant single ordinary interop probe. No constructor, Node oracle or browser.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createServer} from 'node:net';
import {createReadStream} from 'node:fs';
import {readFile, readdir, lstat, realpath, mkdir, open, chmod} from 'node:fs/promises';
import {dirname, join, relative, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const read = async path => JSON.parse(await readFile(path, 'utf8'));
async function row(path) {
  const hash = createHash('sha256'); let bytes = 0;
  for await (const block of createReadStream(path)) { hash.update(block); bytes += block.length; }
  return {path, sha256: hash.digest('hex'), bytes};
}
async function verify(ref) {
  assert.equal(resolve(ref.path), ref.path); assert.equal(await realpath(ref.path), ref.path);
  const stat = await lstat(ref.path); assert(stat.isFile() && !stat.isSymbolicLink() && stat.nlink === 1);
  assert.deepEqual(await row(ref.path), ref);
}
async function walk(root) {
  const files = [], dirs = ['.'];
  async function visit(path) {
    for (const name of (await readdir(path)).sort()) {
      const child = join(path, name), stat = await lstat(child);
      assert(!stat.isSymbolicLink());
      if (stat.isDirectory()) { dirs.push(relative(root, child)); await visit(child); }
      else { assert(stat.isFile() && stat.nlink === 1); files.push(relative(root, child)); }
    }
  }
  await visit(root); return {files: files.sort(), dirs: dirs.sort()};
}
async function family(ref) {
  await verify(ref); const root = dirname(ref.path), index = await read(ref.path);
  const names = index.files.map(item => item.path); assert.equal(new Set(names).size, names.length);
  const expectedDirs = new Set(['.']);
  for (const name of names) {
    assert(!name.startsWith('/') && !name.split('/').includes('..'));
    for (let parent = dirname(name); parent !== '.'; parent = dirname(parent)) expectedDirs.add(parent);
  }
  const actual = await walk(root);
  assert.deepEqual(actual.files, [...names, 'index.json'].sort());
  assert.deepEqual(actual.dirs, [...expectedDirs].sort());
  for (const item of index.files) await verify({path: join(root, item.path), sha256: item.sha256, bytes: item.bytes});
}
async function durable(path, bytes, fresh = false) {
  const handle = await open(path, fresh ? 'wx' : 'w', 0o600);
  try { await handle.writeFile(bytes); await handle.sync(); } finally { await handle.close(); }
}
const errorData = error => ({type: typeof error, isNull: error === null,
  name: error?.name ?? null, message: error?.message ?? String(error), stack: error?.stack ?? null,
  code: error?.code ?? null});
const clean = terminal => terminal.rawExitCode === 0 && terminal.timeout === false && terminal.forcedCleanup === false &&
  terminal.parentOwnedGroupGone === true && terminal.allObservedOwnedGroupsGone === true &&
  ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'].every(key =>
    Array.isArray(terminal[key]) && terminal[key].length === 0) && terminal.finalGroups.every(group => group.alive === false);
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
async function waitBounded(promise, ms) {
  let timer; try { await Promise.race([promise, new Promise(resolve => { timer = setTimeout(resolve, ms); })]); }
  finally { clearTimeout(timer); }
}

async function main() {
  assert.equal(process.version, 'v22.14.0'); assert.deepEqual(process.execArgv, []);
  assert.equal(process.env.NODE_OPTIONS, undefined); assert.equal(process.argv.length, 3);
  const authpath = resolve(process.argv[2]), authority = await row(authpath), a = await read(authpath);
  const plan = await read(join(HERE, 'plan.json'));
  assert.equal(a.state, 'ROOT_FILE_URL_INTEROP_PROBE_AUTHORIZED_V1');
  assert.deepEqual(a.sourceIndex, await row(join(HERE, 'index.json')));
  assert.deepEqual(a.plan, await row(join(HERE, 'plan.json')));
  assert(typeof a.runId === 'string' && /^[a-z0-9][a-z0-9-]{0,47}$/.exec(a.runId)?.[0] === a.runId);
  for (const key of ['ordinaryProbeAllowed', 'loopbackServeAllowed', 'fixtureStagingAllowed']) assert.equal(a[key], true);
  for (const key of ['componentConstructionAllowed', 'nodeControlAllowed', 'browserAllowed', 'appMountAllowed',
    'networkBeyondLoopbackAllowed', 'fullNextAcceptanceAllowed', 'adoptionAllowed']) assert.equal(a[key], false);
  assert.equal(plan.mode, 'interop'); assert.equal(plan.requests, 1); assert.equal(plan.actionsAllowed, false);
  assert.equal(plan.prospectiveActualBindingsPending, false, 'Actual full build and INIT pins must be accepted before launch');
  assert.deepEqual(a.engine, plan.expectedEngine); assert.deepEqual(a.nativeMetadata, plan.expectedNativeMetadata);
  assert.deepEqual(a.component, plan.expectedComponent); assert.deepEqual(a.componentAudit, plan.expectedComponentAudit);
  assert.deepEqual(a.constructionResult, plan.expectedConstructionResult);
  assert.deepEqual(a.constructionDataReview, plan.expectedConstructionDataReview);
  assert.deepEqual(a.constructionCallerIndex, plan.constructionCallerIndex);
  assert(Array.isArray(a.engineBuildEvidence) && a.engineBuildEvidence.length > 0);
  assert(Array.isArray(a.nativeProtectedInputs) && a.nativeProtectedInputs.length > 0);
  assert(Array.isArray(a.nativeSourceFamilies));
  assert.equal(a.rootReview.fullNativeAndWholeWorldGuardsRequired, true);
  for (const key of ['argv', 'environment', 'outputRoot', 'port', 'fixtureRoot']) assert.equal(Object.hasOwn(a, key), false);
  const extra = [];
  async function protect() {
    await verify(authority); await family(a.sourceIndex);
    for (const ref of [...plan.sourceFamilies, ...a.nativeSourceFamilies]) await family(ref);
    for (const key of ['node', 'wasmtime', 'monitor', 'probeEntry', 'constructionPlan', 'expectedEngine',
      'expectedNativeMetadata', 'fullBuildReview', 'adapter']) await verify(plan[key]);
    for (const key of ['engine', 'nativeMetadata', 'constructionResult', 'constructionCallerIndex', 'constructionRootStarted',
      'constructionRootTerminal', 'constructionWorldGuard', 'constructionDataReview', 'component', 'componentAudit']) await verify(a[key]);
    for (const ref of [...extra, ...a.engineBuildEvidence, ...a.nativeProtectedInputs]) await verify(ref);
  }
  await protect();
  const construction = await read(a.constructionResult.path), ctorPlan = await read(plan.constructionPlan.path);
  const ctorAuthority = await read(construction.rootAuthority.path), audit = await read(a.componentAudit.path);
  const constructionReview = await read(a.constructionDataReview.path);
  assert.equal(constructionReview.state, plan.expectedConstructionReviewState);
  assert.equal(constructionReview.verifiedPassed, true); assert.equal(constructionReview.entryMode, 'interop');
  for (const [key, expected] of Object.entries({actualResult: a.constructionResult, rootAuthority: construction.rootAuthority,
    callerIndex: plan.constructionCallerIndex, plan: plan.constructionPlan, component: a.component,
    componentAudit: a.componentAudit, engine: a.engine, nativeMetadata: a.nativeMetadata,
    inputSourceIndex: plan.probeSourceIndex, inputEntry: plan.probeEntry, fullBuildReview: plan.fullBuildReview}))
    assert.deepEqual(constructionReview[key], expected);
  for (const key of ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'filesystemFixtureMountedAtInit',
    'deployedImportOrFilesystemProbeInvoked', 'runtimeAccepted', 'nodeParityProved',
    'productionProfilePromoted']) assert.equal(constructionReview[key], false);
  for (const [key, expected] of Object.entries(plan.expectedConstructionReviewFixedValues))
    assert.deepEqual(constructionReview[key], expected);
  extra.push(construction.rootAuthority, construction.plan);
  assert.equal(construction.passed, true); assert.equal(construction.error, null);
  assert.equal(construction.state, 'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2');
  assert.equal(construction.entryMode, 'interop'); assert.deepEqual(construction.plan, plan.constructionPlan);
  assert.deepEqual(construction.callerIndex, plan.constructionCallerIndex); assert.equal(construction.finalProtection.unchanged, true);
  for (const key of ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'productionProfilePromoted']) assert.equal(construction[key], false);
  assert.deepEqual(ctorPlan.inputSourceIndex, plan.probeSourceIndex); assert.deepEqual(ctorPlan.entries, {interop: plan.probeEntry});
  assert.deepEqual(ctorPlan.worldSourceIndex, plan.worldSourceIndex); assert.equal(ctorPlan.witDirectory, plan.witDirectory);
  assert.deepEqual(ctorPlan.selectedInterfaces, plan.selectedInterfaces);
  assert.equal(ctorAuthority.state, 'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2'); assert.equal(ctorAuthority.entryMode, 'interop');
  assert.deepEqual(ctorAuthority.callerIndex, plan.constructionCallerIndex);
  assert.deepEqual(construction.artifacts.engineBuildEvidence, a.engineBuildEvidence);
  for (const [key, expected] of Object.entries({component: a.component, componentAudit: a.componentAudit,
    engine: a.engine, nativeMetadata: a.nativeMetadata, inputEntry: plan.probeEntry, inputSourceIndex: plan.probeSourceIndex,
    adapter: plan.adapter})) assert.deepEqual(construction.artifacts[key], expected);
  const {validateNative} = await import('./native-model.mjs');
  const native = await read(a.nativeMetadata.path); validateNative(native, a, ctorAuthority);
  assert.equal(native.metadataKind, 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1');
  assert.equal(native.nativePolicyInputCount, 435); assert.equal(native.buildSupportInputCount, 387); assert.equal(native.embeddingInputCount, 3);
  assert(Array.isArray(native.actualCompileRows) && native.actualCompileRows.length === 80);
  assert(Array.isArray(native.actualSeparateEmbeddingCompileRows) && native.actualSeparateEmbeddingCompileRows.length === 1);
  const loader = native.nativePolicyInputManifest.filter(ref => ref.path === 'runtime/script_loader.cpp');
  assert.equal(loader.length, 1); assert.equal(loader[0].sha256, plan.interopLoaderAfterimage.sha256);
  const review = await read(plan.fullBuildReview.path);
  assert.equal(review.verifiedPassed, true); assert.deepEqual(review.engine, a.engine); assert.deepEqual(review.metadata, a.nativeMetadata);
  assert(a.engineBuildEvidence.some(ref => ref.path === plan.fullBuildReview.path && ref.sha256 === plan.fullBuildReview.sha256 && ref.bytes === plan.fullBuildReview.bytes));
  assert.equal(audit.state, 'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1'); assert.equal(audit.passed, true);
  assert.deepEqual(audit.component, a.component); assert.deepEqual(audit.engine, a.engine); assert.deepEqual(audit.nativeMetadata, a.nativeMetadata);
  assert.equal(audit.entryMode, 'interop'); assert.equal(audit.allEmittedVersion, '0.2.10');
  assert.deepEqual([...audit.selectedInterfaces].sort(), [...plan.selectedInterfaces].sort()); assert.equal(plan.selectedInterfaces.length, 13);
  assert.equal(new Set(audit.emittedImports).size, audit.emittedImports.length);
  assert(audit.emittedImports.every(name => plan.selectedInterfaces.includes(name) && name.endsWith('@0.2.10')));
  assert.deepEqual(audit.exports, ['wasi:http/incoming-handler@0.2.10']); assert.equal(audit.noExternalPreview1OrCustomImports, true);
  const world = await read(a.constructionWorldGuard.path);
  assert.equal(world.unchanged, true); assert.deepEqual(world.before, world.after);
  assert.deepEqual(world.before.sourceIndex, plan.worldSourceIndex); assert.equal(world.before.members, 28); assert.equal(world.before.witFiles, 8);
  assert.equal(world.before.exactFileAndDirectoryMembership, true); assert.equal(world.before.noSymlinkOrHardlinkAliases, true);
  const cs = await read(a.constructionRootStarted.path), ct = await read(a.constructionRootTerminal.path);
  assert(clean(ct)); assert.equal(cs.pid, ct.pid); assert.equal(cs.timeoutSeconds, 2400);
  assert.deepEqual(cs.authority, ct.authority); assert.deepEqual(cs.authority, construction.rootAuthority);
  await verify(ct.authority); extra.push(ct.authority, ct.stdout, ct.stderr);
  assert.deepEqual(construction.commands.map(command => command.label), ['componentize-init', 'component-validate', 'component-wit']);
  for (const command of construction.commands) {
    await verify(command.terminal); const terminal = await read(command.terminal.path); assert(clean(terminal));
    assert.deepEqual(terminal.authority, construction.rootAuthority); assert.equal(command.rawExitCode, 0); assert.equal(command.clean, true);
    assert.deepEqual(command.stdout, terminal.stdout); assert.deepEqual(command.stderr, terminal.stderr);
    extra.push(command.terminal, terminal.stdout, terminal.stderr);
  }
  await protect();
  const output = plan.outputPrefix + '-' + a.runId; assert.equal(resolve(output), output);
  assert.equal(process.env.TMPDIR, join(output, 'tmp'));
  await mkdir(output, {mode: 0o700});
  for (const name of ['tmp', 'xdg-cache', 'xdg-config', 'xdg-data']) await mkdir(join(output, name), {mode: 0o700});
  const result = {schemaVersion: 1, state: 'INTEROP_FILE_URL_PROBE_IN_PROGRESS_V1', runId: a.runId, rootAuthority: authority,
    sourceIndex: a.sourceIndex, probeSourceIndex: plan.probeSourceIndex, constructionResult: a.constructionResult,
    component: a.component, componentAudit: a.componentAudit, engine: a.engine, nativeMetadata: a.nativeMetadata,
    fixtures: null, response: null, errors: [], server: null, nodeControlExecuted: false,
    interopProfileMatched: false, nodeCompatibilityAccepted: false, fullNextAcceptance: false, adoption: false};
  const save = () => durable(join(output, 'result.json'), JSON.stringify(result, null, 2) + '\n');
  await save(); const handles = []; let lease, host, hostDone, hostExit = null, stopping = false;
  async function fixtureRecords() {
    const root = join(output, 'fixtures'), actual = await walk(root), files = [];
    assert.deepEqual(actual.files, plan.fixtures.map(ref => ref.relativePath).sort()); assert.deepEqual(actual.dirs, ['.']);
    assert.equal((await lstat(root)).mode & 0o777, 0o555);
    for (const source of plan.fixtures) {
      const path = join(root, source.relativePath), stat = await lstat(path), original = await lstat(source.source.path);
      assert.equal(stat.mode & 0o777, 0o444); assert.equal(stat.nlink, 1);
      assert(stat.dev !== original.dev || stat.ino !== original.ino);
      const ref = await row(path); assert.equal(ref.sha256, source.source.sha256); assert.equal(ref.bytes, source.source.bytes);
      files.push({...ref, mode: 0o444, dev: stat.dev, ino: stat.ino, nlink: stat.nlink});
    }
    const stat = await lstat(root);
    return {root, files, mode: 0o555, dev: stat.dev, ino: stat.ino, nlink: stat.nlink,
      physicalReadOnlyOnly: true, readonlyWasiPreopenRightsProved: false};
  }
  try {
    const root = join(output, 'fixtures'); await mkdir(root, {mode: 0o700});
    for (const fixture of plan.fixtures) {
      assert(!fixture.relativePath.includes('/') && fixture.guestPath === '/probe/' + fixture.relativePath);
      await verify(fixture.source); const path = join(root, fixture.relativePath);
      await durable(path, await readFile(fixture.source.path), true); await chmod(path, 0o444);
    }
    await chmod(root, 0o555); result.fixtures = await fixtureRecords(); await save();
    lease = createServer(); await new Promise((yes, no) => { lease.once('error', no); lease.listen({host: '127.0.0.1', port: 0, exclusive: true}, yes); });
    const address = lease.address(); assert(address && typeof address === 'object' && address.address === '127.0.0.1');
    const origin = 'http://127.0.0.1:' + address.port;
    result.portLease = {origin, port: address.port, singleAttempt: true, fallbackAllowed: false}; await save();
    await protect(); await new Promise((yes, no) => lease.close(error => error ? no(error) : yes())); lease = null;
    const stdout = await open(join(output, 'wasmtime.stdout.log'), 'wx', 0o600);
    handles.push(stdout);
    const stderr = await open(join(output, 'wasmtime.stderr.log'), 'wx', 0o600);
    handles.push(stderr);
    const args = ['serve', '--addr', '127.0.0.1:' + address.port, '-S', 'cli=y,tcp=n,udp=n,allow-ip-name-lookup=n',
      '--max-instance-reuse-count', String(plan.reuseCount), '--idle-instance-timeout', plan.idleInstanceTimeout,
      '--dir', root + '::/probe', a.component.path];
    host = spawn(plan.wasmtime.path, args, {cwd: output, stdio: ['ignore', stdout.fd, stderr.fd],
      env: {...process.env, XDG_CACHE_HOME: join(output, 'xdg-cache'), XDG_CONFIG_HOME: join(output, 'xdg-config'), XDG_DATA_HOME: join(output, 'xdg-data')}});
    hostDone = new Promise(resolve => {
      host.once('error', error => { hostExit = {code: null, signal: null, error: errorData(error)}; resolve(); });
      host.once('exit', (code, signal) => { hostExit = {code, signal, error: null}; if (!stopping) result.errors.push({stage: 'host-exited-before-owned-shutdown', exit: hostExit}); resolve(); });
    });
    result.server = {command: [plan.wasmtime.path, ...args], pid: host.pid ?? null, forcedCleanup: false}; await save();
    const deadline = Date.now() + plan.listenerSeconds * 1000; let ready = false;
    while (Date.now() < deadline) {
      assert.equal(hostExit, null); let logs = '';
      for (const name of ['wasmtime.stdout.log', 'wasmtime.stderr.log']) { const path = join(output, name); assert((await lstat(path)).size <= 8388608); logs += await readFile(path, 'utf8'); }
      const found = /Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(logs)?.[1];
      if (found) { assert.equal(found, origin); ready = true; break; }
      await pause(50);
    }
    assert(ready, 'Exact leased listener not observed within original30s');
    const response = {method: 'GET', url: origin + '/probe', status: null, headers: null, body: null, complete: false,
      receivedBytes: 0, overflow: false, transportError: null, readerCleanupErrors: []}; result.response = response;
    const chunks = []; let kept = 0;
    try {
      const http = await fetch(response.url, {method: 'GET', redirect: 'error', signal: AbortSignal.timeout(plan.requestSeconds * 1000)});
      response.status = http.status; response.headers = Object.fromEntries(http.headers);
      const reader = http.body.getReader();
      try {
        for (;;) {
          const part = await reader.read(); if (part.done) { response.complete = true; break; }
          response.receivedBytes += part.value.byteLength;
          const remaining = plan.responseByteCap - kept;
          if (remaining > 0) { const copy = part.value.slice(0, remaining); chunks.push(copy); kept += copy.byteLength; }
          if (response.receivedBytes > plan.responseByteCap) { response.overflow = true; throw new Error('Probe response byte cap exceeded; explicit prefix retained'); }
        }
      } catch (error) { response.transportError = errorData(error); throw error; }
      finally {
        if (!response.complete) try { await reader.cancel(); }
        catch (error) { response.readerCleanupErrors.push({operation: 'cancel', ...errorData(error)}); }
        try { reader.releaseLock(); }
        catch (error) { response.readerCleanupErrors.push({operation: 'releaseLock', ...errorData(error)}); }
      }
    } catch (error) { response.transportError ??= errorData(error); }
    if (response.complete || kept > 0) {
      const bytes = Buffer.concat(chunks); const path = join(output, 'response.body'); await durable(path, bytes, true);
      response.body = await row(path); response.retainedPrefixBytes = bytes.length;
    }
    await save(); // Raw bytes/partial failure are durable before semantic parsing.
    assert.equal(response.transportError, null); assert.deepEqual(response.readerCleanupErrors, []);
    assert.equal(response.overflow, false); assert.equal(response.complete, true);
    assert.equal(response.status, 200); assert.equal(response.headers['content-type']?.split(';', 1)[0].trim().toLowerCase(), 'application/json');
    const payload = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(await readFile(response.body.path)));
    const {validateInteropResponse} = await import('./comparison.mjs');
    assert.deepEqual(payload.records.map(record => record.id), plan.expectedCaseIds);
    result.validation = validateInteropResponse(payload); result.interopProfileMatched = result.validation.interopProfileMatched;
    result.response.payload = payload; await save();
  } catch (error) { result.errors.push({stage: 'fixture-host-probe-or-validation', ...errorData(error)}); }
  finally {
    try { if (lease?.listening) await new Promise(resolve => lease.close(() => resolve())); }
    catch (error) { result.errors.push({stage: 'lease-close', ...errorData(error)}); }
    try {
      if (host && !hostExit) {
        stopping = true; result.server.shutdownRequested = true; result.server.sigintSent = host.kill('SIGINT');
        await waitBounded(hostDone, plan.shutdownSeconds * 1000);
        if (!hostExit) { result.server.forcedCleanup = true; host.kill('SIGKILL'); await waitBounded(hostDone, plan.shutdownSeconds * 1000); }
      }
      if (result.server) result.server.exit = hostExit;
    } catch (error) { result.errors.push({stage: 'owned-host-shutdown', ...errorData(error)}); }
    for (const handle of handles) try { await handle.sync(); await handle.close(); }
    catch (error) { result.errors.push({stage: 'host-log-close', ...errorData(error)}); }
    if (result.server) for (const name of ['wasmtime.stdout.log', 'wasmtime.stderr.log'])
      try { result.server[name] = await row(join(output, name)); } catch (error) { result.errors.push({stage: 'host-log-final-descriptor', ...errorData(error)}); }
    try { if (result.fixtures) { assert.deepEqual(await fixtureRecords(), result.fixtures); result.fixtureCopyPreserved = true; } }
    catch (error) { result.errors.push({stage: 'fixture-final-protection', ...errorData(error)}); }
    try { await protect(); result.inputsPreserved = true; }
    catch (error) { result.errors.push({stage: 'final-source-artifact-protection', ...errorData(error)}); }
    result.observationsValid = result.errors.length === 0 && result.inputsPreserved === true && result.fixtureCopyPreserved === true &&
      result.server?.shutdownRequested === true && result.server?.sigintSent === true && result.server?.forcedCleanup === false &&
      hostExit?.code === 0 && hostExit?.signal === null && hostExit?.error === null;
    result.state = result.observationsValid && result.interopProfileMatched ? 'INTEROP_SELECTED_DEFAULT_NAMESPACE_PROFILE_OBSERVED_V1' : 'INTEROP_PROBE_FAILED_RAW_PRESERVED_V1';
    await save();
  }
  console.log(JSON.stringify({state: result.state, observationsValid: result.observationsValid,
    interopProfileMatched: result.interopProfileMatched, errors: result.errors, nodeCompatibilityAccepted: false}));
  process.exitCode = result.observationsValid && result.interopProfileMatched ? 0 : 1;
}
main().catch(error => { console.error(error); process.exitCode = 1; });
