// Experimental build-time packaging helper. Importing this file launches nothing.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { lstat, readFile, readdir, readlink, realpath } from 'node:fs/promises';
import Module, { createRequire } from 'node:module';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE=dirname(fileURLToPath(import.meta.url));
const ORIGINAL='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/clock-package-loader-candidate-v1';
const PACKAGE='/private/tmp/starling-node-compat/import-abi-clock-io-v1-package';
const hash=b=>createHash('sha256').update(b).digest('hex');
const equal=(a,b)=>assert.deepEqual(a,b);
let handleIssued=false;

function data(value,label){
  assert(value!==null&&typeof value==='object'&&!Array.isArray(value),label);
  assert([Object.prototype,null].includes(Object.getPrototypeOf(value)),label);
  const ds=Object.getOwnPropertyDescriptors(value);
  for(const [name,d]of Object.entries(ds))assert(Object.hasOwn(d,'value')&&typeof name==='string',label+' accessors');
  assert(Reflect.ownKeys(value).every(k=>typeof k==='string'),label+' symbols');
  return value;
}
function descriptor(value){
  data(value,'descriptor');equal(Object.keys(value).sort(),['bytes','path','sha256']);
  const {path,sha256,bytes}=value;
  assert(typeof path==='string'&&path.startsWith('/')&&!path.split('/').includes('..'));
  assert(typeof sha256==='string'&&/^[0-9a-f]{64}$/.test(sha256));
  assert(Number.isSafeInteger(bytes)&&bytes>=0);
  return Object.freeze({path,sha256,bytes});
}
function physical(path){return path.startsWith('/tmp/')?'/private'+path:path;}
function safe(path){assert(typeof path==='string'&&path&&!path.startsWith('/')&&!path.includes('\\')&&!path.includes('\0')&&path.split('/').every(p=>p&&p!=='.'&&p!=='..'));return path;}
function frozen(value){if(value&&typeof value==='object'){for(const child of Object.values(value))frozen(child);Object.freeze(value);}return value;}
function strings(value){assert(Array.isArray(value)&&Object.getPrototypeOf(value)===Array.prototype);const result=[];for(let i=0;i<value.length;i++){const d=Object.getOwnPropertyDescriptor(value,String(i));assert(d&&Object.hasOwn(d,'value')&&typeof d.value==='string');result.push(d.value);}assert(Reflect.ownKeys(value).every(k=>k==='length'||typeof k==='string'&&/^(0|[1-9][0-9]*)$/.test(k)&&Number(k)<value.length));return Object.freeze(result);}

export function environmentModel(environment,execArgv,version,platform,arch){
  assert(version==='v22.14.0'&&platform==='darwin'&&arch==='arm64');equal(execArgv,[]);
  for(const name of ['NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK'])assert(!environment[name],name);
  return true;
}

export function eligibilityModel(build,failed,metadata,refs){
  assert(build.schemaVersion===1&&build.state==='INDEPENDENT_CLOCK_IO_TOOLS_BUILD_RESULTS_REVIEW_PASSED_V2'&&build.verifiedPassed===true);
  assert(build.sourceIndexSha256==='55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f');
  assert(build.artifacts.length===25&&build.coverage.packageRegularFiles===4889&&build.coverage.privateAliases===21);
  equal(build.actualPrivatePackageInventory,refs.packageInventory);
  assert(build.artifacts.some(r=>r.path===PACKAGE+'/lib/spidermonkey-embedding-splicer.core.wasm'&&r.sha256==='61685a01168e4f3ed12cf701bcde1a568992ea16d4a33266cbd2784fc1532abb'));
  assert(failed.schemaVersion===1&&failed.state==='INDEPENDENT_CLOCK_IO_VALID_ADAPTER_METADATA_FAILURE_REVIEW_PASSED_V1'&&failed.verifiedPassed===true);
  assert(failed.phasePassed===false&&failed.adapterAccepted===false&&failed.metadataDecoded===false&&failed.coreDataAuditPassed===true);
  assert(failed.prunerExitCode===0&&failed.nodeCoreValidationExitCode===0&&failed.metadataExitCode===1&&failed.actualWorkerExitCode===1);
  assert(metadata.schemaVersion===1&&metadata.state==='INDEPENDENT_CLOCK_IO_METADATA_PACKAGE_RESULTS_REVIEW_PASSED_V1'&&metadata.verifiedPassed===true);
  assert(metadata.sourceIndexSha256==='28a8cdab6315394f0479e7a3d9988cedcf4b59ed25bb596ee1fdb40df757ce3a');
  assert(metadata.metadataContinuationPassed===true&&metadata.metadataPackageValidatedByActualNativeDecoder===true);
  assert(metadata.previousPhasePassed===false&&metadata.previousPhaseRemainsFailed===true&&metadata.adapterPromoted===false&&metadata.operationalAdmission===false);
  assert(metadata.decodedPackageCount===6&&metadata.decodedDeclarationCount===28&&metadata.observedResourceAliasClauseCount===10);equal(metadata.packageVersions,['0.2.0']);
  for(const key of ['normalizedAdapter','prunedAdapter','metadataPayload']){equal(failed[key],refs[key]);equal(metadata[key],refs[key]);}
  assert(refs.prunedAdapter.sha256==='87777d4e02ee58a753f1ead050516e612619466e77165a2ab109c1d1cbff6aba'&&refs.prunedAdapter.bytes===48808);
  assert(refs.metadataPayload.sha256==='7485a77ee78375ef134c4cebca67142ded37cd68891130b0213986a27f84c072');
  return true;
}

