// Actual API caller, dormant until separately issued Root authority. INIT only.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,readdir,lstat,readlink,realpath,mkdir} from 'node:fs/promises';
import {resolve,join,dirname,relative,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
async function checked(r){
  assert.equal(resolve(r.path),r.path);let path=r.path;
  while(true){assert(!(await lstat(path)).isSymbolicLink(),path);if(dirname(path)===path)break;path=dirname(path);}
  const bytes=await readFile(r.path);assert.equal(bytes.length,r.bytes);assert.equal(digest(bytes),r.sha256);return bytes;
}
async function files(root){
  const regular=[],links=[];
  async function walk(dir){for(const name of await readdir(dir)){const path=join(dir,name),s=await lstat(path);if(s.isSymbolicLink())links.push(relative(root,path));else if(s.isDirectory())await walk(path);else{assert(s.isFile());regular.push(relative(root,path));}}}
  await walk(root);return {regular:regular.sort(),links:links.sort()};
}
async function family(r){
  const index=JSON.parse(await checked(r)),root=dirname(r.path),actual=await files(root);
  assert.deepEqual(actual.links,[]);assert.deepEqual(actual.regular.filter(p=>p!=='index.json'),index.files.map(r=>r.path).sort());
  for(const item of index.files)await checked({...item,path:join(root,item.path)});
}
async function main(){
  assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert.equal(process.env.NODE_OPTIONS,undefined);
  assert.equal(process.argv.length,5);
  const [authorityPath,authoritySHA,planSHA]=process.argv.slice(2);
  const authorityBytes=await readFile(authorityPath);assert.equal(digest(authorityBytes),authoritySHA);
  const a=JSON.parse(authorityBytes),planBytes=await readFile(join(HERE,'plan.json'));assert.equal(digest(planBytes),planSHA);
  const p=JSON.parse(planBytes);assert.equal(a.state,'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2');assert.equal(a.schemaVersion,1);
  assert.equal(a.componentizeInitAllowed,true);assert.equal(a.ordinaryExportsAllowed,false);assert.equal(a.httpServingAllowed,false);
  assert(Object.hasOwn(p.entries,a.entryMode));assert.equal(a.outputRoot,p.outputPrefix+'-'+a.entryMode+'-'+a.runId);
  assert.match(a.runId,/^[a-z0-9][a-z0-9-]{0,48}$/);assert.equal(process.env.TMPDIR,join(a.outputRoot,'tmp'));
  assert.equal(a.callerIndex.path,join(HERE,'index.json'));
  const metadata=JSON.parse(await checked(a.nativeMetadata));assert(metadata&&typeof metadata==='object'&&!Array.isArray(metadata));
  assert(Object.keys(a.metadataExpectedFixedValues).length>0);
  for(const [key,value]of Object.entries(a.metadataExpectedFixedValues))assert.deepEqual(metadata[key],value,key);
  assert(a.engineBuildEvidence.length>0&&a.newSourceEvidence.length>0&&a.nativeBuildReviewedForConstruction===true);
  const inventory=JSON.parse(await checked(p.packageInventory)).package;
  assert.equal(inventory.root,p.packageRoot);assert.equal(inventory.files.length,4889);assert.equal(inventory.links.length,21);
  async function recheck(){
    assert.equal(digest(await readFile(authorityPath)),authoritySHA);assert.equal(digest(await readFile(join(HERE,'plan.json'))),planSHA);
    assert.equal(process.env.TMPDIR,join(a.outputRoot,'tmp'));
    await family(a.callerIndex);await family(p.inputSourceIndex);
    await family(p.priorCallerSourceIndex);
    for(const r of [p.priorFailedResult,p.priorFailedTerminal,p.priorFailedStderr])await checked(r);
    for(const r of Object.values(p.pins).concat([p.packageInventory,a.engine,a.nativeMetadata],a.engineBuildEvidence,a.newSourceEvidence))await checked(r);
    const actual=await files(p.packageRoot);
    assert.deepEqual(actual.regular,inventory.files.map(r=>r.relativePath).sort());assert.deepEqual(actual.links,inventory.links.map(r=>r.path).sort());
    for(const r of inventory.files){await checked(r);assert.equal((await lstat(r.path)).mode&0o777,r.mode);}
    for(const r of inventory.links){const path=join(p.packageRoot,r.path);assert.equal(await readlink(path),r.target);assert.equal(await realpath(path),r.resolvedPath);assert(r.resolvedPath.startsWith(p.packageRoot+sep));}
  }
  await recheck(); // Complete authentication BEFORE first custom/constructor import.
  const {writeWhole,captureComponentReturn,typedOwnGraph}=await import('./capture.mjs');
  const output=join(a.outputRoot,'api-return');await mkdir(output,{mode:0o700});
  let captured=null,error,finalError,failed=false,finalFailed=false,toolFilesystem=null,mountConfigured=false;
  try{
    // Retain genuine current metadata verbatim; this is no old83 frame adapter.
    await writeWhole(join(output,'native-metadata-input.json'),await checked(a.nativeMetadata));
    const requested={engine:a.engine.path,preview2Adapter:p.pins.adapter.path,witPath:p.witDirectory,worldName:p.worldName,
      disableFeatures:['fetch-event'],enableFeatures:[],enableAot:false,env:{},
      debug:{bindings:false,binary:false,wizerLogging:false},debugBindings:false,debugBuild:false,enableWizerLogging:false};
    await writeWhole(join(output,'requested-options.json'),JSON.stringify(requested,null,2)+'\n');
    // Official tool-side filesystem configuration, before importing the splicer.
    // This fresh Node maps only the authenticated WIT directory, not / or /app.
    toolFilesystem=await import(pathToFileURL(p.pins.toolFilesystemModule.path).href);
    assert.equal(typeof toolFilesystem._getPreopens,'function');assert.equal(typeof toolFilesystem._setPreopens,'function');
    const initialNames=toolFilesystem._getPreopens().map(([,name])=>name);
    await writeWhole(join(output,'tool-preopens-initial.json'),JSON.stringify({count:initialNames.length,virtualNames:initialNames},null,2)+'\n');
    assert.deepEqual(initialNames,[],'Fresh tool parser preopens must be empty');
    toolFilesystem._setPreopens({[p.witDirectory]:p.witDirectory});mountConfigured=true;
    const configuredNames=toolFilesystem._getPreopens().map(([,name])=>name);
    await writeWhole(join(output,'tool-preopens-configured.json'),JSON.stringify({count:configuredNames.length,virtualNames:configuredNames,
      hostMappings:{[p.witDirectory]:p.witDirectory},module:p.pins.toolFilesystemModule,scope:'Construction tool parser only; no application or guest host mount'},null,2)+'\n');
    assert.deepEqual(configuredNames,[p.witDirectory]);
    const {componentize}=await import(pathToFileURL(p.pins.packageEntry.path).href);
    assert.equal(typeof componentize,'function');
    const returned=await componentize((await checked(p.entries[a.entryMode])).toString('utf8'),requested);
    captured=await captureComponentReturn(returned,output);
    await writeWhole(join(output,'node-result.json'),JSON.stringify({schemaVersion:1,state:'NEXT_NATIVE_COMPONENT_API_RETURN_CAPTURED_UNREVIEWED_V1',
      entryMode:a.entryMode,inputEntry:p.entries[a.entryMode],inputSourceIndex:p.inputSourceIndex,
      artifacts:captured,engine:a.engine,nativeMetadata:a.nativeMetadata,ordinaryExportsInvoked:false},null,2)+'\n');
  }catch(caught){
    failed=true;error=caught;
    try{await writeWhole(join(output,'failure.json'),JSON.stringify({schemaVersion:1,state:'NEXT_NATIVE_COMPONENT_API_FAILURE_PRESERVED_V1',
      thrown:typedOwnGraph(caught),captured,returnedComponentMustNotBeInferred:true},null,2)+'\n');}catch(captureError){console.error('Failure retention failed:',captureError);}
  }finally{
    try{
      if(toolFilesystem){
        const finalNames=toolFilesystem._getPreopens().map(([,name])=>name);
        await writeWhole(join(output,'tool-preopens-final.json'),JSON.stringify({count:finalNames.length,virtualNames:finalNames,mountConfigured},null,2)+'\n');
        assert.deepEqual(finalNames,mountConfigured?[p.witDirectory]:[]);
      }
      await recheck();
    }catch(caught){finalFailed=true;finalError=caught;console.error('Final input protection failed:',caught);}
  }
  if(failed)throw error;
  if(finalFailed)throw finalError;
  console.log(JSON.stringify({state:'NEXT_NATIVE_COMPONENT_API_CAPTURE_COMPLETE_V1',entryMode:a.entryMode,artifacts:captured}));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
