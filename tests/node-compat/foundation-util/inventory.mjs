// Public binding/descriptor inventory plus an official pinned-source ledger.
// No exported util operation is called and no process.binding/internalBinding
// inspection is performed in this inventory process.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const hash = value => createHash('sha256').update(value).digest('hex');
const require = createRequire(import.meta.url);
const nodePin = Object.freeze({ release: 'v22.14.0',
  tagObject: 'ddf66aca0766567c70bf16a92610f03ce0cd2bcd',
  revision: '5d2feb257bcee090e57900eb51720171a6aa92f3' });
assert.equal(process.version, nodePin.release);
assert.deepEqual(process.execArgv, []);
assert(!process.env.NODE_OPTIONS, 'Use the pinned default Node configuration');
const provenance = async () => ({ node: process.version, versions: process.versions,
  executable: process.execPath, executableSha256: hash(await readFile(process.execPath)),
  runnerSha256: hash(await readFile(fileURLToPath(import.meta.url))),
  execArgv: process.execArgv, nodeOptionsPresent: Boolean(process.env.NODE_OPTIONS) });

async function runtimeInventory() {
  const objectIds = new Map();
  function identity(value) {
    if (!objectIds.has(value)) objectIds.set(value, `reference-${objectIds.size + 1}`);
    return objectIds.get(value);
  }
  function symbol(value) { return { type: 'symbol', description: value.description ?? null,
    registryKey: Symbol.keyFor(value) ?? null }; }
  function key(value) { return typeof value === 'symbol' ? symbol(value) : value; }
  function flags(descriptor) { return { enumerable: descriptor.enumerable, configurable: descriptor.configurable,
    ...('writable' in descriptor ? { writable: descriptor.writable } : {}) }; }
  function functionMetadata(value) {
    const d = Object.getOwnPropertyDescriptors(value);
    return { type: 'function', identity: identity(value), name: d.name?.value ?? null,
      length: d.length?.value ?? null, ownsPrototype: Object.hasOwn(d, 'prototype') };
  }
  function describe(value, depth = 0, ancestors = new Set()) {
    if (typeof value === 'symbol') return symbol(value);
    if (value === undefined) return { type: 'undefined' };
    if (value === null) return { type: 'object', value: null };
    if (typeof value === 'number' && !Number.isFinite(value)) return { type: 'number', value: String(value) };
    if (typeof value === 'bigint') return { type: 'bigint', value: String(value) };
    if (!['function', 'object'].includes(typeof value)) return { type: typeof value, value };
    const summary = typeof value === 'function' ? functionMetadata(value)
      : { type: 'object', identity: identity(value), array: Array.isArray(value),
        nullPrototype: Object.getPrototypeOf(value) === null };
    if (ancestors.has(value)) return { ...summary, cycle: true };
    if (depth > 2) return summary;
    const next = new Set(ancestors); next.add(value);
    const intrinsicFunctionKeys = new Set(['length', 'name', 'caller', 'arguments']);
    const properties = [];
    for (const propertyKey of Reflect.ownKeys(value)) {
      if (typeof value === 'function' && intrinsicFunctionKeys.has(propertyKey)) continue;
      // Prototype descriptors are shallow; util class methods are inventoried,
      // without recursing into their inherited object graphs.
      const descriptor = Object.getOwnPropertyDescriptor(value, propertyKey);
      const row = { key: key(propertyKey), ...flags(descriptor) };
      if ('value' in descriptor) row.value = describe(descriptor.value,
        propertyKey === 'prototype' ? 2 : depth + 1, next);
      else {
        row.kind = 'accessor';
        row.get = descriptor.get ? functionMetadata(descriptor.get) : null;
        row.set = descriptor.set ? functionMetadata(descriptor.set) : null;
        row.valueNotRead = true;
      }
      properties.push(row);
    }
    return { ...summary, properties };
  }
  const ids = ['node:util', 'util', 'node:util/types', 'util/types'];
  const commonjs = Object.fromEntries(ids.map(id => [id, require(id)]));
  const before = Object.fromEntries(['node:util', 'node:util/types'].map(id => [id, describe(commonjs[id], 2)]));
  const namespaces = Object.fromEntries(await Promise.all(ids.map(async id => [id, await import(id)])));
  const modules = [];
  for (const id of ids) {
    const namespace = namespaces[id], cjs = commonjs[id];
    if (id === 'util' || id === 'util/types') {
      modules.push({ id, aliasOf: `node:${id}`, namespaceIdentity: identity(namespace),
        commonjsIdentity: identity(cjs), exports: Object.getOwnPropertyNames(namespace),
        descriptorDetailsRef: `node:${id}` });
      continue;
    }
    const publicBindings = [];
    for (const name of Object.getOwnPropertyNames(namespace)) {
      const descriptor = Object.getOwnPropertyDescriptor(namespace, name);
      const cjsDescriptor = Object.getOwnPropertyDescriptor(cjs, name);
      publicBindings.push({ name, ...flags(descriptor),
        value: describe(descriptor.value, ['default', 'types'].includes(name) ? 3 : 0),
        ...(name === 'default' ? { relationship: 'ESM default is CommonJS export object', sameAsCommonJS: descriptor.value === cjs }
          : cjsDescriptor && 'value' in cjsDescriptor
            ? { defaultPropertyKind: 'data', sameAsDefaultProperty: descriptor.value === cjsDescriptor.value }
            : { defaultPropertyKind: cjsDescriptor ? 'accessor' : 'absent',
              defaultAccessorNotInvoked: Boolean(cjsDescriptor) }) });
    }
    modules.push({ id, namespaceIdentity: identity(namespace), commonjsIdentity: identity(cjs),
      exports: Object.getOwnPropertyNames(namespace), publicBindings,
      namespaceSymbols: Object.getOwnPropertySymbols(namespace).map(propertyKey => ({ key: key(propertyKey),
        ...flags(Object.getOwnPropertyDescriptor(namespace, propertyKey)),
        value: describe(Object.getOwnPropertyDescriptor(namespace, propertyKey).value) })),
      commonjsBeforeESMImport: before[id], commonjsAfterESMImport: describe(cjs, 2) });
  }
  const util = namespaces['node:util'], types = namespaces['node:util/types'];
  const relationships = {
    utilAliasSameESMNamespace: util === namespaces.util,
    typesAliasSameESMNamespace: types === namespaces['util/types'],
    utilAliasSameCommonJSObject: commonjs['node:util'] === commonjs.util,
    typesAliasSameCommonJSObject: commonjs['node:util/types'] === commonjs['util/types'],
    utilDefaultSameCommonJSObject: util.default === commonjs['node:util'],
    typesDefaultSameCommonJSObject: types.default === commonjs['node:util/types'],
    utilTypesSameTypesDefault: util.types === types.default,
    allDataNamedBindingsSameDefaultValues: modules.filter(module => module.publicBindings).every(module => module.publicBindings
      .filter(binding => binding.defaultPropertyKind === 'data').every(binding => binding.sameAsDefaultProperty)),
    debugAndDebuglogSameBinding: util.debug === util.debuglog,
  };
  assert(Object.values(relationships).every(Boolean));
  const report = { schemaVersion: 1, state: 'verified-public-namespace-and-descriptors-only',
    recordedAtUtc: new Date().toISOString(), ...await provenance(), nodePin, relationships, modules,
    symbols: { inspectCustom: describe(Object.getOwnPropertyDescriptor(util.inspect, 'custom')?.value),
      promisifyCustom: describe(Object.getOwnPropertyDescriptor(util.promisify, 'custom')?.value) },
    scope: 'Public ESM/CommonJS imports, ordinary reflection and identity only. No util export invoked, no getter invoked by this inspector, no private binding/source introspection. Node may initialize lazy exports while constructing its builtin ESM facade.',
    limitations: ['Function arity/name/prototype descriptors do not establish supported invocation semantics or constructibility.',
      'Accessor descriptors are recorded without calling them; their named/default value identity is deliberately not inferred.',
      'Reference identifiers are run-local identity labels, not a cross-release object identity contract.'] };
  await writeFile(join(here, 'node-inventory.json'), JSON.stringify(report, null, 2) + '\n');
  return { relationships, modules: modules.map(module => ({ id: module.id, exports: module.exports.length })) };
}