export function releaseMetadataModel(metadata,engineSha256){
  assert(metadata&&typeof metadata==='object'&&metadata.engineSha256===engineSha256,'Actual complete sidecar must match engine bytes');
  assert(metadata.observedCMakeOptions?.CMAKE_BUILD_TYPE==='Release','Only unambiguous Release; no DEBUG or legacy fallback');
  assert(metadata.oomTesting===false&&metadata.debuggerEnabled===false&&metadata.wptSupportEnabled===false);
  assert(metadata.profileEnabled===true&&metadata.strictInitialization===true&&metadata.abiFixEnabled===true&&metadata.bigIntFixEnabled===true);
  assert(['off','runtime-only'].includes(metadata.entropyPolicy));
  return true; // Consistency only; genuine native artifact admission belongs to caller.
}

export function optionSnapshot(source,options,root,refs){
  assert(typeof source==='string'&&Buffer.byteLength(source)<=32*1024*1024&&hash(source)===root.guestSourceSha256);
  data(options,'component options');equal(Object.keys(options).sort(),['disableFeatures','enableAot','enableFeatures','engine','env','preview2Adapter','selectedInterfaces','witWorld','worldName']);
  assert(options.engine===root.nativeEngine.path&&options.preview2Adapter===refs.prunedAdapter.path);
  assert(typeof options.witWorld==='string'&&Buffer.byteLength(options.witWorld)<=1024*1024&&hash(options.witWorld)===root.witWorldSha256);
  assert(typeof options.worldName==='string'&&options.worldName===root.worldName&&/^[a-z][a-z0-9-]*$/.test(options.worldName));
  assert(options.enableAot===false);data(options.env,'explicit empty component env');equal(Object.keys(options.env),[]);
  const selectedInterfaces=strings(options.selectedInterfaces),disableFeatures=strings(options.disableFeatures),enableFeatures=strings(options.enableFeatures);
  equal(selectedInterfaces,root.selectedInterfaces);equal(disableFeatures,root.disableFeatures);equal(enableFeatures,[]);
  return frozen({source,selectedInterfaces,publicOptions:{engine:options.engine,preview2Adapter:options.preview2Adapter,witWorld:options.witWorld,worldName:options.worldName,disableFeatures:[...disableFeatures],enableFeatures:[],enableAot:false,env:{}}});
}

