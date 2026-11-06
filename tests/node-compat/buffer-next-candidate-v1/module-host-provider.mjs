// TEST ONLY. Candidate Buffer in an isolated application VM context; host
// globals and Node's own internals keep the original host Buffer untouched.
import * as nodeModule from 'node:module';
import {readFileSync,statSync,realpathSync} from 'node:fs';
import {compileFunction,createContext} from 'node:vm';
import {createModuleAPI} from '../foundation-module/node-module-candidate-v1/module-core.mjs';
import {createBufferModule} from './native/builtins/node-compat/buffer-facade.mjs';
import {hostKernel} from './host-kernel.mjs';
const hostRequire=nodeModule.createRequire(import.meta.url),hostBuffer=globalThis.Buffer;
export function createHostModuleRequire(filename,observations){
 const custom=createBufferModule(hostKernel),builtins=new Set(),compiled=new Set();
 const sandbox={};
 for(const key of Reflect.ownKeys(globalThis))if(!['global','globalThis','Buffer'].includes(key))Object.defineProperty(sandbox,key,Object.getOwnPropertyDescriptor(globalThis,key));
 sandbox.Buffer=custom.Buffer;const context=createContext(sandbox);context.global=context;
 const provider={cwd:()=>process.cwd(),kind(path){try{const s=statSync(path);return s.isFile()?'file':s.isDirectory()?'directory':'other';}catch(e){if(['ENOENT','ENOTDIR'].includes(e.code))return null;throw e;}},readText:p=>readFileSync(p,'utf8'),realpath:p=>realpathSync(p),getBuiltin(id){builtins.add(id);return id==='buffer'||id==='node:buffer'?custom.default:hostRequire(id);},compile(source,filename){compiled.add(filename);return compileFunction(source,['exports','require','module','__filename','__dirname'],{filename,parsingContext:context});}};
 const api=createModuleAPI(provider,nodeModule.builtinModules,['node:sea','node:sqlite','node:test','node:test/reporters'],Object.keys(nodeModule),nodeModule.constants);
 observations.sourceOnlyCandidate=true;observations.nativeProviderExecuted=false;observations.hostGlobalsAndNodeBuiltins=true;
 observations.applicationGlobalBufferReplacedInPrivateVMOnly=true;observations.hostBufferUnchanged=()=>globalThis.Buffer===hostBuffer;
 observations.snapshot=()=>({builtins:[...builtins].sort(),compiled:[...compiled].sort(),cachedModules:Object.keys(api.default._cache).length,candidateModuleIdentity:api.default.createRequire(filename)('node:module')===api.default,hostBufferUnchanged:globalThis.Buffer===hostBuffer,contextBufferSameAsBuiltin:context.Buffer===api.default.createRequire(filename)('node:buffer').Buffer});
 return api.createRequire(filename);
}
