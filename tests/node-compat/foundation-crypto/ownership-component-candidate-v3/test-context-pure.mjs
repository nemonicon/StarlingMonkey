// Actual JSON/context DATA only. No captureConfiguredBootstrap/helper import or action.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {executableContextModel,assertReturnedContexts,bootstrapEnvironment} from './bootstrap-context.mjs';
import {authorityModel} from './guard.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),OLD=join(HERE,'../ownership-component-candidate-v1');let checks=0;const ck=(v,m)=>{assert(v,m);checks++;};
async function data(row){const raw=await readFile(row.path);ck(raw.length===row.bytes&&createHash('sha256').update(raw).digest('hex')===row.sha256,'exact actual data '+row.path);return JSON.parse(raw);}
const c=JSON.parse(await readFile(join(HERE,'bootstrap-context.json'))),contract=await data(c.actualContract),frame=await data(c.actualFrame),p=JSON.parse(await readFile(join(OLD,'prerequisites.json')));
ck(executableContextModel(c,contract,p),'genuine configured context accepted by pure model');ck(assertReturnedContexts(frame,contract,frame),'actual retained full genuine frame accepted unchanged');
for(const edited of [
 {...c,configuredBootstrapEntry:p.bootstrapEntry},
 {...c,configuredSourceRoot:dirname(dirname(dirname(dirname(dirname(p.bootstrapEntry.path)))))},
 {...c,configuredSourceIndex:p.nativeSourceIndex},
 {...c,configuredToolDependencies:767},
 {...c,sourceRoot:c.configuredSourceRoot},
]){assert.throws(()=>executableContextModel(edited,contract,p));checks++;}
for(const edited of [{...contract,readOnlyBootstrapOnly:false},{...contract,positiveKeyOperationsInvoked:true},{...contract,otherVariantsNull:false},{...contract,configuredSourceRoot:'/Users/dan/dev/StarlingMonkey'}]){assert.throws(()=>executableContextModel(c,edited,p));checks++;}
for(const edited of [{...frame,configuredSourceRoot:'/Users/dan/dev/StarlingMonkey'},{...frame,sourceRoot:c.configuredSourceRoot},{...frame,enginePath:frame.enginePath.replace('/tmp/','/private/tmp/')},{...frame,metadata:{...frame.metadata,sourceManifest:frame.metadata.sourceManifest.slice(0,350)}},{...frame,selectedManifests:frame.selectedManifests.slice(1)},{...frame,pin:{...frame.pin,reviewRequired:true}}]){assert.throws(()=>assertReturnedContexts(edited,contract,frame));checks++;}
const template=JSON.parse(await readFile(join(HERE,'future-component-authority.template.json')));assert.throws(()=>authorityModel(template,'a'.repeat(64)));checks++;ck(template.componentBuildAllowed===false&&template.componentSourceIndexSha256===null,'new Root source/action remainsNULL');
ck(bootstrapEnvironment({}),'ordinary empty Python override domain');for(const key of ['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE']){assert.throws(()=>bootstrapEnvironment({[key]:'/unreviewed'}));checks++;}
console.log(JSON.stringify({schemaVersion:1,state:'PURE_ACTUAL_BOOTSTRAP_CONTEXT_BOUNDARY_CHECKS_PASSED',checks,positiveValuesAreRetainedJsonDataOnly:true,originalPrepEntryRejectedDespiteEqualSourceHash:true,genuineBootstrapInvoked:false,componentizerInvoked:false,keyOrCryptoInvoked:false,ownerActionsInvoked:false}));