class Capture {
  files=new Map();families=[];trees=[];
  async file(raw){
    const row=descriptor(raw),path=physical(row.path);
    for(let p=path;;p=dirname(p)){const s=await lstat(p);assert(!s.isSymbolicLink(),p);if(dirname(p)===p)break;}
    const a=await lstat(path);assert(a.isFile()&&a.size===row.bytes);
    const h=createHash('sha256');for await(const chunk of createReadStream(path))h.update(chunk);
    const b=await lstat(path);equal([a.dev,a.ino,a.size,a.mtimeMs,a.ctimeMs,a.mode,a.nlink],[b.dev,b.ino,b.size,b.mtimeMs,b.ctimeMs,b.mode,b.nlink]);assert(h.digest('hex')===row.sha256);
    const item={row,path,identity:[b.dev,b.ino,b.size,b.mtimeMs,b.ctimeMs,b.mode,b.nlink]};
    const old=this.files.get(path);if(old){assert(old.row.sha256===row.sha256&&old.row.bytes===row.bytes);equal(old.identity,item.identity);}else this.files.set(path,item);
    return path;
  }
  async json(row){assert(row.bytes<=32*1024*1024);const path=await this.file(row),bytes=await readFile(path);assert(hash(bytes)===row.sha256);return frozen(JSON.parse(bytes));}
  async family(row){
    const index=await this.json(row),root=dirname(physical(row.path)),expected=new Set(['index.json']);
    for(const file of index.files){safe(file.path);assert(!expected.has(file.path));expected.add(file.path);await this.file({path:join(root,file.path),sha256:file.sha256,bytes:file.bytes});}
    equal(await walk(root),[...expected].sort());this.families.push({root,expected:[...expected].sort()});return index;
  }
  async proof(pair){const ix=await this.family(pair.index),base=dirname(physical(pair.index.path));assert(ix.files.filter(r=>join(base,r.path)===physical(pair.result.path)&&r.sha256===pair.result.sha256&&r.bytes===pair.result.bytes).length===1);return this.json(pair.result);}
  async tree(inventory){
    assert(inventory.root===PACKAGE&&inventory.files.length===4889&&inventory.links.length===21);
    const root=inventory.root,files=new Set(),links=new Map();
    const dir=await lstat(root);assert(dir.isDirectory()&&!dir.isSymbolicLink()&&(dir.mode&0o777)===0o700);
    for(const r of inventory.files){const name=safe(r.relativePath);assert(!files.has(name)&&physical(r.path)===join(root,name));files.add(name);const path=await this.file({path:r.path,sha256:r.sha256,bytes:r.bytes}),s=await lstat(path);assert((s.mode&0o777)===r.mode&&s.nlink===1);}
    for(const r of inventory.links){safe(r.path);assert(!files.has(r.path)&&!links.has(r.path));links.set(r.path,r);}
    const state={root,identity:[dir.dev,dir.ino],files:[...files].sort(),links:[...links.values()]};await checkTree(state);this.trees.push(state);
  }
  async recheck(){for(const item of [...this.files.values()])await this.file(item.row);for(const f of this.families)equal(await walk(f.root),f.expected);for(const t of this.trees)await checkTree(t);}
}
async function walk(root){
  const result=[];
  async function visit(path,prefix){for(const n of await readdir(path)){const p=join(path,n),r=prefix?prefix+'/'+n:n,s=await lstat(p);if(s.isDirectory())await visit(p,r);else{assert(s.isFile()&&!s.isSymbolicLink(),p);result.push(r);}}}
  await visit(root,'');return result.sort();
}
async function checkTree(tree){
  const rootStat=await lstat(tree.root);assert(rootStat.isDirectory()&&!rootStat.isSymbolicLink()&&(rootStat.mode&0o777)===0o700);equal([rootStat.dev,rootStat.ino],tree.identity);
  const expected=new Set([...tree.files,...tree.links.map(r=>r.path)]),found=[];
  async function visit(path,prefix){for(const n of await readdir(path)){const p=join(path,n),r=prefix?prefix+'/'+n:n,s=await lstat(p);if(s.isDirectory())await visit(p,r);else if(s.isSymbolicLink()){const declared=tree.links.find(l=>l.path===r);assert(declared&&await readlink(p)===declared.target);const actual=await realpath(p);assert(actual===declared.resolvedPath&&actual.startsWith(tree.root+sep)&&tree.files.includes(relative(tree.root,actual)));found.push(r);}else{assert(s.isFile());found.push(r);}}}
  await visit(tree.root,'');equal(found.sort(),[...expected].sort());
}