async function sourceInventory() {
  const output = resolve(process.env.NODE_COMPAT_UTIL_NODE_SOURCE ?? '/tmp/starling-node-compat/foundation-util/node-v22.14.0-source');
  const tc = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/native-toolchain-lock');
  const parserPackage = JSON.parse(await readFile(join(tc, 'node_modules/rolldown/package.json')));
  assert.equal(parserPackage.version, '1.2.16');
  const parserPath = join(tc, 'node_modules/rolldown/dist/parse-ast-index.mjs');
  const { parseAst } = await import(pathToFileURL(parserPath));
  const requested = [
    'lib/util.js', 'lib/util/types.js', 'lib/internal/util/types.js', 'lib/internal/util.js',
    'lib/internal/util/inspect.js', 'lib/internal/util/comparisons.js', 'lib/internal/util/debuglog.js',
    'lib/internal/util/colors.js', 'lib/internal/util/parse_args/parse_args.js', 'lib/internal/util/parse_args/utils.js',
    'lib/internal/encoding.js', 'lib/internal/mime.js', 'lib/internal/errors.js', 'lib/internal/validators.js',
    'lib/internal/streams/utils.js', 'lib/internal/abort_controller.js', 'lib/internal/options.js',
    'lib/internal/source_map/source_map_cache.js', 'lib/internal/console/global.js',
    'lib/internal/per_context/primordials.js', 'lib/internal/bootstrap/realm.js',
    'src/node_util.cc', 'src/node_types.cc', 'doc/api/util.md',
    'test/parallel/test-util.js', 'test/parallel/test-util-types.js', 'test/parallel/test-util-format.js',
    'test/parallel/test-util-inspect.js', 'test/parallel/test-util-promisify.js',
    'test/parallel/test-util-callbackify.js', 'test/parallel/test-util-inherits.js',
  ];
  const downloaded = [], missing = [];
  // Bounded read-only source downloads, not a recursive npm/Node module load.
  for (let i = 0; i < requested.length; i += 4) {
    const results = await Promise.all(requested.slice(i, i + 4).map(async path => {
      const url = `https://raw.githubusercontent.com/nodejs/node/${nodePin.revision}/${path}`;
      const response = await fetch(url);
      if (!response.ok) return { path, url, status: response.status };
      const bytes = new Uint8Array(await response.arrayBuffer()), localPath = join(output, path);
      await mkdir(dirname(localPath), { recursive: true }); await writeFile(localPath, bytes);
      return { path, url, localPath, bytes: bytes.length, sha256: hash(bytes) };
    }));
    for (const result of results) (result.localPath ? downloaded : missing).push(result);
  }
  assert(downloaded.some(file => file.path === 'lib/util.js'));
  assert(downloaded.some(file => file.path === 'lib/util/types.js'));
  assert(downloaded.some(file => file.path === 'lib/internal/util/types.js'));
  function visit(node, callback, ancestors = []) {
    if (!node || typeof node !== 'object') return;
    if (typeof node.type === 'string') { callback(node, ancestors); ancestors = [...ancestors, node]; }
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) for (const item of value) visit(item, callback, ancestors);
      else if (value && typeof value === 'object') visit(value, callback, ancestors);
    }
  }
  const ledger = [];
  for (const file of downloaded) {
    if (!file.path.endsWith('.js')) { ledger.push(file); continue; }
    const source = await readFile(file.localPath, 'utf8');
    const ast = parseAst(source, {}, file.path), calls = [], primordials = [], lazyExportGroups = [];
    const line = offset => source.slice(0, offset).split('\n').length;
    visit(ast, (node, ancestors) => {
      if (node.type === 'CallExpression' && node.callee?.type === 'Identifier' && ['require', 'internalBinding'].includes(node.callee.name)) {
        const argument = node.arguments[0];
        calls.push({ kind: node.callee.name, specifier: typeof argument?.value === 'string' ? argument.value : null,
          literal: typeof argument?.value === 'string', line: line(node.start),
          nestedInFunction: ancestors.some(parent => /Function|MethodDefinition/.test(parent.type)) });
      }
      if (node.type === 'VariableDeclarator' && node.init?.type === 'Identifier' && node.init.name === 'primordials' && node.id.type === 'ObjectPattern') {
        for (const property of node.id.properties) primordials.push(property.key?.name ?? property.key?.value ?? '<rest>');
      }
      if (node.type === 'CallExpression' && node.callee?.type === 'Identifier' && node.callee.name === 'defineLazyProperties') {
        lazyExportGroups.push({ line: line(node.start), sourceModule: node.arguments[1]?.value ?? null,
          names: node.arguments[2]?.elements?.map(element => element?.value ?? null) ?? [] });
      }
    });
    ledger.push({ ...file, staticCalls: calls, primordialNames: primordials, lazyExportGroups });
  }
  const availablePaths = new Set(downloaded.map(file => file.path));
  const requiredNotInSelectedLedger = [...new Set(ledger.flatMap(file => file.staticCalls ?? [])
    .filter(call => call.kind === 'require' && call.literal)
    .map(call => call.specifier))].filter(specifier => !availablePaths.has(`lib/${specifier}.js`)).sort();
  const report = { schemaVersion: 1, state: 'official-pinned-source-selected-ledger', recordedAtUtc: new Date().toISOString(),
    ...await provenance(), nodePin, sourceRoot: output,
    tagResolution: { tagApi: 'https://api.github.com/repos/nodejs/node/git/ref/tags/v22.14.0',
      annotatedTagApi: `https://api.github.com/repos/nodejs/node/git/tags/${nodePin.tagObject}`,
      taggerAtUtc: '2025-02-11T10:10:47Z' },
    parser: { package: 'rolldown/parseAst', version: parserPackage.version, path: parserPath, sha256: hash(await readFile(parserPath)) },
    files: ledger, unavailableRequestedFiles: missing, requiredNotInSelectedLedger,
    scope: 'Selected official Node source files and test sources downloaded by immutable commit. AST records literal require/internalBinding calls and primordial names without loading or executing these sources. Nested-in-function distinguishes syntactic nesting, not guaranteed lazy/eager runtime behavior.',
    limitations: ['Selected source ledger, not the complete transitive Node build graph. Unselected dependencies and nonliteral calls are explicit.',
      'Source native-binding declarations explain integration requirements; no private binding is invoked to derive runtime behavior.',
      'Test sources are inventoried, not executed. Source presence does not imply portable implementation or supported behavior.'] };
  await writeFile(join(here, 'node-source-inventory.json'), JSON.stringify(report, null, 2) + '\n');
  return { files: ledger.length, missing: missing.length, sourceRoot: output };
}

const summary = {};
if (!process.argv.includes('--sources-only')) summary.runtime = await runtimeInventory();
if (!process.argv.includes('--runtime-only')) summary.sources = await sourceInventory();
console.log(JSON.stringify(summary, null, 2));
