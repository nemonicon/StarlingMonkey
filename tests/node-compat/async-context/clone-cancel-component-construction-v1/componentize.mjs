// Host tool caller. The selected guest only installs inert definitions during INIT.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, readdir, lstat, readlink, realpath, mkdir } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const hash = data => createHash('sha256').update(data).digest('hex');
async function checked(ref) {
  assert.equal(await realpath(ref.path), ref.path, 'Canonical selected input');
  const before = await lstat(ref.path);
  assert(before.isFile() && !before.isSymbolicLink());
  const data = await readFile(ref.path), after = await lstat(ref.path);
  assert.equal(data.length, ref.bytes); assert.equal(hash(data), ref.sha256);
  assert.equal(before.size, after.size); assert.equal(before.mtimeMs, after.mtimeMs);
  return data;
}
async function inventory(root) {
  const files = [], links = [];
  async function visit(directory) {
    for (const name of await readdir(directory)) {
      const path = join(directory, name), stat = await lstat(path);
      if (stat.isSymbolicLink()) links.push(relative(root, path));
      else if (stat.isDirectory()) await visit(path);
      else { assert(stat.isFile()); files.push(relative(root, path)); }
    }
  }
  await visit(root);
  return { files: files.sort(), links: links.sort() };
}

async function main() {
  assert.equal(process.version, 'v22.14.0');
  assert.deepEqual(process.execArgv, []);
  assert.equal(process.env.NODE_OPTIONS, undefined); assert.equal(process.env.NODE_PATH, undefined);
  assert.equal(process.cwd(), here); assert.equal(process.argv.length, 4);
  const [requestPath, requestSHA] = process.argv.slice(2);
  const requestBytes = await readFile(requestPath); assert.equal(hash(requestBytes), requestSHA);
  const request = JSON.parse(requestBytes);
  assert.equal(request.state, 'ROOT_CLONE_CANCEL_ENGINE_CONSTRUCTION_V1');
  assert.equal(request.ordinaryExportsAllowed, false);
  const selection = JSON.parse(await checked(request.compilerSelection));
  assert.equal(selection.state, 'FRESH_COMPILER_PACKAGE_SELECTED_V1');
  const pkg = selection.package;
  const metadataBytes = await checked(request.nativeMetadata);
  const metadata = JSON.parse(metadataBytes);
  assert.deepEqual(Object.keys(metadata).sort(), request.metadataKeys);
  const admission = JSON.parse(await checked(request.engineAdmission));
  assert.equal(admission.state, 'CLONE_CANCEL_ACTUAL_ENGINE_ADMISSION_PASSED_V1');
  assert.equal(admission.passed, true);
  assert.deepEqual(admission.engine, request.engine);
  assert.deepEqual(admission.nativeMetadata, request.nativeMetadata);
  assert.deepEqual(admission.metadataKeys, request.metadataKeys);
  assert.deepEqual(metadata.engine, request.engine);
  assert.equal(admission.completeActualMetadataReviewed, true);
  assert.equal(admission.oldMetadataProjected, false);
  assert.equal(admission.nativeBuildPassed, true);
  assert.equal(admission.guestExecuted, false);
  async function protect() {
    assert.equal(hash(await readFile(requestPath)), requestSHA);
    await checked(request.compilerSelection);
    await checked(request.engineAdmission);
    for (const ref of request.inputs) await checked(ref);
    const found = await inventory(pkg.root);
    assert.deepEqual(found.files, pkg.files.map(row => row.relativePath).sort());
    assert.deepEqual(found.links, pkg.links.map(row => row.path).sort());
    for (const ref of pkg.files) {
      await checked(ref);
      assert.equal((await lstat(ref.path)).mode & 0o777, ref.mode);
    }
    for (const ref of pkg.links) {
      const path = join(pkg.root, ref.path);
      assert.equal(await readlink(path), ref.target); assert.equal(await realpath(path), ref.resolvedPath);
    }
    assert((await checked(request.nativeMetadata)).equals(metadataBytes));
  }
  await protect();
  await checked(request.capture);
  const { writeWhole, captureComponentReturn, typedOwnGraph } = await import(pathToFileURL(request.capture.path).href);
  await mkdir(request.output, { mode: 0o700 });
  let primarySet = false, primary, filesystem;
  const secondary = [];
  try {
    filesystem = await import(pathToFileURL(join(pkg.root, 'node_modules/@bytecodealliance/preview2-shim/dist/nodejs/filesystem.js')).href);
    assert.deepEqual(filesystem._getPreopens().map(([, name]) => name), []);
    filesystem._setPreopens({ [request.witDirectory]: request.witDirectory });
    const options = { engine: request.engine.path, preview2Adapter: request.adapter.path,
      witPath: request.witDirectory, worldName: 'next-http',
      disableFeatures: ['fetch-event'], enableFeatures: [], enableAot: false, env: {},
      debug: { bindings: false, binary: false, wizerLogging: false },
      debugBindings: false, debugBuild: false, enableWizerLogging: false };
    await writeWhole(join(request.output, 'options.json'), JSON.stringify(options, null, 2) + '\n');
    const { componentize } = await import(pathToFileURL(join(pkg.root, 'src/componentize.js')).href);
    const returned = await componentize((await checked(request.entry)).toString('utf8'), options);
    const artifacts = await captureComponentReturn(returned, request.output);
    await writeWhole(join(request.output, 'result.json'), JSON.stringify({ schemaVersion: 1,
      state: 'CLONE_CANCEL_LIFECYCLE_COMPONENT_CAPTURED_UNREVIEWED_V1', artifacts,
      engine: request.engine, nativeMetadata: request.nativeMetadata, engineAdmission: request.engineAdmission,
      compilerSelection: request.compilerSelection, inputEntry: request.entry,
      ordinaryExportInvoked: false }, null, 2) + '\n');
    console.log(JSON.stringify({ artifacts }));
  } catch (error) {
    primarySet = true; primary = error;
    try { await writeWhole(join(request.output, 'failure.json'), JSON.stringify(typedOwnGraph(error), null, 2) + '\n'); }
    catch (captureError) { secondary.push({ stage: 'failure-capture', error: typedOwnGraph(captureError) }); }
  } finally {
    try {
      if (filesystem) {
        const names = filesystem._getPreopens().map(([, name]) => name);
        await writeWhole(join(request.output, 'final-preopens.json'), JSON.stringify(names) + '\n');
        assert.deepEqual(names, [request.witDirectory]);
      }
      await protect();
    } catch (error) {
      if (!primarySet) { primarySet = true; primary = error; }
      else secondary.push({ stage: 'final-protection', error: typedOwnGraph(error) });
    }
  }
  if (secondary.length) console.error(JSON.stringify({ secondary }));
  if (primarySet) throw primary;
}

main().catch(error => { console.error(error); process.exitCode = 1; });
