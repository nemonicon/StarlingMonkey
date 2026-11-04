// New pure/context IO helper only; NO owner selector/bootstrap/admit execution.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {sourceContexts,verifyNativeContexts,assertCoreContext} from './source-contexts.mjs';
const source='/private/tmp/starling-node-compat/consumers-source-v2',frozen='/tmp/starling-node-compat/production-consumers-v1/native-freeze/source';
const config={admissionSourceRoot:source,nativeConfiguredSourceRoot:source,runtimeSourceRoot:frozen,nativeFrozenSourceRoot:frozen};
let checks=0;const yes=fn=>{fn();checks++;},no=fn=>{assert.throws(fn);checks++;};
const metadata=JSON.parse(await readFile('/tmp/starling-node-compat/production-consumers-v1/native-freeze/normal-off.engine.wasm.build.json'));
const native={sourceRoot:frozen,metadata},pin={sourceRoot:frozen};
const roots=sourceContexts(config,native,pin);yes(()=>assert.equal(roots.admissionSourceRoot,source));yes(()=>assert.equal(roots.runtimeSourceRoot,native.sourceRoot));
no(()=>sourceContexts({...config,admissionSourceRoot:frozen},native,pin));no(()=>sourceContexts({...config,runtimeSourceRoot:source},native,pin));no(()=>sourceContexts(config,{...native,sourceRoot:source},pin));no(()=>sourceContexts(config,native,{sourceRoot:source}));no(()=>sourceContexts({...config,admissionSourceRoot:source+'/../consumers-source-v2'},native,pin));
no(()=>sourceContexts(config,{...native,metadata:{sourceManifest:metadata.sourceManifest.slice(1)}},pin));
const data=await verifyNativeContexts(metadata,roots);yes(()=>assert.equal(data.nativeSources,355));yes(()=>assert.equal(data.toolDependenciesVerifiedHere,false));
// Derived DATA carrier, not a genuine admit result or fake engine proof.
const names=['buffer-facade.mjs','unsupported.mjs','export-manifest.node-v22.14.0.json','factories.generated.h','buffer.cpp'].map(n=>'builtins/node-compat/'+n);
const core={schema:1,coreVersion:'sm-node-22.14.0-m0.11',allocUnsafePolicy:'zeroed-no-pool-direct-u8-v1',sourceHashes:Object.fromEntries(names.map(name=>[name,metadata.sourceManifest.find(r=>r.path===name).sha256]))};
yes(()=>assertCoreContext(core,metadata));no(()=>assertCoreContext({...core,sourceRoot:source},metadata));no(()=>assertCoreContext({...core,coreVersion:'old'},metadata));no(()=>assertCoreContext({...core,sourceHashes:{...core.sourceHashes,[names[0]]:'a'.repeat(64)}},metadata));
const output={schemaVersion:1,state:'SOURCE_CONTEXT_MODELS_AND_ACTUAL_NATIVE_HASHES_PASSED',checks,actualNativeFilesPerRoot:355,nativeRoots:2,coreCarrierIsDataOnly:true,genuineAdmitInvoked:false,ownerBootstrapOrPreflightInvoked:false,engineGuestCompilerOrNativeExecution:false};process.stdout.write(JSON.stringify(output)+'\n');
