// Source/retained DATA and read-only world guard only. No actor or resource IO.
import assert from 'node:assert/strict';
import {readFile,readdir,lstat,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,relative} from 'node:path';
import {compileFunction} from 'node:vm';
const code=await readFile(new URL('./deploy.mjs',import.meta.url),'utf8');
const old=await readFile(new URL('../wasmcloud-cold-candidate-v2/deploy.mjs',import.meta.url),'utf8');
const plan=JSON.parse(await readFile(new URL('./plan.json',import.meta.url),'utf8'));
const refs=JSON.parse(await readFile(new URL('./test-data-inputs.json',import.meta.url),'utf8')).inputs;
const construction=JSON.parse(await readFile(refs.constructionResult.path,'utf8'));
const ctorPlan=JSON.parse(await readFile(construction.plan.path,'utf8'));
const row=async path=>{const bytes=await readFile(path);return {path,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length};};
assert.deepEqual(await row(construction.plan.path),construction.plan);
assert.deepEqual(ctorPlan.inputSourceIndex,construction.artifacts.inputSourceIndex);
assert.notDeepEqual(plan.worldFamily.sourceIndex,ctorPlan.inputSourceIndex);
assert.deepEqual(ctorPlan.worldSourceIndex,plan.worldFamily.sourceIndex);
let checks=0;
function guards(source,p,c,a){
 const from=source.indexOf('async function row(path){'),to=source.indexOf('\nconst authpath=',from);
 const start=source.indexOf('async function witBookend(){'),end=source.indexOf('\nawait witBookend();',start);
 assert(from>=0&&to>from&&start>=0&&end>start);
 // Actual authenticated function text, with real read-only filesystem inputs.
 return compileFunction(source.slice(from,to)+'\nlet worldIdentityBefore;\n'+source.slice(start,end)+'\nreturn witBookend;',
  ['plan','ctorPlan','a','assert','createHash','createReadStream','readFile','readdir','lstat','realpath','dirname','join','resolve','relative','read'])(
  p,c,a,assert,createHash,createReadStream,readFile,readdir,lstat,realpath,dirname,join,resolve,relative,
  async path=>JSON.parse(await readFile(path,'utf8')));
}
const a={inputSourceIndex:ctorPlan.inputSourceIndex};
await assert.rejects(guards(old,plan,ctorPlan,a));checks++;
const actual=guards(code,plan,ctorPlan,a);await actual();await actual();checks+=2;
for(const [name,change] of [
 ['missing constructor world',c=>delete c.worldSourceIndex],
 ['entry family substituted as world',c=>c.worldSourceIndex=c.inputSourceIndex],
 ['wrong world digest',c=>c.worldSourceIndex.sha256='0'.repeat(64)],
 ['wrong world size',c=>c.worldSourceIndex.bytes++],
 ['wrong physical WIT directory',c=>c.witDirectory='/pure-data/wrong'],
]){
 const c=structuredClone(ctorPlan);change(c);await assert.rejects(guards(code,plan,c,a),undefined,name);checks++;
}
const wrongDirs=structuredClone(plan);wrongDirs.worldFamily.directories.push('unexpected');
await assert.rejects(guards(code,wrongDirs,ctorPlan,a));checks++;
const wrongFixed=structuredClone(plan);wrongFixed.fixedWit.files[0].sha256='0'.repeat(64);
await assert.rejects(guards(code,wrongFixed,ctorPlan,a));checks++;
console.log(JSON.stringify({sourceOnly:true,worldChecks:checks,actualWorldGuardTextUsed:true,
 wholeCurrentWorldBeforeAndFinalReadOnly:true,oldEntryFamilyEqualityRefused:true,
 externalConstructorWorldAccepted:true,actualActorsOrCliOrNetworkOrCopiesOrGuestInvoked:false}));
