// PURE/PARSER ONLY. Never import captured glue, a codec/provider, or run workers.
import {readFile,mkdir,writeFile,realpath} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {hash,need,observedCall} from './transport.mjs';
import {PARSER} from './parser-tuple.mjs';
import {validateGlueProgram,validateNamespace,scalarArguments,captureArtifactRows,validatePackageBytes} from './loading.mjs';
import {authorityModel,artifactModel,NODE,COMPONENT,TOOLING,GUEST,PUBLICATION,ARMS} from './admission.mjs';
import {jobModel} from './worker.mjs';
import {primaryJobs,matrixJobs,offJobs} from './plan.mjs';
import {requireCoverage} from './coverage.mjs';
import {parsePublicWit,parsePublicDts,checkTranspileMetadata} from './glue-policy.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),checks=[];
function check(ok,label){if(!ok)throw new Error('PURE check failed: '+label);checks.push(label);}
async function rejects(label,fn){let failed=false;try{await fn();}catch{failed=true;}check(failed,label);}
const tuple=path=>({path,sha256:'0'.repeat(64),bytes:1}),proof=()=>({index:tuple('/private/tmp/synthetic/index.json'),result:tuple('/private/tmp/synthetic/results.json')});
async function main(){
 check(process.version==='v22.14.0'&&await realpath(process.execPath)===NODE.path,'pinned Node for pure/parser checks');check(hash(await readFile(NODE.path))===NODE.sha256,'actual Node executable bytes verified');
 const parserBytes=await readFile(PARSER.path);check(hash(parserBytes)===PARSER.sha256&&parserBytes.length===PARSER.bytes,'exact standalone parser bytes before parser import');const {parse}=await import(pathToFileURL(PARSER.path).href);
 const origins=JSON.parse(await readFile(join(HERE,'observed-source/origins.json')));for(const row of origins.files){const raw=await readFile(join(HERE,'observed-source',row.copy));check(hash(raw)===row.sha256&&raw.length===row.bytes,'actual failed-v2 captured source bytes '+row.copy);}
 check(origins.parentAndWorkerOverallRawExitCode===1&&origins.acceptedArtifactProof===null,'captured partial is not accepted artifact proof');
 check(validatePackageBytes(Buffer.from('{\"type\":\"module\"}\n')),'cf31 SOURCE expected package literal DATA only; v2 failed before writing it');for(const text of['{\"type\":\"commonjs\"}\n','{\"type\":\"module\",\"imports\":{}}\n','{}','not-json'])await rejects('wrong or extra package classification '+text,()=>validatePackageBytes(Buffer.from(text)));
 const mutable={parentAuditedActualComponent:true,...Object.fromEntries(['component','glue','core','dts','wit','transpileMetadata','packageJson'].map(name=>[name,tuple('/private/tmp/synthetic/'+name)]))},captured=captureArtifactRows(mutable);mutable.glue.path='/private/tmp/replacement';mutable.glue.sha256='1'.repeat(64);check(captured.glue.path==='/private/tmp/synthetic/glue'&&captured.glue.sha256==='0'.repeat(64)&&Object.isFrozen(captured)&&Object.isFrozen(captured.glue),'genuine capture seam keeps private immutable descriptor primitives before awaits');
 await rejects('capture seam refuses missing parent-audited boundary',()=>captureArtifactRows({...mutable,parentAuditedActualComponent:false}));
 const src=await readFile(join(HERE,'observed-source/codec_cost.js'),'utf8'),dts=await readFile(join(HERE,'observed-source/codec_cost.d.ts'),'utf8'),wit=await readFile(join(HERE,'observed-source/emitted.wit'),'utf8'),metadata=JSON.parse(await readFile(join(HERE,'observed-source/transpile-metadata.json')));
 const checked=validateGlueProgram(parse(src,{ecmaVersion:'latest',sourceType:'module'}));check(checked.names.length===8&&checked.abiFunctionNames.length===7&&checked.glueHelpers[0].name==='_util','actual captured source parses as7scalar functions plus exact empty helper');
 check(checked.coreRelativePath==='codec_cost.core.wasm'&&checked.topLevelInitializationAwaited&&checked.nodeBuiltinLoader==='node:fs/promises','actual source-only TLA/relativecore/Node loader protocol');
 check(Object.keys(parsePublicWit(wit)).length===7&&Object.keys(parsePublicDts(dts)).length===7&&checkTranspileMetadata(metadata),'actual captured WIT/d.ts/Jco metadata data checks, not ABI execution');
 const helper=/export const _util = \{\s*\}/;check(helper.test(src),'exact observed helper construction located');
 const edits=[
  ['nonempty helper',s=>s.replace(helper,'export const _util = { x: 1 }')],
  ['getter helper',s=>s.replace(helper,'export const _util = { get x(){ return 1; } }')],
  ['spread helper',s=>s.replace(helper,'export const _util = { ...{} }')],
  ['prototype helper',s=>s.replace(helper,'export const _util = { __proto__: null }')],
  ['helper reference before export',s=>s.replace(helper,'_util.x = 1;\nexport const _util = {}')],
  ['unknown then export',s=>s.replace(helper,'export function then(){}\nexport const _util = {}')],
  ['aliased export',s=>s.replace('export { batch,','export { setup as then, batch,')],
  ['public function async',s=>s.replace('function setup(arg0)','async function setup(arg0)')],
  ['public wrong arity',s=>s.replace('function setup(arg0)','function setup(arg0,arg1)')],
  ['public function reassignment',s=>s.replace(helper,'setup = ()=>"bad";\nexport const _util = {}')],
  ['static JS dependency',s=>'import x from "node:os";\n'+s],
  ['extra dynamic JS dependency',s=>s.replace(helper,'import("node:path");\nexport const _util = {}')],
  ['wrong core path',s=>s.replace('./codec_cost.core.wasm','../escaped.wasm')],
  ['wrong TLA protocol',s=>s.replace('await $init;','await Promise.resolve();')],
  ['extra public default',s=>s+'\nexport default {};']
 ];
 for(const[label,edit]of edits){const changed=edit(src);check(changed!==src,'negative source mutation actual edit '+label);await rejects('parser-only rejects '+label,()=>validateGlueProgram(parse(changed,{ecmaVersion:'latest',sourceType:'module'})));}
 const fake=Object.fromEntries(['identity','setup','observe','batch','checkpoint','stage','validate'].map(name=>[name,function(){throw new Error('Synthetic function MUST NEVER BE CALLED');}]));fake._util={};check(validateNamespace(fake),'pure namespace shape model; no function calls');
 let gets=0;Object.defineProperty(fake,'then',{get(){gets++;throw Error('then getter');},configurable:true});await rejects('then name refused before value read',()=>validateNamespace(fake));check(gets===0,'then getter not read');delete fake.then;
 fake._util={x:1};await rejects('nonempty runtime helper refused',()=>validateNamespace(fake));fake._util=()=>{};await rejects('callable helper refused',()=>validateNamespace(fake));fake._util={};delete fake.observe;await rejects('missing ordinary function refused',()=>validateNamespace(fake));
 for(const[name,args]of[['identity',[]],['setup',[0]],['observe',[29]],['batch',[29,1]],['stage',['{}']],['validate',['{}']],['checkpoint',[]]]){scalarArguments(name,args);check(true,'exact supported scalar call model '+name);}
 for(const[name,args]of[['then',[]],['setup',['0']],['setup',[-0]],['setup',[NaN]],['setup',[1.5]],['setup',[30]],['batch',[0,7]],['batch',[30,1]],['stage',[{}]],['validate',['x'.repeat(2097153)]],['identity',[1]]])await rejects('no coercion/extra scope '+name+'/'+checks.length,()=>scalarArguments(name,args));
 for(const job of primaryJobs()){jobModel(job);check(true,'finite primary job model '+job.arm+'/'+job.kind+'/'+(job.caseId??'all'));}
 for(const job of[{kind:'retained-primary',arm:'native-on',rotations:2,caseIds:Array.from({length:30},(_,i)=>i)},{kind:'fresh-primary',arm:'fflate-on',caseId:0,rotations:3},{kind:'main-crossdecode',arm:'fflate-off',stream:{kind:'codec-cost-stage-v1',caseId:1,provider:'native-on'}},{kind:'off-guest-crossdecode',arm:'fflate-on',stream:{kind:'codec-cost-stage-v1',caseId:1,provider:'native-on'}},{kind:'main-crossdecode',arm:'native-on',stream:{kind:'codec-cost-stage-v1',caseId:1,provider:'fflate-off'}}])await rejects('wrong job domain '+job.kind+'/'+job.arm,()=>jobModel(job));
 const root=JSON.parse(await readFile(join(HERE,'root-authority.template.json')));await rejects('actual Root template NULL/false refuses',()=>authorityModel(root,'0'.repeat(64)));
 const shaped={...root,actionAllowed:true,correctnessSourceIndexSha256:'0'.repeat(64),ordinaryGuestCallsAllowed:true,nodeMatrixCodecCallsAllowed:true,sourceIndependentReview:proof(),oracle:tuple('/private/tmp/synthetic/oracle.json'),componentBuildAuthorities:Object.fromEntries(ARMS.map(arm=>[arm,tuple('/private/tmp/synthetic/'+arm+'.json')])),actualComponentReviews:Object.fromEntries(ARMS.map(arm=>[arm,proof()]))};check(authorityModel(shaped,'0'.repeat(64)),'synthetic authority SHAPE only; no file/proof/preflight validation');
 await rejects('old Root v1 state refused',()=>authorityModel({...shaped,state:'ROOT_REVIEWED_ZLIB_COST_JCO_CORRECTNESS_V1'},'0'.repeat(64)));await rejects('missing one actual arm review refuses',()=>authorityModel({...shaped,actualComponentReviews:{'native-on':proof(),'fflate-on':proof()}},'0'.repeat(64)));await rejects('timing authority refused',()=>authorityModel({...shaped,pilotOrTimingAllowed:true},'0'.repeat(64)));
 const base='/private/tmp/starling-node-compat/zlib-cost-component-v3-native-on/worker',r={schemaVersion:1,state:'INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1',verifiedPassed:true,arm:'native-on',componentSourceIndexSha256:COMPONENT,toolingSourceIndexSha256:TOOLING,guestSourceIndexSha256:GUEST,sourcePublicationIndexSha256:PUBLICATION,externalParentExitCode:0,rawWorkerExitCode:0,ownedGroupGone:true,generatedModuleImported:false,ordinaryGuestExportsInvoked:false,operationalAdmission:false,timingAllowed:false,generatedJsGluePolicy:'JCO7_SCALAR_FUNCTIONS_PLUS_EXACT_EMPTY_UTIL_V1',emittedImports:[],emittedAbi:parsePublicWit(wit)};
 for(const[name,path]of Object.entries({component:'codec-cost.component.wasm',glue:'transpiled/codec_cost.js',core:'transpiled/codec_cost.core.wasm',dts:'transpiled/codec_cost.d.ts',wit:'emitted.wit',transpileMetadata:'transpile-metadata.json',packageJson:'transpiled/package.json',workerIndex:'index.json',workerCompletion:'completion.json',workerResult:'results.json'}))r[name]=tuple(base+'/'+path);
 for(const name of['code','nativeEngine','metadata','actualBuildAuthority','externalParentTerminal','ownedWorkerTerminal','parentResult'])r[name]=tuple('/private/tmp/synthetic/'+name+'.json');check(artifactModel(r,'native-on'),'synthetic artifact SHAPE only; not actual indexed proof');
 for(const changed of[{...r,externalParentExitCode:1},{...r,rawWorkerExitCode:1},{...r,ownedGroupGone:false},{...r,emittedImports:['wasi:random/random@0.2.10']},{...r,emittedAbi:{...r.emittedAbi,setup:'(u32) -> s32'}},{...r,component:{...r.component,path:r.component.path.replace('component-v3','component-v2')}},{...r,generatedModuleImported:true},{...r,componentSourceIndexSha256:'e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa'}])await rejects('actual-only artifact model refusal '+checks.length,()=>artifactModel(changed,'native-on'));
 let trap=0;const bad=Object.defineProperty({},'then',{get(){trap++;throw Error('then');}}),raw=[];await rejects('raw unexpected thenable never assimilated',()=>observedCall({invoke:()=>bad,write:async(name,v)=>{raw.push({name,v});return{name};},name:'carrier',exportName:'observe',args:[0]}));check(trap===0&&raw.at(-1).v.returned.kind==='opaque','typed raw persisted before failure without getter');
 const primary=primaryJobs().flatMap(job=>job.kind==='retained-primary'?Array.from({length:3},(_,rotation)=>job.caseIds.map(caseId=>({kind:job.kind,arm:job.arm,caseId,rotation}))).flat():[{...job,rotation:0}]);const coverage={primary,mainEdges:matrixJobs(),offEncodings:offJobs().encoding,offNodeEdges:offJobs().node,offGuestEdges:offJobs().guest};check(requireCoverage(coverage).mainCrossdecodeEdges===135,'unchanged exact matrix coverage model');for(const name of Object.keys(coverage))await rejects('no omitted coverage '+name,()=>requireCoverage({...coverage,[name]:coverage[name].slice(1)}));
 return{schemaVersion:1,state:'PURE_PARSER_LOADING_AND_CORRECTNESS_MODELS_PASSED_V2',checks:checks.length,labels:checks,parserOnlyCapturedFailedV2Source:true,actualSourceEvaluated:false,syntheticModelsNotActualAuthorityOrArtifacts:true,codecOrProviderCalls:0,ordinaryGuestCalls:0,workersSpawned:0,positivePreflightsInvoked:0,actualLoaderInvoked:false,timing:false};
}
let result;try{result=await main();}catch(error){result={schemaVersion:1,state:'PURE_CHECKS_FAILED',checks:checks.length,labels:checks,error:{type:typeof error,message:error.message,stack:error.stack},actualSourceEvaluated:false,codecOrProviderCalls:0};process.exitCode=1;}
const output=process.env.COST_JCO_LOADING_PURE_OUTPUT;need(output&&resolve(output)===output,'Fresh explicit absolute pure output required');await mkdir(output,{mode:0o700});await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx',mode:0o600});process.stdout.write(JSON.stringify({state:result.state,checks:result.checks,output})+'\n');
