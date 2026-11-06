"""Authoring-only source assembly. Do not rerun in the held family."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
PARENT=REPO/'tests/node-compat/foundation-http/next-http-candidate-v1/wasi-adapter.mjs'
NATIVE=Path('/private/tmp/starling-node-compat/next-native-profile-v2/source')
def desc(path):
    raw=path.read_bytes();return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def write(name,text):(HERE/name).write_text(text)
parent=PARENT.read_text()
before='''      return runFreshRequest(handleResources, undefined, incoming, outparam);'''
after='''      let entered=false;
      try {
        return runFreshRequest((...args)=>{
          entered=true;
          return handleResources(...args);
        },undefined,incoming,outparam);
      } catch(error) {
        if(!entered)disposeBeforeEntry(incoming,outparam);
        throw error;
      }'''
assert parent.count(before)==1
disposal='''
// The caller still owns incoming/outparam until native callback entry. Always
// attempt both drops, preserving the original pre-entry error even if cleanup
// itself refuses. Cleanup failure is diagnostic and cannot turn into success.
function disposeBeforeEntry(incoming,outparam) {
  let failures=0;
  for(const value of [incoming,outparam])try{drop(value);}catch{failures++;}
  if(failures)try{console.error('NEXT_COMPONENT_PRE_ENTRY_DISPOSAL_FAILURE',failures);}catch{}
}
'''
adapter=parent.replace(before,after)+disposal
write('adapter-descendant.mjs',adapter)
lifecycle=(HERE/'lifecycle.mjs').read_text().replace('export function ','function ')
common="""// UNCOMPILED raw ESM entry. No bootstrap, FS, clocks, entropy or Promise
// workload runs at INIT. No bundler, rewritten Next code or host Node adapter.
import {bootstrap} from 'starling:node-startup';
import {createServerHandler,runFreshRequest,runNeutralServer} from 'starling:node-http';
import Module from 'node:module';
import fs from 'node:fs';
import * as types from 'wasi:http/types@0.2.10';
"""
body=adapter.replace('export function createWasiHttpHandler','function createWasiHttpHandler')+'\n'+lifecycle+'\n'
write('guest-entry.mjs',common+body+(HERE/'next-prepare.mjs').read_text()+
      '\nexport const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry});\n')
dependency="""import {Buffer} from 'node:buffer';
import {AsyncLocalStorage} from 'node:async_hooks';
import vm from 'node:vm';
import {createGzip,gzipSync,gunzipSync} from 'node:zlib';
import {Readable,Writable} from 'node:stream';
import {pipeline} from 'node:stream/promises';
import {setImmediate,setTimeout} from 'node:timers';
import {randomBytes,randomFillSync,randomUUID} from 'node:crypto';
"""
write('dependency-entry.mjs',common+dependency+body+(HERE/'dependency-prepare.mjs').read_text()+
      '\nexport const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer:prepareDependencyServer,disposeBeforeEntry});\n')
deps=HERE/'deps';deps.mkdir(exist_ok=False)
wit=[]
for old in sorted((NATIVE/'host-apis/wasi-0.2.10/wit/deps').glob('*/package.wit')):
    target=deps/old.parent.name/'package.wit';target.parent.mkdir();target.write_bytes(old.read_bytes())
    wit.append({'source':desc(old),'copy':desc(target)})
refs={'schemaVersion':1,'rawSingleEsm':True,'worldPackage':'starling:next-component@0.1.0','worldName':'next-http',
      'nativeSourceRoot':str(NATIVE),'parentAdapter':desc(PARENT),'adapterDerivation':{'before':before,'after':after,'appended':disposal},
      'nativeApis':[desc(NATIVE/x) for x in ['builtins/node-compat/private-startup-export-manifest.v1.json',
       'builtins/node-compat/next-http/private-http-export-manifest.v1.json','builtins/node-compat/next-http/http-core.mjs',
       'builtins/node-compat/startup-core.mjs','runtime/async_context_runtime.cpp']],
      'witDependencies':wit,'actualNativeEngine':None,'actualComponent':None,'actualGuestExecution':None,
      'fixtureContract':desc(REPO/'tests/node-compat/frameworks/nextjs/fixture-contract.json'),
      'applicationSourceRoot':'/private/tmp/starling-node-compat/next-http-bridge-module-v1/application',
      'nextOptionEvidence':[desc(Path('/private/tmp/starling-node-compat/next-http-bridge-module-v1/application/node_modules/next/dist/server')/x)
                           for x in ('next.js','lib/start-server.js','next-server.js')],
      'readinessFailurePolicy':'One sticky neutral initialization promise per component; no retry/reset; dispose unentered request/outparam pairs.',
      'requiredRoutingEnvironment':'STARLING_NEXT_ORIGIN canonical HTTP(S) origin, set independently of incoming requests',
      'modelTestsProveNativeAsync':False}
write('references.json',json.dumps(refs,indent=2)+'\n')
print(json.dumps({'entries':2,'parentAdapter':refs['parentAdapter'],'witDependencies':len(wit),'operationalActions':False}))
