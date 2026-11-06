// Host-only source parser. Never imports or evaluates fixture.mjs.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
const [file, manifest, acornPath, inventory] = process.argv.slice(2);
const { parse } = await import(pathToFileURL(acornPath).href);
const source = fs.readFileSync(file, 'utf8'), m = JSON.parse(fs.readFileSync(manifest, 'utf8'));
const tree = parse(source, { sourceType: 'module', ecmaVersion: 'latest', locations: true });
function literal(n) {
  if (n.type === 'Literal') return n.value;
  if (n.type === 'ArrayExpression') return n.elements.map(literal);
  if (n.type === 'ObjectExpression') return Object.fromEntries(n.properties.map(p => [p.key.name ?? p.key.value, literal(p.value)]));
  throw Error('Nonliteral metadata ' + n.type);
}
const metadata = Object.fromEntries(tree.body.filter(n => n.type === 'VariableDeclaration').flatMap(n => n.declarations.map(d => [d.id.name, literal(d.init)])));
assert.equal(metadata.calls, 0);
assert.deepEqual(Object.keys(metadata).sort(), ['calls', 'HASH_VECTORS', 'HMAC_VECTORS', 'EXPECTED_NAMESPACE_NAMES'].sort());
assert.deepEqual(metadata.HASH_VECTORS, m.knownHashVectors);
assert.deepEqual(metadata.HMAC_VECTORS, m.knownHmacVectors);
const exports = tree.body.filter(n => n.type === 'ExportNamedDeclaration');
assert.equal(exports.length, 1); assert.equal(exports[0].declaration.type, 'FunctionDeclaration');
const run = exports[0].declaration;
assert.equal(run.id.name, 'run'); assert.equal(run.params.length, 0); assert.equal(run.async, false); assert.equal(run.generator, false);
assert.deepEqual(tree.body.filter(n => n.type === 'ImportDeclaration').map(n => n.source.value), m.staticNativeImports);
assert.deepEqual(tree.body.map(n => n.type).filter(t => !['ImportDeclaration', 'VariableDeclaration', 'FunctionDeclaration', 'ExportNamedDeclaration'].includes(t)), []);
let topCalls = 0, cryptoSites = [], rows = [], policies = [], surrogateLiterals = [];
function visit(n, depth = 0) {
  if (!n || typeof n !== 'object') return;
  const isFn = ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'].includes(n.type), d = depth + (isFn ? 1 : 0);
  if (['CallExpression', 'NewExpression', 'AwaitExpression', 'ImportExpression'].includes(n.type) && depth === 0) topCalls++;
  if (n.type === 'CallExpression' || n.type === 'NewExpression') {
    const c = n.callee;
    if (c?.type === 'MemberExpression' && !c.computed && ['createHash', 'createHmac', 'update', 'digest', 'Hash', 'Hmac'].includes(c.property.name)) cryptoSites.push({ operation: c.property.name, line: n.loc.start.line, insideFunction: depth > 0 });
    if (c?.type === 'Identifier' && c.name === 'row' && n.arguments[0]?.type === 'Literal') rows.push(n.arguments[0].value);
    if (c?.type === 'Identifier' && c.name === 'policy' && n.arguments[0]?.type === 'Literal') policies.push(n.arguments[0].value);
  }
  if (n.type === 'ObjectExpression') for (const pr of n.properties)
    if (pr.type === 'Property' && (pr.key.name ?? pr.key.value) === 'id' && pr.value.type === 'Literal' && String(pr.value.value).startsWith('invalid-')) policies.push(pr.value.value);
  if (n.type === 'Literal' && typeof n.value === 'string' && n.value.includes(String.fromCharCode(0xd834))) surrogateLiterals.push(n.value);
  for (const [key, value] of Object.entries(n)) {
    if (['loc', 'start', 'end'].includes(key)) continue;
    if (Array.isArray(value)) { for (const child of value) if (child && typeof child === 'object') visit(child, d); }
    else if (value && typeof value === 'object') visit(value, d);
  }
}
visit(tree);
assert.equal(topCalls, 0); assert.ok(cryptoSites.length > 0 && cryptoSites.every(x => x.insideFunction));
const blockLoops = [];
function findBlocks(n) {
  if (!n || typeof n !== 'object') return;
  if (n.type === 'ForOfStatement' && n.left.type === 'VariableDeclaration' && n.left.declarations[0].id.name === 'n') blockLoops.push(literal(n.right));
  for (const [key,value] of Object.entries(n)) {
    if (['loc','start','end'].includes(key)) continue;
    if (Array.isArray(value)) { for (const c of value) if (c && typeof c === 'object') findBlocks(c); }
    else if (value && typeof value === 'object') findBlocks(value);
  }
}
findBlocks(run); assert.deepEqual(blockLoops, [[55,56,63,64,65]]);
const caseIds = [...metadata.HASH_VECTORS.map(x => x.id), ...rows, ...blockLoops[0].map(n => 'hash-block-' + n), ...metadata.HMAC_VECTORS.map(x => x.id)];
assert.equal(caseIds.length, 20); assert.equal(new Set(caseIds).size, 20); assert.deepEqual([...caseIds].sort(), [...m.nodeComparableCases].sort());
assert.equal(policies.length, 8); assert.equal(new Set(policies).size, 8); assert.deepEqual([...policies].sort(), [...m.profileOnlyCases].sort());
assert.equal(surrogateLiterals.length, 2);
for (const s of surrogateLiterals) assert.equal(Buffer.from(s, 'utf8').toString('hex'), m.stringConversionChecks.surrogateExpectedUtf8Hex);
for (const v of [...metadata.HASH_VECTORS, ...metadata.HMAC_VECTORS]) assert.match(v.expectedHex, /^[a-f0-9]{64}$/);
assert.equal(Math.max(...metadata.HMAC_VECTORS.map(v => v.keyHex ? v.keyHex.length / 2 : Buffer.byteLength(v.keyUtf8))), m.limits.fixtureMaximumKeyBytes);
assert.equal(Math.max(...metadata.HMAC_VECTORS.map(v => Buffer.byteLength(v.message))), m.limits.fixtureMaximumMessageBytes);
const inv = JSON.parse(fs.readFileSync(inventory, 'utf8'));
assert.equal(metadata.EXPECTED_NAMESPACE_NAMES.length, 68);
assert.deepEqual([...metadata.EXPECTED_NAMESPACE_NAMES].sort(), [...inv.initialEnumerableKeys, 'default'].sort());
assert.ok(source.includes("Buffer.from([0xd1, 97, 98, 99, 0xe2])") && source.includes('bufferBacking.subarray(1, 4)'));
assert.ok(source.includes('c.update(bufferView) === c; bufferView.fill(120)'));
assert.ok(Object.values(m.requiredFutureInputs).every(v => v === null) && m.sourcePeer === null && m.rootAuthority === null);
for (const k of ['runtimeActionsExecuted', 'hostOrGuestCryptoExecuted', 'nativeCompiled', 'componentBuilt', 'operationalAdmission', 'runtimeAcceptanceClaim']) assert.equal(m[k], false);
assert.deepEqual(m.proposedSelectedInterfaces, []); assert.deepEqual(m.requiredFinalEmittedImports, []);
console.log(JSON.stringify({ state: 'STATIC_SOURCE_AND_LITERAL_DATA_CHECKS_ONLY', topLevelOperationCount: topCalls, imports: m.staticNativeImports, exports: ['run()->string'], acceptedCaseIds: caseIds.sort(), profileCaseIds: policies.sort(), cryptoSourceCallSites: cryptoSites, namespaceNames: 68, unicodeSourceLiteralUtf8Checked: true, algorithmsExecuted: [], fixtureImported: false, fixtureRunCalled: false }));
