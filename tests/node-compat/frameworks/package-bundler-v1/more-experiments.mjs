// Additional bounded host-only API/ordering experiments. No generated module
// is imported here; original sources and every generated bundle are retained.
import assert from 'node:assert/strict';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire, builtinModules } from 'node:module';
import { createHash } from 'node:crypto';
import { bundleProfile } from '../../profile-bundler.mjs';
const HERE = dirname(fileURLToPath(import.meta.url));
const require = createRequire('/private/tmp/starling-node-compat/toolchain/package.json');
const { rolldown } = await import(pathToFileURL(require.resolve('rolldown')));
const { parseAst } = await import(pathToFileURL(require.resolve('rolldown/parseAst')));
const { esmExternalRequirePlugin } = await import(pathToFileURL(require.resolve('rolldown/plugins')));
assert.equal(process.version, 'v22.14.0');
const root = join(HERE, 'additional-evidence'); await mkdir(root);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const row = async path => { const bytes = await readFile(path); return { path: resolve(path), sha256: hash(bytes), bytes: bytes.length }; };
const sourceRoot = '/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source';
const core = JSON.parse(await readFile(join(sourceRoot, 'builtins/node-compat/export-manifest.node-v22.14.0.json')));
const builtins = new Set(builtinModules), cases = [
  { name: 'package-js-commonjs', files: { 'entry.mjs': "import p from './pkg/index.js';export const value=p;", 'pkg/package.json': '{"type":"commonjs"}', 'pkg/index.js': "module.exports=require('./leaf.js');", 'pkg/leaf.js': 'module.exports={ordinary:true};' } },
  { name: 'original-plugin-js-require', original: true, files: { 'entry.mjs': "import p from './pkg/index.js';export const value=p;", 'pkg/package.json': '{"type":"commonjs"}', 'pkg/index.js': "module.exports=require('node:buffer');" } },
  { name: 'original-plugin-cjs-relative', original: true, files: { 'entry.mjs': "import p from './pkg.cjs';export const value=p;", 'pkg.cjs': "module.exports=require('./leaf.cjs');", 'leaf.cjs': 'module.exports={ordinary:true};' } },
  { name: 'bare-output-path-canonicalization', official: true, paths: true, files: { 'entry.mjs': "import p from './pkg.cjs';export const value=p;", 'pkg.cjs': "module.exports=require('buffer');" } },
  { name: 'early-external-resolver-skips-official', official: true, earlyExternal: true, files: { 'entry.mjs': "import p from './pkg.cjs';export const value=p;", 'pkg.cjs': "module.exports=require('node:buffer');" } },
  { name: 'production-dead-unselected-builtin', files: { 'entry.mjs': "import p from './pkg.cjs';export const value=p;", 'pkg.cjs': "if(process.env.NODE_ENV!=='production'){module.exports=require('node:fs')}else{module.exports={production:true}};" } },
  { name: 'production-dead-dynamic-require', files: { 'entry.mjs': "import p from './pkg.cjs';export const value=p;", 'pkg.cjs': "if(process.env.NODE_ENV!=='production'){module.exports=function(x){return require(x)}}else{module.exports={production:true}};" } },
  { name: 'unknown-env-remains', files: { 'entry.mjs': 'export const value=process.env.OTHER_ENV;' } },
  { name: 'computed-require', files: { 'entry.mjs': "import p from './pkg.cjs';export const value=p;", 'pkg.cjs': 'module.exports=function(x){return require(x)};' } },
  { name: 'require-resolve', files: { 'entry.mjs': "import p from './pkg.cjs';export const value=p;", 'pkg.cjs': "module.exports=function(){return require.resolve('./leaf.cjs')};", 'leaf.cjs': 'module.exports=1;' } },
  { name: 'module-require', files: { 'entry.mjs': "import p from './pkg.cjs';export const value=p;", 'pkg.cjs': 'module.exports=function(x){return module.require(x)};' } },
  { name: 'dynamic-import-expression', files: { 'entry.mjs': 'export async function value(x){return import(x)};' } },
];
const results = [];
for (const item of cases) {
  const folder = join(root, item.name); await mkdir(folder); const inputs = [];
  for (const [relative, text] of Object.entries({ 'package.json': '{"type":"module"}', ...item.files })) {
    const path = join(folder, relative); await mkdir(dirname(path), { recursive: true }); await writeFile(path, text + '\n', { flag: 'wx' }); inputs.push(await row(path));
  }
  const logs = [], pluginEvents = [], result = { name: item.name, input: inputs, logs, pluginEvents, generatedModuleImported: false, nativeEngineExecuted: false };
  let build;
  const guard = { name: 'selected-native-guard', resolveId: { order: item.earlyExternal ? 'pre' : undefined, handler(source, importer) {
    pluginEvents.push({ source, importer: importer ?? null });
    if (source.startsWith('node:') || builtins.has(source)) {
      if (!['buffer', 'node:buffer'].includes(source)) throw new Error('AUDIT_NATIVE_NOT_SELECTED: ' + source);
      if (item.earlyExternal) return { id: source, external: true };
    }
    return null;
  } } };
  try {
    if (item.original) {
      const chunk = await bundleProfile({ rolldown, parseAst, input: join(folder, 'entry.mjs'), builtinManifests: [core] });
      await writeFile(join(folder, 'bundle.mjs'), chunk.code, { flag: 'wx' }); result.bundle = await row(join(folder, 'bundle.mjs'));
    } else {
      const plugins = [guard]; if (item.official) plugins.push(esmExternalRequirePlugin({ external: ['buffer', 'node:buffer'] }));
      build = await rolldown({ input: join(folder, 'entry.mjs'), platform: 'neutral', treeshake: false,
        resolve: { mainFields: ['main', 'module'] }, transform: { define: { 'process.env.NODE_ENV': JSON.stringify('production') } }, plugins,
        onLog(level, log, next) { logs.push({ level, code: log.code, message: log.message }); if (level === 'error') next(level, log); } });
      const output = await build.generate({ format: 'esm', codeSplitting: false, ...(item.paths ? { paths: { buffer: 'node:buffer' } } : {}) });
      assert.equal(output.output.length, 1); const chunk = output.output[0]; parseAst(chunk.code);
      await writeFile(join(folder, 'bundle.mjs'), chunk.code, { flag: 'wx' }); result.bundle = await row(join(folder, 'bundle.mjs'));
      result.imports = chunk.imports; result.codeImports = [...chunk.code.matchAll(/from\s+["']([^"']+)["']/g)].map(x => x[1]); result.moduleIds = Object.keys(chunk.modules);
      result.residualDynamicRequire = /\b__require\b|\brequire\s*\(|\brequire\.resolve\b|\bmodule\.require\b/.test(chunk.code);
      result.residualProcess = /\bprocess\b/.test(chunk.code); result.residualDynamicImport = /\bimport\s*\(/.test(chunk.code);
    }
    result.generated = true;
  } catch (error) { result.error = { name: error.name, message: error.message, code: error.code }; }
  finally { if (build) await build.close(); }
  await writeFile(join(folder, 'result.json'), JSON.stringify(result, null, 2) + '\n', { flag: 'wx' }); results.push(result);
}
await writeFile(join(root, 'results.json'), JSON.stringify({ schemaVersion: 1, node: process.version, cases: results, generatedModuleImported: false, nativeEngineExecuted: false }, null, 2) + '\n', { flag: 'wx' });
process.stdout.write(JSON.stringify(results.map(x => ({ name: x.name, imports: x.imports, codeImports: x.codeImports, dynamicRequire: x.residualDynamicRequire, process: x.residualProcess, dynamicImport: x.residualDynamicImport, error: x.error?.message })), null, 2) + '\n');