async function noExternalSearchRoots(){
  const roots=new Set(Module.globalPaths.map(physical));
  for(let p=dirname(PACKAGE);;p=dirname(p)){roots.add(join(p,'node_modules'));if(dirname(p)===p)break;}
  for(const path of roots){
    if(path.startsWith(PACKAGE+sep))continue;
    let found;try{found=await lstat(path);}catch(error){if(error.code!=='ENOENT')throw error;}
    assert(found===undefined,'External Node dependency search root must be absent: '+path);
  }
}

function rootModel(root,own,refs){
  assert(root.schemaVersion===1&&root.state==='ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V1'&&root.phase==='experimental-component-construction');
  equal(root.sourceIndex,own);assert(root.packageRoot===PACKAGE);
  assert(root.packageModuleInitializationAllowed===true&&root.componentConstructionAllowed===true&&root.engineInitializationDuringConstructionAllowed===true);
  assert(root.nativeArtifactAdmissionMustBePerformedByCaller===true&&root.freshOwnedNodeProcessRequired===true);
  for(const k of ['adapterPromotionAllowed','defaultPackagerReplacementAllowed','keyOrCryptoWorkloadsAllowed','ordinaryGuestExportsAllowed','hostServersAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed'])assert(root[k]===false,k);
  for(const k of ['toolsBuildReview','failedAdapterPhaseReview','metadataReview'])equal(root[k],refs[k]);
  descriptor(root.nativeEngine);descriptor(root.nativeMetadata);assert(root.nativeMetadata.path===root.nativeEngine.path+'.build.json');
  assert(typeof root.privateTemporaryRoot==='string'&&root.privateTemporaryRoot.startsWith('/private/tmp/')&&!root.privateTemporaryRoot.split('/').includes('..'));
  assert(/^[0-9a-f]{64}$/.test(root.guestSourceSha256)&&/^[0-9a-f]{64}$/.test(root.witWorldSha256));
  strings(root.selectedInterfaces);strings(root.disableFeatures);
}

function createSelected(context){
  let attempted=false;
  return Object.freeze({provenance:context.provenance,
    recheck:()=>context.recheck(),
    componentize:async(source,options)=>{
      try{
        assert(!attempted,'Exactly one construction attempt per fresh owned helper handle');attempted=true;
        // Capture synchronously before the first await; even validation failures
        // and forbidden repeat calls still execute the final protection audit.
        const call=optionSnapshot(source,options,context.root,context.refs);
        await context.recheck();
        releaseMetadataModel(context.nativeMetadata,context.root.nativeEngine.sha256);
        const policy=context.selectedInterfacePolicy(context.nativeMetadata,{...call.publicOptions,selectedInterfaces:call.selectedInterfaces});
        assert(policy!==null,'Modern explicit capability policy required');
        const result=await context.packageComponentize(call.source,call.publicOptions);
        assert(result&&result.component instanceof Uint8Array,'Actual packager must return component bytes');
        const interfaceAudit=await context.auditSelectedInterfaces(context.toolchain,result.component,policy);
        return {...result,interfaceAudit,packagingProvenance:context.provenance};
      }finally{await context.recheck();}
    }});
}

