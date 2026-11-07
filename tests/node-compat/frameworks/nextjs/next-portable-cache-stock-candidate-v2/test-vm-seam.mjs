// Root-owned future Node22 seam test. Never imported by the app actor.
// Root stages the two exact tiny fixtures and runs this once under original0af.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,realpath,writeFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHostModuleRequire as createOldRequire} from '../http-bridge-candidate-v1/module-host-provider.mjs';
import {createHostModuleRequire as createNewRequire} from './module-host-provider.mjs';

assert.equal(process.version,'v22.14.0');
assert.deepEqual(process.execArgv,[]);
assert.equal(process.env.NODE_OPTIONS,undefined);
assert.equal(process.argv.length,4,'Explicit Root-staged fixture directory and fresh result path required');
const here=dirname(fileURLToPath(import.meta.url));
const fixtures=resolve(process.argv[2]),output=resolve(process.argv[3]);
assert.equal(fixtures,process.argv[2]);assert.equal(output,process.argv[3]);
assert(fixtures.startsWith('/private/tmp/starling-node-compat/'));
assert(output.startsWith('/private/tmp/starling-node-compat/'));
assert.equal(await realpath(fixtures),fixtures);assert.equal(await realpath(dirname(output)),dirname(output));
const result={schemaVersion:1,state:'ROOT_NODE_VM_SEAM_UNREVIEWED_V2',node:process.version,passed:false,
 oldExpectedError:null,newDefaultClass:null,errors:[],fixtures:[],noHttpNextBrowserOrGuest:true};
const errorData=e=>({name:e?.name??null,message:e?.message??String(e),code:e?.code??null,stack:e?.stack??null});
const digest=raw=>createHash('sha256').update(raw).digest('hex');
try {
 for(const name of ['driver.cjs','target.cjs']) {
  const path=join(fixtures,name),source=join(here,'vm-fixtures',name),s=await lstat(path);
  assert(s.isFile()&&!s.isSymbolicLink());assert.equal(s.nlink,1);assert.equal(await realpath(path),path);
  const raw=await readFile(path),original=await readFile(source);assert.deepEqual(raw,original);
  result.fixtures.push({path,sha256:digest(raw),bytes:raw.length,source});
 }
 const driverPath=join(fixtures,'driver.cjs'),targetPath=join(fixtures,'target.cjs');
 const oldObservations={},newObservations={};
 const oldRequire=createOldRequire(driverPath,oldObservations);
 const oldDriver=oldRequire(driverPath);
 try { await oldDriver.load('./target.cjs'); }
 catch(error) { result.oldExpectedError=errorData(error); }
 assert.equal(result.oldExpectedError?.code,'ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING');
 const newRequire=createNewRequire(driverPath,newObservations);
 const driver=newRequire(driverPath);
 const first=await driver.load('./target.cjs');
 const second=await driver.load('./target.cjs');
 const nodeRequire=createRequire(driverPath),ordinary=nodeRequire(targetPath);
 assert.equal(typeof first.default,'function');assert.equal(first.default,ordinary);
 assert.equal(first,second);assert.equal(new first.default(7).result(),'main-loader:7');
 const candidateExport=newRequire(targetPath);
 assert.notEqual(candidateExport,first.default,'Default Node import cache is separate from candidate synchronous require cache');
 result.newDefaultClass={defaultSameAsRealNodeRequire:first.default===ordinary,
  repeatedNamespaceIdentity:first===second,constructedValue:new first.default(7).result(),
  candidateSynchronousRequireIsSeparate:candidateExport!==first.default};
 result.oldProviderConfiguration=oldObservations;
 result.newProviderConfiguration=newObservations;
 result.oldSnapshot=oldObservations.snapshot();result.newSnapshot=newObservations.snapshot();
 result.passed=true;
} catch(error) { result.errors.push(errorData(error)); }
finally {
 await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx',mode:0o600});
}
console.log(JSON.stringify({state:result.state,passed:result.passed,errors:result.errors}));
process.exitCode=result.passed?0:1;
