// Future raw fixture bootstrap only. No componentizer, guest or output creation.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const run=promisify(execFile);
async function regular(path,sha){const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink());const bytes=await readFile(path);assert.equal(hash(bytes),sha,path);return bytes;}
export async function zlibBootstrapPreflight({variant='normal-off',reviewedPinsPath,reviewedPinsSha256,rootReviewPath,rootReviewSha256}={}){
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
 const pinsBytes=await regular(reviewedPinsPath,reviewedPinsSha256),reviewBytes=await regular(rootReviewPath,rootReviewSha256);
 const pins=JSON.parse(pinsBytes);assert.equal(pins.state,'ROOT_REVIEWED_ZLIB350_VALIDATION_BOOTSTRAP_V1');
 assert(pins.variants?.[variant]&&pins.variants[variant].reviewRequired===false,'Null/unreviewed pins refuse before loader/artifact reads');
 const review=JSON.parse(reviewBytes);assert.equal(review.reviewedPinsSha256,reviewedPinsSha256);
 const indexSha=review.proposalIndexSha256,indexPath=join(here,'../index.json');
 const index=JSON.parse(await regular(indexPath,indexSha));
 const privateRows=index.files.map(row=>Object.freeze({...row}));
 async function own(){for(const row of privateRows)await regular(join(here,'..',row.path),row.sha256);}
 await own();
 const args=[join(here,'bootstrap-classifier.py'),reviewedPinsPath,reviewedPinsSha256,rootReviewPath,rootReviewSha256,variant];
 const execute=async()=>{
  const child=await run('python3',args,{timeout:55000,maxBuffer:16*1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
  const result=JSON.parse(child.stdout);assert.equal(result.state,'ROOT_REVIEWED_ZLIB350_BUILD_VALIDATION_BOOTSTRAP_PASSED');
  assert.equal(result.operationalAdmission,false);assert.equal(result.variant,variant);return result;
 };
 const actual=await execute();
 const checks=actual.manifestPaths.map(path=>{const row=actual.metadata.sourceManifest.find(row=>row.path===path);assert(row);return Object.freeze({...row});});
 const selected=[];for(const row of checks)selected.push(JSON.parse(await regular(join(actual.sourceRoot,row.path),row.sha256)));
 async function recheck(){await regular(reviewedPinsPath,reviewedPinsSha256);await regular(rootReviewPath,rootReviewSha256);await regular(indexPath,indexSha);await own();await execute();}
 await recheck();
 return Object.freeze({enginePath:actual.enginePath,sourceRoot:actual.sourceRoot,metadata:actual.metadata,pin:actual.pin,variant,selectedManifests:selected,
  validationBootstrapOnly:true,operationalAdmission:false,recheck});
}
