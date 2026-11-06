// TEST ONLY. Exercise the actual candidate loader on the entire real Next app.
// Host FS, compiler, builtins and globals are used; this is not guest evidence.
import * as nodeModule from 'node:module';
import {readFileSync, statSync, realpathSync} from 'node:fs';
import {compileFunction} from 'node:vm';
import {createModuleAPI} from '../../../foundation-module/node-module-candidate-v1/module-core.mjs';

const hostRequire = nodeModule.createRequire(import.meta.url);
export function createHostModuleRequire(filename, observations) {
  const builtins = new Set(), compiled = new Set();
  const provider = {
    cwd: () => process.cwd(),
    kind(path) {
      try { const stat = statSync(path); return stat.isFile() ? 'file' : stat.isDirectory() ? 'directory' : 'other'; }
      catch (error) { if (['ENOENT', 'ENOTDIR'].includes(error.code)) return null; throw error; }
    },
    readText: path => readFileSync(path, 'utf8'),
    realpath: path => realpathSync(path),
    getBuiltin(id) { builtins.add(id); return hostRequire(id); },
    compile(source, filename) {
      compiled.add(filename);
      return compileFunction(source, ['exports', 'require', 'module', '__filename', '__dirname'], {filename});
    },
  };
  const api = createModuleAPI(provider, nodeModule.builtinModules,
    ['node:sea', 'node:sqlite', 'node:test', 'node:test/reporters'], Object.keys(nodeModule), nodeModule.constants);
  observations.sourceOnlyCandidate = true;
  observations.nativeProviderExecuted = false;
  observations.hostGlobalsAndNodeBuiltins = true;
  observations.snapshot = () => ({builtins: [...builtins].sort(), compiled: [...compiled].sort(),
    cachedModules: Object.keys(api.default._cache).length,
    candidateModuleIdentity: api.default.createRequire(filename)('node:module') === api.default});
  return api.createRequire(filename);
}
