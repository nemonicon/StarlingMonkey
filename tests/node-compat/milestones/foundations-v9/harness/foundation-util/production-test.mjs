// Host-source gate only; actual installed builtin component gates follow wiring.
import assert from 'node:assert/strict';
import * as canonical from '../../../builtins/node-compat/util.mjs';
import * as canonicalTypes from '../../../builtins/node-compat/util-types.mjs';
import * as canonicalSys from './canonical-sys.mjs';
import * as nodeUtil from 'node:util';
import * as nodeTypes from 'node:util/types';
import * as nodeSys from 'node:sys';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {runComponentCases} from './component-cases.mjs';
import {validateManifest} from '../../../builtins/node-compat/validate-manifest.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../..'),directory=join(root,'builtins/node-compat'),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const scope=JSON.parse(await readFile(join(here,'prototype-scope.json'))),manifest=JSON.parse(await readFile(join(directory,'export-manifest.util.node-v22.14.0.json')));
validateManifest(manifest,JSON.parse(await readFile(join(directory,'manifest.schema.json'))));assert.equal(manifest.profileVersion,'sm-node-22.14.0-m0.7');
const generation=spawnSync(process.execPath,[join(directory,'generate-util-factories.mjs'),'--check'],{encoding:'utf8'});assert.equal(generation.status,0,generation.stderr);
const header=await readFile(join(directory,'util-factories.generated.h'),'utf8'),match=header.match(/R"SM_NODE_PROFILE\(([\s\S]*)\)SM_NODE_PROFILE";\n$/);assert(match);
// C++ evaluate_factory sets forceStrictMode on the entire script. The indirect
// eval directive here deliberately models that exact script-level contract.
const factory=(0,eval)('"use strict"; ('+match[1]+')');assert.equal(factory.length,1);
const graph=factory(undefined),factorySys=Object.freeze(Object.assign(Object.create(null),graph.root));
assert(Object.isFrozen(graph)&&Object.isFrozen(graph.root)&&Object.isFrozen(graph.types));
assert.equal(Object.getPrototypeOf(graph.root),null);assert.equal(Object.getPrototypeOf(graph.types),null);
assert.equal(graph.root.types,graph.types.default);assert.equal(graph.root.default.types,graph.types.default);
const features={sharedArrayBuffer:typeof SharedArrayBuffer==='function',transfer:true,resizable:true};
const expected=await runComponentCases({util:nodeUtil,types:nodeTypes,sys:nodeSys,predicateNames:scope.typesImplemented,features});
const records=[];
for(const[name,util,types,sys]of [['canonical-esm',canonical,canonicalTypes,canonicalSys],['strict-generated-factory',graph.root,graph.types,factorySys]]){
  assert.deepEqual(Object.keys(util).sort(),manifest.modules['node:util'].exports);assert.deepEqual(Object.keys(types).sort(),manifest.modules['node:util/types'].exports);
  const result=await runComponentCases({util,types,sys,predicateNames:scope.typesImplemented,features});assert.deepEqual(result,expected);
  let deferredChecks=0;
  for(const[id,ns,deferred]of [['node:util',util,manifest.modules['node:util'].unsupportedStatic],['node:util/types',types,manifest.modules['node:util/types'].unsupportedStatic]])for(const operation of deferred)for(const construct of [false,true]){
    let error;try{if(construct)Reflect.construct(ns[operation],[]);else ns[operation]();}catch(caught){error=caught;}
    assert.equal(error?.code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(error.module,id);assert.equal(error.operation,operation==='debug'?'debuglog':operation);assert.equal(error.profile,manifest.profileVersion);deferredChecks++;
  }
  function strictReceiver(callback){'use strict';callback(null,this===undefined?'undefined':typeof this);}
  assert.equal(await util.promisify(strictReceiver)(),'undefined','strict wrapper receiver');
  records.push({name,checks:result.checks,deferredChecks,features,observations:result.observations,strictScriptReceiver:true});
}
// Extra hardening beyond the earlier prototype: errors/options are unaffected
// by replaced globals, Object.assign or an inherited Error.code setter.
const ErrorCtor=globalThis.Error,TypeErrorCtor=globalThis.TypeError,assign=Object.assign,codeDescriptor=Object.getOwnPropertyDescriptor(ErrorCtor.prototype,'code');
let unsupported,invalid,setterCalls=0,depth;
try{
  Object.defineProperty(ErrorCtor.prototype,'code',{set(){setterCalls++;throw new ErrorCtor('inherited setter');},configurable:true});
  globalThis.Error=function(){throw new ErrorCtor('poisoned Error global');};globalThis.TypeError=function(){throw new ErrorCtor('poisoned TypeError global');};Object.assign=function(){throw new ErrorCtor('poisoned assign');};
  try{graph.root.inspect();}catch(error){unsupported=error;}
  try{graph.root.inherits(null,function(){});}catch(error){invalid=error;}
  const old=graph.root.inspect.defaultOptions.depth;graph.root.inspect.defaultOptions={depth:4};depth=graph.root.inspect.defaultOptions.depth;graph.root.inspect.defaultOptions={depth:old};
}finally{globalThis.Error=ErrorCtor;globalThis.TypeError=TypeErrorCtor;Object.assign=assign;if(codeDescriptor)Object.defineProperty(ErrorCtor.prototype,'code',codeDescriptor);else delete ErrorCtor.prototype.code;}
assert.equal(unsupported?.code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(unsupported.profile,manifest.profileVersion);assert.equal(invalid?.code,'ERR_INVALID_ARG_TYPE');assert.equal(setterCalls,0);assert.equal(depth,4);
const names=['util.mjs','util-types.mjs','util-core.mjs','util-metadata.mjs','util-unsupported.mjs','export-manifest.util.node-v22.14.0.json','generate-util-factories.mjs','util-factories.generated.h','LICENSE.util'];
const report={schemaVersion:1,state:'canonical-source-and-strict-generated-factory-host-gates-passed',atUtc:new Date().toISOString(),node:process.version,executableSha256:hash(await readFile(process.execPath)),manifestVersion:manifest.profileVersion,sourceFiles:await Promise.all(names.map(async path=>({path,sha256:hash(await readFile(join(directory,path)))}))),runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),records,hardening:{capturedErrorConstructors:true,inheritedErrorCodeSetterCalls:setterCalls,capturedAssignDefaultOptions:depth,matchedStrictScript:true},scope:'Public Node source/factory checks only. No shared registration/CMake/build changes, native helper, installed util builtin component proof, CJS admission or new host capability.'};
await writeFile(join(here,'production-source-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,records:records.map(({name,checks,deferredChecks})=>({name,checks,deferredChecks})),hardening:report.hardening},null,2));
