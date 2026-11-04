// Extract pure finite parsers/denial functions; no policy loader or engine reads.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync(new URL('./proposed/tests/node-compat/stream-consumers-admission.mjs',import.meta.url),'utf8');
const checks=[];const check=(name,fn)=>{fn();checks.push(name);};
const segment=(start,end)=>source.slice(source.indexOf(start),source.indexOf(end,source.indexOf(start)));
const functions=segment('function words(','function compiled(')+segment('function hinted(','export function validateStreamConsumersSourceModel(')+segment('export function validateStreamConsumersSourceAdmission(','export function validateStreamConsumersBuildSourceAdmission(').replace('export ','');
const scope={assert,RECIPE_SHA:/const RECIPE_SHA='([a-f0-9]{64})'/.exec(source)[1]};vm.createContext(scope);vm.runInContext(functions+'\nthis.api={words,macro,release,hinted,admit:validateStreamConsumersSourceAdmission};',scope);
const {words,macro,release,hinted,admit}=scope.api;
check('historicalUnhintedNoNewFlagFabricated',()=>assert.equal(admit({buildRecipeSha256:'4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2'}),null));
for(const metadata of[{buildRecipeSha256:scope.RECIPE_SHA},{streamConsumersEnabled:false},{streamConsumersEnabled:true},{streamConsumersPolicy:{}},{streamConsumersSourcePolicy:{}},{requestedCMakeOptions:{NODE_COMPAT_STREAM_CONSUMERS:'OFF'}},{observedCMakeOptions:{NODE_COMPAT_STREAM_CONSUMERS:'ON'}},{sourceManifest:[{path:'builtins/node-compat/stream-consumers/facade.mjs'}]}])check('operationalClosed'+checks.length,()=>{assert.equal(hinted(metadata),true);assert.throws(()=>admit(metadata),/operational admission CLOSED/);});
for(const malformed of['clang -D X=1 -c a.cpp','clang -U X -c a.cpp','clang -c a.cpp && echo nope','clang -c a.cpp; echo nope',"clang -c 'a.cpp",'clang -fsyntax-only -c a.cpp','clang -c a.cpp -c b.cpp'])check('malformedCapturedCommand'+checks.length,()=>assert.throws(()=>words(malformed)));
check('pureJoinedMacroPositive',()=>{const tokens=words('clang -O3 -DNDEBUG -DNODE_COMPAT_STREAM_CONSUMERS=1 -c a.cpp');macro(tokens,'NODE_COMPAT_STREAM_CONSUMERS',true);release(tokens);});
for(const command of['clang -O2 -DNDEBUG -c a.cpp','clang -O3 -DDEBUG -DNDEBUG -c a.cpp','clang -O3 -DNDEBUG -DNODE_COMPAT_OOM_TESTING=1 -c a.cpp'])check('releaseRefusal'+checks.length,()=>assert.throws(()=>release(words(command))));
check('buildSourceRejectsSyntheticBeforeModel',()=>assert(source.includes("assert(metadata.syntheticMetadataOnly===undefined||metadata.syntheticMetadataOnly===false,'Synthetic source models never enter production admission');")));
console.log(JSON.stringify({schemaVersion:1,state:'PURE_ADMISSION_DENIAL_CHECKS_PASSED',checks,passed:checks.length,syntheticMetadataOnly:true,engineOrFactoryOpened:false}));
