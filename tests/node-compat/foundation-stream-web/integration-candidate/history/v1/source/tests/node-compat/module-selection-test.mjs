// Build-time admission tests. Synthetic receipts exercise rejection paths;
// these do not claim that a synthetic receipt is an executed engine build.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from './toolchain.mjs';
import { builtinMap, CORE_MANIFEST, PATH_MANIFEST, EVENTS_MANIFEST,
  STRING_DECODER_MANIFEST, ASSERT_MANIFEST, QUERYSTRING_MANIFEST, UTIL_MANIFEST, STREAM_WEB_MANIFEST,
  selectedManifestsForEngine } from './module-selection.mjs';
import { bundleProfile, createProfilePlugin } from './profile-bundler.mjs';

const repository = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const sources = await Promise.all([CORE_MANIFEST, PATH_MANIFEST].map(async path => {
  const bytes = await readFile(join(repository, path));
  return { path, bytes, sha256: hash(bytes), manifest: JSON.parse(bytes) };
}));
const [core, path] = sources.map(source => source.manifest);
const manifests = [core, path];
const eventsBytes = await readFile(join(repository, EVENTS_MANIFEST));
const events = JSON.parse(eventsBytes);
const eventsSource = { path: EVENTS_MANIFEST, bytes: eventsBytes, sha256: hash(eventsBytes), manifest: events };
const foundations = await Promise.all([
  ['StringDecoder', 'stringDecoderEnabled', 'NODE_COMPAT_STRING_DECODER', STRING_DECODER_MANIFEST],
  ['Assert', 'assertEnabled', 'NODE_COMPAT_ASSERT', ASSERT_MANIFEST],
  ['Querystring', 'querystringEnabled', 'NODE_COMPAT_QUERYSTRING', QUERYSTRING_MANIFEST],
  ['Util', 'utilEnabled', 'NODE_COMPAT_UTIL', UTIL_MANIFEST],
  ['StreamWeb', 'streamWebEnabled', 'NODE_COMPAT_STREAM_WEB', STREAM_WEB_MANIFEST],
].map(async ([name, field, option, path]) => {
  const bytes = await readFile(join(repository, path));
  return { name, field, option, path, bytes, sha256: hash(bytes), manifest: JSON.parse(bytes) };
}));
function foundationReceipt(enabledNames = [], { pathEnabled = false, eventsEnabled = false } = {}) {
  const metadata = eventsReceipt(pathEnabled, eventsEnabled);
  for (const source of foundations) {
    const enabled = enabledNames.includes(source.name);
    metadata[source.field] = enabled;
    metadata.observedCMakeOptions[source.option] = enabled ? 'ON' : 'OFF';
    metadata.sourceManifest.push({ path: source.path, sha256: source.sha256 });
    if (enabled) metadata.selectedModuleManifests.push({ path: source.path,
      sha256: source.sha256, profileVersion: source.manifest.profileVersion });
  }
  return metadata;
}
const tools = await loadToolchain();
const temporary = await mkdtemp(join(tmpdir(), 'starling-native-admission-'));
const results = [];
async function test(name, operation) {
  try { await operation(); results.push({ name, passed: true }); }
  catch (error) { results.push({ name, passed: false, error: error.message }); }
}
function receipt(pathEnabled) {
  return {
    profileEnabled: true, pathEnabled, streamWebEnabled: false,
    observedCMakeOptions: { NODE_COMPAT_PATH: pathEnabled ? 'ON' : 'OFF', NODE_COMPAT_STREAM_WEB: 'OFF' },
    selectedModuleManifests: sources.slice(0, pathEnabled ? 2 : 1).map(({ path, sha256, manifest }) =>
      ({ path, sha256, profileVersion: manifest.profileVersion })),
    sourceManifest: sources.map(({ path, sha256 }) => ({ path, sha256 })),
  };
}
function eventsReceipt(pathEnabled, eventsEnabled) {
  const metadata = receipt(pathEnabled);
  metadata.eventsEnabled = eventsEnabled;
  metadata.observedCMakeOptions.NODE_COMPAT_EVENTS = eventsEnabled ? 'ON' : 'OFF';
  metadata.sourceManifest.push({ path: eventsSource.path, sha256: eventsSource.sha256 });
  if (eventsEnabled) metadata.selectedModuleManifests.push({ path: eventsSource.path,
    sha256: eventsSource.sha256, profileVersion: events.profileVersion });
  return metadata;
}
function plugin(options = {}) { return createProfilePlugin(tools.parseAst, options); }
async function bundle(input, builtinManifests) {
  return bundleProfile({ ...tools, input, builtinManifests });
}
const canonicalPath = ['node:path', 'node:path/posix', 'node:path/win32'];
try {
  await test('finite frozen core map', () => {
    const map = builtinMap([core]);
    assert.equal(Object.getPrototypeOf(map), null); assert(Object.isFrozen(map));
    assert.deepEqual(Object.keys(map).sort(), ['buffer', 'child_process', 'node:buffer', 'node:child_process']);
    assert.equal(map.buffer, 'node:buffer'); assert.equal(map.then, undefined);
  });
  await test('optional Path map has six additional identifiers', () => {
    const map = builtinMap(manifests);
    assert.equal(Object.keys(map).length, 10);
    for (const id of canonicalPath) { assert.equal(map[id], id); assert.equal(map[id.slice(5)], id); }
  });
  await test('core receipt selects only core bindings', () => {
    const selected = selectedManifestsForEngine(receipt(false));
    assert.equal(selected.length, 1); assert.equal(builtinMap(selected)['node:path'], undefined);
  });
  await test('Path receipt selects both manifests', () => {
    const selected = selectedManifestsForEngine(receipt(true));
    assert.equal(selected.length, 2); assert.equal(builtinMap(selected)['path/win32'], 'node:path/win32');
  });
  await test('historical core-only receipt remains bounded', () => {
    const metadata = receipt(false);
    delete metadata.pathEnabled; metadata.observedCMakeOptions = { NODE_COMPAT_STREAM_WEB: 'OFF' }; delete metadata.selectedModuleManifests;
    assert.equal(selectedManifestsForEngine(metadata).length, 1);
  });
  for (const pathEnabled of [false, true]) {
    await test(`flag mismatch rejects Path=${pathEnabled}`, () => {
      const metadata = receipt(pathEnabled);
      metadata.observedCMakeOptions.NODE_COMPAT_PATH = pathEnabled ? 'OFF' : 'ON';
      assert.throws(() => selectedManifestsForEngine(metadata), /CMake|Path selection/);
    });
    await test(`explicit Path=${pathEnabled} requires observed flag`, () => {
      const metadata = receipt(pathEnabled); delete metadata.observedCMakeOptions.NODE_COMPAT_PATH;
      assert.throws(() => selectedManifestsForEngine(metadata), /CMake|Path selection/);
    });
  }
  await test('nonboolean optional feature receipt rejects', () => {
    const metadata = receipt(false); metadata.pathEnabled = 'ON';
    assert.throws(() => selectedManifestsForEngine(metadata), /boolean|pathEnabled/);
  });
  await test('disabled profile rejects admission', () => {
    const metadata = receipt(true); metadata.profileEnabled = false;
    assert.throws(() => selectedManifestsForEngine(metadata));
  });
  await test('Path ON requires explicit manifest selection', () => {
    const metadata = receipt(true); delete metadata.selectedModuleManifests;
    assert.throws(() => selectedManifestsForEngine(metadata), /explicit selectedModuleManifests/);
  });
  for (const [name, mutate] of [
    ['omitted optional manifest', metadata => metadata.selectedModuleManifests.pop()],
    ['duplicate selected manifest', metadata => metadata.selectedModuleManifests.push(metadata.selectedModuleManifests[0])],
    ['unknown selected manifest', metadata => metadata.selectedModuleManifests[1].path = 'builtin-override.json'],
  ]) {
    await test(name + ' rejects', () => {
      const metadata = receipt(true); mutate(metadata);
      assert.throws(() => selectedManifestsForEngine(metadata), /Unselected or omitted/);
    });
  }
  await test('OFF receipt cannot admit existing Path manifest', () => {
    const metadata = receipt(false); metadata.selectedModuleManifests.push(receipt(true).selectedModuleManifests[1]);
    assert.throws(() => selectedManifestsForEngine(metadata), /Unselected or omitted/);
  });
  await test('selected manifest must be in compiled source inventory', () => {
    const metadata = receipt(true); metadata.sourceManifest.pop();
    assert.throws(() => selectedManifestsForEngine(metadata), /input receipt omits/);
  });
  await test('compiled source inventory is required', () => {
    const metadata = receipt(true); delete metadata.sourceManifest;
    assert.throws(() => selectedManifestsForEngine(metadata), /compiled inputs/);
  });
  await test('manifest receipt hash must agree with compiled inputs', () => {
    const metadata = receipt(true); metadata.selectedModuleManifests[1].sha256 = '0'.repeat(64);
    assert.throws(() => selectedManifestsForEngine(metadata), /receipt conflicts/);
  });
  await test('actual manifest bytes must match engine receipt', async () => {
    const root = join(temporary, 'altered-sources');
    for (const source of sources) {
      const destination = join(root, source.path); await mkdir(dirname(destination), { recursive: true });
      await writeFile(destination, source.bytes);
    }
    await writeFile(join(root, PATH_MANIFEST), sources[1].bytes + '\n');
    assert.throws(() => selectedManifestsForEngine(receipt(true), { sourceRoot: root }), /differs from built engine/);
  });
  await test('receipt profile version must match selected manifest', () => {
    const metadata = receipt(true); metadata.selectedModuleManifests[1].profileVersion = 'sm-node-22.14.0-m0.99';
    assert.throws(() => selectedManifestsForEngine(metadata));
  });
  await test('duplicate canonical selections reject', () => {
    assert.throws(() => builtinMap([core, core]), /Duplicate native module selection/);
  });
  await test('aliases collide across selected manifests', () => {
    const other = structuredClone(path);
    other.modules = { 'node:fs': { ...structuredClone(path.modules['node:path']), aliases: ['buffer'] } };
    assert.throws(() => builtinMap([core, other]), /alias collision/);
  });
  await test('unknown Node release module rejects', () => {
    const other = structuredClone(path);
    other.modules = { 'node:sm_admission_invented': { ...structuredClone(path.modules['node:path']), aliases: [] } };
    assert.throws(() => builtinMap([other]), /Unknown Node release module/);
  });
  await test('manifest cannot create thenable namespace', () => {
    const other = structuredClone(path); other.modules['node:path'].exports.push('then');
    assert.throws(() => builtinMap([other]), /then export/);
  });
  for (const id of ['node:path', 'path', 'node:path/posix', 'path/win32', 'node:buffer', 'fs']) {
    await test(`virtual declaration cannot replace ${id}`, () => {
      assert.throws(() => plugin({ builtinManifests: manifests, virtualModules: { [id]: 'export default 1;' } }),
        /cannot replace a native builtin/);
    });
  }
  for (const id of ['jco:node/path', 'wasmcloud:compat/path']) {
    await test(`virtual declaration cannot bypass reserved adapter ${id}`, () => {
      assert.throws(() => plugin({ virtualModules: { [id]: 'export default 1;' } }), /Nonstandard|reserved|adapter/);
    });
  }
  await test('private virtual load ignores inherited code', () => {
    const virtualModules = Object.create({ 'node:path': 'export default "shadow";',
      'node-compat:inherited': 'export default "inherited";' });
    const admitted = plugin({ virtualModules });
    for (const id of ['node:path', 'node-compat:inherited', 'toString', '__proto__']) {
      assert.equal(admitted.load('\0' + id) ?? null, null, `Inherited private source: ${id}`);
    }
    assert.equal(admitted.resolveId('node-compat:inherited'), null);
    assert.throws(() => admitted.resolveId('node:path'), /not admitted/);
  });
  await test('owned private virtual source remains usable', () => {
    const admitted = plugin({ virtualModules: { 'node-compat:own': 'export default 17;' } });
    assert.equal(admitted.resolveId('node-compat:own'), '\0node-compat:own');
    assert.equal(admitted.load('\0node-compat:own'), 'export default 17;');
  });
  await test('invalid private virtual declarations reject', () => {
    assert.throws(() => plugin({ virtualModules: { '\0node:path': 'export default 1;' } }));
    assert.throws(() => plugin({ virtualModules: { 'node-compat:not-source': {} } }));
  });
  const esm = join(temporary, 'application.mjs');
  const commonjs = join(temporary, 'application.cjs');
  await writeFile(esm, "import root from 'path'; import posix from 'node:path/posix'; import win32 from 'path/win32'; export const value = [root,posix,win32];\n");
  await writeFile(commonjs, "const root = require('path'); const posix = require('path/posix'); const win32 = require('node:path/win32'); module.exports={root,posix,win32};\n");
  for (const [kind, input] of [['ESM aliases', esm], ['literal CommonJS aliases', commonjs]]) {
    await test(kind + ' select registered canonical modules', async () => {
      const result = await bundle(input, manifests);
      assert.deepEqual(result.imports.sort(), canonicalPath);
      assert.deepEqual(result.admittedBuiltins, ['node:buffer', 'node:child_process', ...canonicalPath]);
      assert(result.moduleIds.every(id => !/node_modules|node-builtins|path-matcher/.test(id)));
      const namespace = await import('data:text/javascript;base64,' + Buffer.from(result.code).toString('base64'));
      const actual = kind === 'ESM aliases' ? namespace.value : Object.values(namespace.default);
      const expected = await Promise.all(canonicalPath.map(id => import(id).then(module => module.default)));
      assert.deepEqual(actual, expected, 'Explicit CommonJS default mapping or ESM alias resolution changed');
    });
    await test(kind + ' reject when Path feature is OFF', async () => {
      await assert.rejects(() => bundle(input, [core]), /not admitted/);
    });
  }
  await test('Path OFF rejects before the actual Jco adapter can resolve', async () => {
    const adapterPath = join(dirname(tools.require.resolve('@bytecodealliance/jco')), 'node-builtins/path.js');
    const { createPathBuiltin } = await import(pathToFileURL(adapterPath));
    const adapter = createPathBuiltin({ options: {}, worldMetadata: { imports: [
      { namespace: 'wasi', package: 'cli', interface: 'environment', version: { major: 0n, minor: 2n, patch: 10n } },
    ] } });
    let attempts = 0;
    const fallback = { name: 'actual-jco-adapter-must-not-run', resolveId(id) {
      if (id === 'path' || id === 'node:path') attempts++;
      return adapter.resolveId(id);
    }, load(id) { return adapter.load(id); } };
    for (const id of ['path', 'node:path']) {
      const input = join(temporary, 'adapter-present.mjs');
      await writeFile(input, `import path from ${JSON.stringify(id)}; export const result=path.sep;\n`);
      await assert.rejects(async () => {
        const build = await tools.rolldown({ input, platform: 'neutral', plugins: [plugin(), fallback] });
        try { await build.generate({ format: 'esm' }); } finally { await build.close(); }
      }, /not admitted/);
    }
    assert.equal(attempts, 0, 'A denied builtin reached a later JavaScript adapter');
  });
  await test('optional Events map adds only two identifiers', () => {
    const map = builtinMap([core, events]);
    assert.equal(Object.keys(map).length, 6); assert.equal(map.events, 'node:events');
    assert.equal(map['node:events'], 'node:events'); assert.equal(map['node:path'], undefined);
  });
  for (const pathEnabled of [false, true]) for (const eventsEnabled of [false, true]) {
    await test(`independent optional selection Path=${pathEnabled},Events=${eventsEnabled}`, () => {
      const selected = selectedManifestsForEngine(eventsReceipt(pathEnabled, eventsEnabled));
      const map = builtinMap(selected);
      assert.equal(selected.length, 1 + Number(pathEnabled) + Number(eventsEnabled));
      assert.equal(map['node:events'], eventsEnabled ? 'node:events' : undefined);
      assert.equal(map['node:path'], pathEnabled ? 'node:path' : undefined);
    });
  }
  for (const eventsEnabled of [false, true]) {
    await test(`Events flag mismatch rejects ${eventsEnabled}`, () => {
      const metadata = eventsReceipt(false, eventsEnabled);
      metadata.observedCMakeOptions.NODE_COMPAT_EVENTS = eventsEnabled ? 'OFF' : 'ON';
      assert.throws(() => selectedManifestsForEngine(metadata), /CMake/);
    });
    await test(`explicit Events=${eventsEnabled} requires observed flag`, () => {
      const metadata = eventsReceipt(false, eventsEnabled); delete metadata.observedCMakeOptions.NODE_COMPAT_EVENTS;
      assert.throws(() => selectedManifestsForEngine(metadata), /CMake/);
    });
  }
  await test('nonboolean Events feature receipt rejects', () => {
    const metadata = eventsReceipt(false, false); metadata.eventsEnabled = 'ON';
    assert.throws(() => selectedManifestsForEngine(metadata), /boolean|eventsEnabled/);
  });
  await test('Events ON requires explicit optional manifest', () => {
    const metadata = eventsReceipt(false, true); delete metadata.selectedModuleManifests;
    assert.throws(() => selectedManifestsForEngine(metadata), /explicit selectedModuleManifests/);
  });
  await test('omitted Events manifest rejects', () => {
    const metadata = eventsReceipt(true, true); metadata.selectedModuleManifests.pop();
    assert.throws(() => selectedManifestsForEngine(metadata), /Unselected or omitted/);
  });
  await test('Events OFF cannot admit an existing Events manifest', () => {
    const metadata = eventsReceipt(true, false);
    metadata.selectedModuleManifests.push(eventsReceipt(false, true).selectedModuleManifests[1]);
    assert.throws(() => selectedManifestsForEngine(metadata), /Unselected or omitted/);
  });
  await test('Events manifest receipt hash mismatch rejects', () => {
    const metadata = eventsReceipt(true, true); metadata.selectedModuleManifests[2].sha256 = '0'.repeat(64);
    assert.throws(() => selectedManifestsForEngine(metadata), /receipt conflicts/);
  });
  await test('Events manifest must appear in compiled inputs', () => {
    const metadata = eventsReceipt(true, true); metadata.sourceManifest.pop();
    assert.throws(() => selectedManifestsForEngine(metadata), /input receipt omits/);
  });
  await test('Events actual manifest bytes must match receipt', async () => {
    const root = join(temporary, 'altered-events');
    for (const source of [...sources, eventsSource]) {
      const destination = join(root, source.path); await mkdir(dirname(destination), { recursive: true });
      await writeFile(destination, source.bytes);
    }
    await writeFile(join(root, EVENTS_MANIFEST), eventsBytes + '\n');
    assert.throws(() => selectedManifestsForEngine(eventsReceipt(true, true), { sourceRoot: root }), /differs from built engine/);
  });
  await test('Events profile version must match receipt', () => {
    const metadata = eventsReceipt(false, true); metadata.selectedModuleManifests[1].profileVersion = 'sm-node-22.14.0-m0.99';
    assert.throws(() => selectedManifestsForEngine(metadata));
  });
  await test('Events duplicate canonical selection rejects', () => {
    assert.throws(() => builtinMap([core, events, events]), /Duplicate native module selection/);
  });
  await test('Events alias collision rejects', () => {
    const other = structuredClone(events);
    other.modules = { 'node:fs': { ...structuredClone(events.modules['node:events']), aliases: ['events'] } };
    assert.throws(() => builtinMap([core, events, other]), /alias collision/);
  });
  await test('invented Events canonical module rejects', () => {
    const other = structuredClone(events);
    other.modules = { 'node:sm_events_admission_invented': { ...structuredClone(events.modules['node:events']), aliases: [] } };
    assert.throws(() => builtinMap([other]), /Unknown Node release module/);
  });
  for (const id of ['events', 'node:events']) {
    await test('virtual declaration cannot shadow ' + id, () => {
      assert.throws(() => plugin({ builtinManifests: [core, events], virtualModules: { [id]: 'export default {};' } }),
        /cannot replace a native builtin/);
    });
  }
  const eventsEsm = join(temporary, 'events.mjs'), eventsCjs = join(temporary, 'events.cjs');
  await writeFile(eventsEsm, "import EventEmitter,* as events from 'events'; import canonical from 'node:events'; export const value={EventEmitter,events,canonical};\n");
  await writeFile(eventsCjs, "const events=require('events'); const canonical=require('node:events'); module.exports={events,canonical};\n");
  for (const [kind, input] of [['ESM Events', eventsEsm], ['literal CommonJS Events', eventsCjs]]) {
    await test(kind + ' selects native constructor default and aliases', async () => {
      const result = await bundle(input, [core, events]);
      assert.deepEqual(result.imports, ['node:events']);
      assert.deepEqual(result.admittedBuiltins, ['node:buffer', 'node:child_process', 'node:events']);
      assert(result.moduleIds.every(id => !/node_modules|node-builtins/.test(id)));
      const actual = await import('data:text/javascript;base64,' + Buffer.from(result.code).toString('base64'));
      const expected = (await import('node:events')).default;
      if (kind === 'ESM Events') {
        assert.equal(actual.value.EventEmitter, expected); assert.equal(actual.value.canonical, expected);
        assert.equal(actual.value.events.default, expected); assert.equal(actual.value.events.EventEmitter, expected);
      } else { assert.equal(actual.default.events, expected); assert.equal(actual.default.canonical, expected); }
    });
    await test(kind + ' rejects when Events is OFF despite Path selection', async () => {
      await assert.rejects(() => bundle(input, manifests), /not admitted/);
    });
  }
  await test('known immutable legacy stream feature absence stays OFF', async () => {
    const legacy = JSON.parse(await readFile(new URL('./legacy-stream-web-test-receipt.json', import.meta.url)));
    const selected = selectedManifestsForEngine(legacy);
    assert.equal(builtinMap(selected)['node:stream/web'], undefined);
    const reordered = structuredClone(legacy); reordered.sourceManifest.reverse();
    assert.equal(builtinMap(selectedManifestsForEngine(reordered))['node:stream/web'], undefined, 'Canonical inventory digest ignores entry order');
  });
  for (const [name, mutate] of [
    ['source-list spoof', value => value.sourceManifest[0].sha256 = '0'.repeat(64)],
    ['recipe spoof', value => value.buildRecipeSha256 = '0'.repeat(64)],
    ['engine spoof', value => value.engineSha256 = '0'.repeat(64)],
    ['observed-only flag', value => value.observedCMakeOptions.NODE_COMPAT_STREAM_WEB = 'OFF'],
  ]) await test('legacy stream absence rejects ' + name, async () => {
    const legacy = JSON.parse(await readFile(new URL('./legacy-stream-web-test-receipt.json', import.meta.url))); mutate(legacy);
    assert.throws(() => selectedManifestsForEngine(legacy), /legacy|streamWebEnabled/);
  });
  await test('unknown synthetic receipt must explicitly declare new stream flag', () => {
    const metadata = receipt(false); delete metadata.streamWebEnabled; delete metadata.observedCMakeOptions.NODE_COMPAT_STREAM_WEB;
    assert.throws(() => selectedManifestsForEngine(metadata), /legacy|streamWebEnabled/);
  });
  await test('owned undefined stream flag is not historical absence', () => {
    const metadata = receipt(false); metadata.streamWebEnabled = undefined;
    assert.throws(() => selectedManifestsForEngine(metadata), /boolean/);
  });
  // Exhaustive independent feature selection, including each foundation with
  // Path/Events both enabled and disabled. Receipts here are synthetic.
  const pathBit = 1 << foundations.length, eventsBit = pathBit << 1;
  for (let bits = 0; bits < eventsBit * 2; bits++) {
    await test(`${foundations.length + 2} independent optional selections ${bits}`, () => {
      const enabled = foundations.filter((_, index) => bits & (1 << index)).map(source => source.name);
      const metadata = foundationReceipt(enabled, { pathEnabled: !!(bits & pathBit), eventsEnabled: !!(bits & eventsBit) });
      const selected = selectedManifestsForEngine(metadata);
      const map = builtinMap(selected);
      assert.equal(selected.length, 1 + enabled.length + Number(!!(bits & pathBit)) + Number(!!(bits & eventsBit)));
      for (const source of foundations) for (const [id, module] of Object.entries(source.manifest.modules)) {
        for (const alias of [id, ...module.aliases]) assert.equal(map[alias], enabled.includes(source.name) ? id : undefined);
      }
    });
  }
  for (const source of foundations) {
    const only = () => foundationReceipt([source.name]);
    for (const enabled of [false, true]) {
      await test(`${source.name} flag mismatch rejects ${enabled}`, () => {
        const metadata = foundationReceipt(enabled ? [source.name] : []);
        metadata.observedCMakeOptions[source.option] = enabled ? 'OFF' : 'ON';
        assert.throws(() => selectedManifestsForEngine(metadata), /CMake/);
      });
    }
    for (const [label, mutate, pattern] of [
      ['missing observed flag', metadata => delete metadata.observedCMakeOptions[source.option], /CMake/],
      ['nonboolean flag', metadata => metadata[source.field] = 'ON', /boolean/],
      ['missing manifest', metadata => metadata.selectedModuleManifests.pop(), /Unselected or omitted/],
      ['missing compiled input', metadata => metadata.sourceManifest = metadata.sourceManifest.filter(entry => entry.path !== source.path), /input receipt omits/],
      ['mismatched hash', metadata => metadata.selectedModuleManifests.at(-1).sha256 = '0'.repeat(64), /receipt conflicts/],
      ['mismatched profile version', metadata => metadata.selectedModuleManifests.at(-1).profileVersion = 'sm-node-22.14.0-m0.99', /Assertion/],
    ]) {
      await test(`${source.name} ${label} rejects`, () => {
        const metadata = only(); mutate(metadata);
        assert.throws(() => selectedManifestsForEngine(metadata), pattern);
      });
    }
    await test(`${source.name} OFF cannot admit its manifest`, () => {
      const metadata = foundationReceipt();
      metadata.selectedModuleManifests.push(only().selectedModuleManifests.at(-1));
      assert.throws(() => selectedManifestsForEngine(metadata), /Unselected or omitted/);
    });
    await test(`${source.name} duplicate module selection rejects`, () => {
      assert.throws(() => builtinMap([core, source.manifest, source.manifest]), /Duplicate native module selection/);
    });
    for (const [id, module] of Object.entries(source.manifest.modules)) {
      for (const alias of [id, ...module.aliases]) {
        await test(`${source.name} ${alias} cannot be shadowed or admitted when OFF`, () => {
          assert.throws(() => plugin({ builtinManifests: [core, source.manifest], virtualModules: { [alias]: 'export default {};' } }), /cannot replace a native builtin/);
          assert.throws(() => plugin().resolveId(alias), /not admitted/);
        });
      }
      const alias = module.aliases[0];
      for (const kind of ['esm', 'cjs']) {
        const input = join(temporary, `${source.name}-${id.replaceAll('/', '-')}.${kind === 'esm' ? 'mjs' : 'cjs'}`);
        await writeFile(input, kind === 'esm'
          ? `import primary from ${JSON.stringify(id)}; import alias from ${JSON.stringify(alias)}; export const value={primary,alias};\n`
          : `const primary=require(${JSON.stringify(id)}); const alias=require(${JSON.stringify(alias)}); module.exports={primary,alias};\n`);
        await test(`${source.name} ${id} ${kind} keeps native imports and default identity`, async () => {
          const result = await bundle(input, [core, source.manifest]);
          assert.deepEqual(result.imports, [id]);
          assert(result.moduleIds.every(moduleId => !/node_modules|node-builtins/.test(moduleId)));
          const actual = await import('data:text/javascript;base64,' + Buffer.from(result.code).toString('base64'));
          const expected = (await import(id)).default;
          const pair = kind === 'esm' ? actual.value : actual.default;
          assert.equal(pair.primary, expected); assert.equal(pair.alias, expected);
        });
        await test(`${source.name} ${id} ${kind} rejects when OFF`, async () => {
          await assert.rejects(() => bundle(input, [core]), /not admitted/);
        });
      }
    }
  }
} finally { await rm(temporary, { recursive: true, force: true }); }
const failures = results.filter(result => !result.passed);
console.log(JSON.stringify({ node: process.version, tests: results.length, passed: results.length - failures.length,
  failures, scope: 'build-time manifest, engine receipt and bundle selection; no engine execution claimed' }, null, 2));
assert.equal(failures.length, 0, 'Native module admission regressions');
