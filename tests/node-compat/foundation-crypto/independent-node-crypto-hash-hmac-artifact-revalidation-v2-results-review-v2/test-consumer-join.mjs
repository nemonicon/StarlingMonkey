// Host-only DATA test. The operational entry module is never imported.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,readdir,mkdtemp,writeFile,rm,realpath} from 'node:fs/promises';
import {dirname,join,isAbsolute,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const K=dirname(HERE),CALLER=join(K,'node-crypto-hash-hmac-component-diagnostic-candidate-v1');
const NODE={path:'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024};
const ACORN={path:'/private/tmp/starling-node-compat/import-abi-clock-io-v1-package/node_modules/acorn/dist/acorn.mjs',sha256:'1cbcbf252a5800e496dc505c706f309a9dd4e1789392e12963c77ae9497ff6f7',bytes:232769};
const hash=b=>createHash('sha256').update(b).digest('hex');
async function row(path){const s=await lstat(path);assert(s.isFile()&&!s.isSymbolicLink());const b=await readFile(path),z=await lstat(path);assert.deepEqual([s.dev,s.ino,s.mode,s.nlink,s.size,s.mtimeMs,s.ctimeMs],[z.dev,z.ino,z.mode,z.nlink,z.size,z.mtimeMs,z.ctimeMs]);return{path,sha256:hash(b),bytes:b.length};}
async function verify(r){assert.deepEqual(await row(r.path),r);return readFile(r.path,'utf8');}
async function ownFamily(root,expected){const ix=await row(join(root,'index.json'));assert.equal(ix.sha256,expected);const files=JSON.parse(await verify(ix)).files,names=new Set(['index.json']);for(const r of files){assert(!isAbsolute(r.path)&&r.path.split('/').every(x=>x&&x!=='.'&&x!=='..')&&!names.has(r.path));names.add(r.path);await verify({...r,path:join(root,r.path)});}const actual=[];async function walk(p,prefix=''){for(const n of await readdir(p)){const q=join(p,n),s=await lstat(q);assert(!s.isSymbolicLink());if(s.isDirectory())await walk(q,prefix+n+'/');else{assert(s.isFile());actual.push(prefix+n);}}}await walk(root);assert.deepEqual(actual.sort(),[...names].sort());return ix;}
const errorData=e=>({name:e?.name??null,code:e?.code??null,message:String(e?.message??e)});
async function refused(f){try{await f();}catch(e){const d=errorData(e);assert.equal(d.code,'ERR_ASSERTION');assert(d.message.includes('same(p.coverage,k.requiredCoverage)'),d.message);return d;}throw Error('Expected actual requiredCoverage refusal');}
async function pair(root){return{index:await row(join(root,'index.json')),result:await row(join(root,'results.json'))};}
async function main(){
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert.equal(await realpath(process.execPath),NODE.path);await verify(NODE);
 for(const key of ['NODE_OPTIONS','NODE_PATH','LD_PRELOAD','LD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK'])assert(!process.env[key]);assert(!Object.keys(process.env).some(x=>x.startsWith('DYLD_')));
 const consumerIndex=await ownFamily(CALLER,'7fb5371b64ac41cdaa402c601cd45f758e9d41493988a3085b2d5366b35e4371');
 const consumerEntry=await row(join(CALLER,'entry.mjs'));assert.equal(consumerEntry.sha256,'b4b53df1a0df7a4142ee6e4c9a63d261dac7e8dad89e74da8c6dfde26df7e467');
 await verify(ACORN);const {parse}=await import(pathToFileURL(ACORN.path));
 const text=await verify(consumerEntry),ast=parse(text,{sourceType:'module',ecmaVersion:'latest'}),wanted=new Set(['descriptor','physical','fingerprint','treeDigest','Capture','hash','selectedTmp']),segments=[];
 for(const n of ast.body){if(n.type==='ImportDeclaration'){assert(n.source.value.startsWith('node:'));segments.push(text.slice(n.start,n.end));continue;}const id=n.id?.name??(n.type==='VariableDeclaration'&&n.declarations.length===1?n.declarations[0].id.name:null);if(wanted.has(id)){segments.push(text.slice(n.start,n.end));wanted.delete(id);}}
 assert.equal(wanted.size,0);assert.equal(segments.length,14);
 const extracted=segments.join('\n')+'\nexport {Capture};\n';parse(extracted,{sourceType:'module',ecmaVersion:'latest'});
 const {Capture}=await import('data:text/javascript;base64,'+Buffer.from(extracted).toString('base64'));
 const oldRoot=join(K,'independent-node-crypto-hash-hmac-artifact-revalidation-v2-results-review-v1'),oldPair=await pair(oldRoot),oldContract=await row(join(oldRoot,'result-contract.json'));
 assert.equal(oldPair.index.sha256,'61250674d78fb5d162e7dee5f4c7db6676d69f0fd2f85bd2350f64e97df9b5fc');
 const oldRefusal=await refused(()=>new Capture().proof(oldPair,oldContract));
 const newPair=await pair(HERE),newContract=await row(join(HERE,'result-contract.json')),c=new Capture();
 const p=await c.proof(newPair,newContract);assert.equal(p.publicationVersion,2);await c.recheck();
 const scratch=await mkdtemp('/private/tmp/starling-node-compat/hash357-coverage-negative-');let negativeRefusal;
 try{const bad=structuredClone(p);bad.coverage.currentLedgerFiles--;await writeFile(join(scratch,'results.json'),JSON.stringify(bad));await writeFile(join(scratch,'result-contract.json'),await readFile(newContract.path));const files=[];for(const name of ['result-contract.json','results.json'])files.push({...await row(join(scratch,name)),path:name});await writeFile(join(scratch,'index.json'),JSON.stringify({schemaVersion:1,files}));const scratchPair=await pair(scratch),scratchContract=await row(join(scratch,'result-contract.json'));negativeRefusal=await refused(()=>new Capture().proof(scratchPair,scratchContract));
 }finally{await rm(scratch,{recursive:true});}
 // Scratch descriptors are evaluated before invoking the genuine proof method.
 console.log(JSON.stringify({schemaVersion:1,state:'ACTUAL_CAPTURE_PROOF_DATA_JOIN_CHECK_PASSED',consumerIndex,consumerEntry,node:NODE,acorn:ACORN,extractedSegmentCount:segments.length,extractedSourceSha256:hash(extracted),extraction:'Exact AST-selected stdlib imports and read-only declarations; excludes authorize/main and operational module import.',oldPair,oldContract,newPair,newContract,oldMissingCoverageRefused:true,oldRefusal,newClosedPairPassed:true,newPrivateRecheckPassed:true,consistentCoverageMutationRefused:true,negativeRefusal,actualRevalidationOrHelperRerun:false,guestEngineCryptoActionsInvoked:false}));
}
main().catch(e=>{console.error(JSON.stringify(errorData(e)));process.exitCode=1;});