export async function loadExperimentalClockPackage({configDescriptor}){
  const configRow=descriptor(configDescriptor);assert(!handleIssued,'One helper load per fresh owned process');handleIssued=true;
  assert(HERE===ORIGINAL,'Use the explicit original helper context');
  environmentModel({...process.env},process.execArgv,process.version,process.platform,process.arch);
  const c=new Capture();
  try{
  const config=await c.json(configRow);assert(config.schemaVersion===1&&config.state==='CLOCK_PACKAGE_LOADER_CONFIG_V1');
  const own=descriptor(config.sourceIndex);assert(physical(own.path)===join(HERE,'index.json'));await c.family(own);
  const refsRow=await fingerprint(join(HERE,'references.json')),refs=await c.json(refsRow);
  const inputs=await c.json(await fingerprint(join(HERE,'source-inputs.json')));
  for(const row of inputs.files)await c.file(row);for(const ix of inputs.families)await c.family(ix);
  const build=await c.proof(refs.toolsBuildReview),failed=await c.proof(refs.failedAdapterPhaseReview),metadata=await c.proof(refs.metadataReview);
  eligibilityModel(build,failed,metadata,refs);
  const root=await c.json(config.rootAuthority);rootModel(root,own,refs);
  const peer=await c.proof(root.sourceIndependentReview);
  assert(peer.schemaVersion===1&&peer.state==='INDEPENDENT_CLOCK_PACKAGE_LOADER_SOURCE_REVIEW_PASSED_V1'&&peer.sourceIndexSha256===own.sha256&&peer.sourceOnly===true&&peer.sourceReviewPassed===true&&peer.ownerActionsInvoked===false);
  const inventory=await c.json(refs.packageInventory);await c.tree(inventory.package);
  assert((await c.json(refs.packageJson)).version==='0.23.0');
  assert((await c.json(refs.jcoPackage)).version==='1.40.0');
  for(const row of refs.actualArtifacts)await c.file(row);equal(build.artifacts,refs.actualArtifacts);
  assert(physical(root.nativeMetadata.path)===physical(root.nativeEngine.path)+'.build.json');
  await c.file(root.nativeEngine);const nativeMetadata=await c.json(root.nativeMetadata);releaseMetadataModel(nativeMetadata,root.nativeEngine.sha256);
  assert(physical(process.execPath)===refs.node.path);await c.file(refs.node);
  for(let p=root.privateTemporaryRoot;;p=dirname(p)){assert(!(await lstat(p)).isSymbolicLink());if(dirname(p)===p)break;}
  const tmp=await lstat(root.privateTemporaryRoot);assert(tmp.isDirectory()&&!tmp.isSymbolicLink()&&(tmp.mode&0o777)===0o700&&process.env.TMPDIR===root.privateTemporaryRoot);
  equal(await readdir(root.privateTemporaryRoot),[],'Fresh caller-owned temporary directory required before package initialization');
  const tmpIdentity=[tmp.dev,tmp.ino];
  const recheck=async()=>{environmentModel({...process.env},process.execArgv,process.version,process.platform,process.arch);assert(process.env.TMPDIR===root.privateTemporaryRoot);for(let p=root.privateTemporaryRoot;;p=dirname(p)){assert(!(await lstat(p)).isSymbolicLink());if(dirname(p)===p)break;}const now=await lstat(root.privateTemporaryRoot);equal([now.dev,now.ino],tmpIdentity);assert(now.isDirectory()&&!now.isSymbolicLink()&&(now.mode&0o777)===0o700);await noExternalSearchRoots();await c.recheck();};
  try{
    await recheck();
    const capability=await import(pathToFileURL(refs.capabilityPolicy.path));
    const loaded=await import(pathToFileURL(refs.packageEntry.path));
    assert(typeof loaded.componentize==='function'&&loaded.version==='0.23.0');
    const require=createRequire(join(PACKAGE,'package.json'));
    assert(physical(require.resolve('@bytecodealliance/jco')).startsWith(PACKAGE+'/node_modules/'));
    await recheck();
    const provenance=frozen({schemaVersion:1,kind:'experimental-clock-package-v1',sourceIndex:own,toolsBuildReview:refs.toolsBuildReview,failedAdapterPhaseReview:refs.failedAdapterPhaseReview,metadataReview:refs.metadataReview,physicalPackage:{root:PACKAGE,inventory:refs.packageInventory,regularFiles:4889,aliases:21},actualArtifacts:refs.actualArtifacts,splicerCore:refs.splicerCore,explicitAdapter:refs.prunedAdapter,encodedTypePackage:refs.metadataPayload,oldAdapterPhasePassed:false,adapterPromoted:false,nativeArtifactAdmission:'Separate genuine caller-owned native admission required; this helper checks byte/sidecar/Release consistency only.',nodeImportCaching:'No ESM cache introspection or eviction; caller must use a new owned process with no earlier package/dependency imports. Current file hashes alone do not prove cached module freshness.'});
    return createSelected({root,refs,nativeMetadata,provenance,recheck,toolchain:{require},selectedInterfacePolicy:capability.selectedInterfacePolicy,auditSelectedInterfaces:capability.auditSelectedInterfaces,packageComponentize:loaded.componentize});
  }finally{await recheck();}
  }finally{await c.recheck();}
}

async function fingerprint(path){const s=await lstat(path),h=createHash('sha256');assert(s.isFile()&&!s.isSymbolicLink());for await(const chunk of createReadStream(path))h.update(chunk);return descriptor({path,sha256:h.digest('hex'),bytes:s.size});}
