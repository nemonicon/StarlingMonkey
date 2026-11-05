// Bounded host-only Rolldown experiments. Generated toy modules may be loaded
// in a fresh Node process for namespace identity; no native engine or guest runs.
import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { createRequire, builtinModules } from 'node:module';
const HERE = dirname(fileURLToPath(import.meta.url));
const TOOL = '/private/tmp/starling-node-compat/toolchain';
const require = createRequire(join(TOOL, 'package.json'));
assert.equal(process.version, 'v22.14.0');
const { rolldown } = await import(pathToFileURL(require.resolve('rolldown')));
const { esmExternalRequirePlugin } = await import(pathToFileURL(require.resolve('rolldown/plugins')));
const { parseAst } = await import(pathToFileURL(require.resolve('rolldown/parseAst')));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const row = async path => { const b = await readFile(path); return { path: resolve(path), sha256: hash(b), bytes: b.length }; };
const output = join(HERE, 'evidence'); await mkdir(output);
const allowed = new Set(['node:buffer', 'buffer', 'node:stream', 'stream']);
const native = new Set(builtinModules);
const policy = { name: 'audit-native-selection', resolveId(source) {
  if (source.startsWith('node:') || native.has(source)) {
    if (!allowed.has(source)) throw new Error('AUDIT_UNSELECTED_BUILTIN: ' + source);
  }
  return null;
} };
const fixtures = [
  { name: 'official-buffer', builtin: 'node:buffer', plugins: 'official' },
  { name: 'official-bare-buffer', builtin: 'buffer', plugins: 'official' },
  { name: 'official-stream', builtin: 'node:stream', plugins: 'official' },
  { name: 'official-bare-stream', builtin: 'stream', plugins: 'official' },
  { name: 'duplicate-external', builtin: 'node:buffer', plugins: 'official', duplicate: true, execute: false },
  { name: 'manual-default-mixed-cjs', builtin: 'node:buffer', plugins: 'manual' },
  { name: 'ordinary-package-commonjs', plugins: 'none', packageOnly: true },
  { name: 'production-define', plugins: 'none', defineOnly: true },
  { name: 'dynamic-require', plugins: 'none', dynamic: true, execute: false },
  { name: 'external-esm-live', plugins: 'official', externalLive: true },
];
const results = [];
for (const fixture of fixtures) {
  const directory = join(output, fixture.name); await mkdir(directory);
  const files = { 'package.json': '{"type":"module"}\n' };
  if (fixture.packageOnly) {
    files['entry.mjs'] = "import value from './pkg/index.cjs'; export function observe(){return {value};}\n";
    files['pkg/index.cjs'] = "module.exports={fromPackage:require('./leaf.cjs'),production:process.env.NODE_ENV};\n";
    files['pkg/leaf.cjs'] = "module.exports='ordinary-cjs-leaf';\n";
  } else if (fixture.defineOnly) {
    files['entry.mjs'] = "export function observe(){return {env:process.env.NODE_ENV};}\n";
  } else if (fixture.dynamic) {
    files['entry.mjs'] = "import value from './pkg.cjs'; export function observe(){return value;}\n";
    files['pkg.cjs'] = "module.exports=function(name){return require(name);};\n";
  } else if (fixture.externalLive) {
    files['entry.mjs'] = "import value from './pkg.cjs'; import original,{number,change} from './external.mjs'; export function observe(){const before=value.number;change(2);return {sameDefault:value===original,extraDefault:Object.hasOwn(value,'default'),before,requiredAfter:value.number,esmAfter:number};}\n";
    files['pkg.cjs'] = "module.exports=require('./external.mjs');\n";
    files['external.mjs'] = "export let number=1;export function change(value){number=value;}export default {differentDefault:true};\n";
  } else {
    files['entry.mjs'] = `import expected from ${JSON.stringify(fixture.builtin)};import value from './pkg.cjs';export function observe(){return {sameDefault:value===expected,hasOwnDefault:Object.hasOwn(value,'default'),type:typeof value,keys:Object.keys(value).sort(),streamSelf:value.Stream===value};}\n`;
    files['pkg.cjs'] = `module.exports=require(${JSON.stringify(fixture.builtin)});\n`;
  }
  const inputs = [];
  for (const [file, text] of Object.entries(files)) { const path = join(directory, file); await mkdir(dirname(path), { recursive: true }); await writeFile(path, text, { flag: 'wx' }); inputs.push(await row(path)); }
  const logs = [], plugins = [policy];
  if (fixture.plugins === 'official') plugins.unshift(esmExternalRequirePlugin({ external: fixture.externalLive ? ['./external.mjs'] : [fixture.builtin] }));
  if (fixture.plugins === 'manual') plugins.unshift({ name: 'audit-exact-default-import', transform(code, id) {
    if (!id.endsWith('/pkg.cjs')) return null;
    const needle = 'require(' + JSON.stringify(fixture.builtin) + ')'; assert.equal(code.split(needle).length, 2);
    return { code: 'import __auditNativeDefault from ' + JSON.stringify(fixture.builtin) + ';\n' + code.replace(needle, '__auditNativeDefault'), map: null };
  } });
  if (fixture.plugins !== 'official') plugins.push({ name: 'audit-external-owning', resolveId(source) { if (allowed.has(source)) return { id: source, external: true }; return null; } });
  let build; const result = { name: fixture.name, input: inputs, fixture, logs, generatedBundleExecuted: false, nativeEngineExecuted: false, frameworkPackageExecuted: false };
  try {
    build = await rolldown({ input: join(directory, 'entry.mjs'), platform: 'neutral', resolve: { mainFields: ['main', 'module'] },
      treeshake: false, transform: { define: { 'process.env.NODE_ENV': JSON.stringify('production') } },
      plugins, ...(fixture.duplicate ? { external: [fixture.builtin] } : {}),
      onLog(level, log, defaultHandler) { logs.push({ level, code: log.code, message: log.message }); if (level === 'error') defaultHandler(level, log); } });
    const generated = await build.generate({ format: 'esm', codeSplitting: false, externalLiveBindings: true });
    assert.equal(generated.output.length, 1); const chunk = generated.output[0];
    const path = join(directory, 'bundle.mjs'); await writeFile(path, chunk.code, { flag: 'wx' });
    parseAst(chunk.code);
    result.bundle = await row(path); result.imports = chunk.imports; result.moduleIds = Object.keys(chunk.modules);
    result.containsResidualRequire = /\b__require\b|\brequire\s*\(/.test(chunk.code);
    result.containsProcess = /\bprocess\b/.test(chunk.code); result.bundleGenerated = true;
    if (fixture.execute !== false) {
      const script = `import * as module from ${JSON.stringify(pathToFileURL(path).href)};process.stdout.write(JSON.stringify(module.observe())+'\\n');`;
      const args = ['--input-type=module', '--eval', script];
      const child = spawnSync(process.execPath, args, { timeout: 10000, maxBuffer: 1024 * 1024, encoding: 'utf8' });
      await writeFile(join(directory, 'host.stdout.txt'), child.stdout ?? '', { flag: 'wx' }); await writeFile(join(directory, 'host.stderr.txt'), child.stderr ?? '', { flag: 'wx' });
      result.host = { executable: process.execPath, args, status: child.status, signal: child.signal, error: child.error?.message ?? null,
        stdout: await row(join(directory, 'host.stdout.txt')), stderr: await row(join(directory, 'host.stderr.txt')) };
      result.generatedBundleExecuted = true;
      if (child.status === 0) result.observed = JSON.parse(child.stdout);
    }
  } catch (error) { result.error = { name: error.name, message: error.message, code: error.code }; }
  finally { if (build) await build.close(); }
  await writeFile(join(directory, 'result.json'), JSON.stringify(result, null, 2) + '\n', { flag: 'wx' }); results.push(result);
}
const summary = { schemaVersion: 1, scope: 'HOST_ONLY_TOY_ROLLDOWN_BUNDLING_AND_NAMESPACE_IDENTITY', node: process.version,
  nodeBinary: await row(process.execPath), rolldownPackage: await row(join(TOOL, 'node_modules/rolldown/package.json')),
  rolldownVersion: JSON.parse(await readFile(join(TOOL, 'node_modules/rolldown/package.json'))).version,
  cases: results, nativeEngineExecuted: false, guestExecuted: false, frameworkPackageExecuted: false };
await writeFile(join(output, 'results.json'), JSON.stringify(summary, null, 2) + '\n', { flag: 'wx' });
process.stdout.write(JSON.stringify(results.map(r => ({ name: r.name, imports: r.imports, observed: r.observed, residualRequire: r.containsResidualRequire, error: r.error, hostStatus: r.host?.status })), null, 2) + '\n');
