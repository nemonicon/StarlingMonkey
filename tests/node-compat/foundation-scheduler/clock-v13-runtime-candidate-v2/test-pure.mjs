// Inert harness/grammar + synthetic/injected DATA only. No Jco API/shim/app import.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {artifactModel,phaseModel,htmlResult,mappedGlueModel,namespaceModel,scalarRunArguments} from './models.mjs';
import {capturedRun,observed,terminalModel} from './body.mjs';
import {parseScalarStringOutput} from './wave.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),refs=JSON.parse(await readFile(join(HERE,'references.json')));let checks=0;
const ck=(v,m)=>{assert(v,m);checks++;},deny=fn=>{assert.throws(fn);checks++;};
const proof=JSON.parse(await readFile(refs.actualArtifactReview.result.path)),contract=JSON.parse(await readFile(refs.actualArtifactContract.path));ck(artifactModel(proof,contract,refs),'Real completed b073 artifact DATA');
for(const[k,v]of [['componentSha256','0'.repeat(64)],['nativeSourceFiles',355],['selectedManifestCount',11],['fullMetadataFields',75],['generatedModuleImported',true],['ordinaryGuestExportsInvoked',true],['emittedImports',[]],['publicAbiFunctions',['run','extra']]]){const p=structuredClone(proof);p[k]=v;deny(()=>artifactModel(p,contract,refs));}
const own={path:join(HERE,'index.json'),sha256:'a'.repeat(64),bytes:1},template=JSON.parse(await readFile(join(HERE,'future-root-authority.template.json')));deny(()=>phaseModel(template,own,refs,'mapped-transpile'));
for(const phase of ['mapped-transpile','runtime-differential']){
 const map=phase==='mapped-transpile',r={...template,state:'ROOT_REVIEWED_CLOCK_V13_REACTDOM_DIFFERENTIAL_V2',phase,sourceIndex:own,outputRoot:map?refs.mappedOutputRoot:refs.runtimeOutputRoot,externalOutputRoot:(map?refs.mappedOutputRoot:refs.runtimeOutputRoot)+'-external-root',mappedTranspileAllowed:map,jcoCompilerWasmHelpersAllowed:map,generatedApplicationImportAllowed:!map,ordinaryRunAllowed:!map,stockWasmtimeAllowed:!map,nativeReadOnlyPreflightAllowed:true,standardShimWorkerThreadsAllowed:true,actualMappedOutputReview:map?null:{path:'/synthetic/never-issued.json'}};
 ck(phaseModel(r,own,refs,phase),'Pure future phase shape, no authority file');
 for(const[k,v]of [['componentSha256','0'.repeat(64)],['selectedInterfaces',[]],['standardShimWorkerThreadsAllowed',false],['ordinaryRunAllowed',map],['mappedTranspileAllowed',!map],['ownedWorkerDeadlineMs',1],['resourceSevenCaseProfileAccepted',true],['clockProfilePromotionAllowed',true],['adapterPromotionAllowed',true],['customHostServicesAllowed',true],['resetOrReuseAllowed',true]]){const x=structuredClone(r);x[k]=v;deny(()=>phaseModel(x,own,refs,phase));}
}
ck(htmlResult(refs.oracleValue,refs.oracleValue).bytes===45,'Actual retained whole Node oracle bytes');
for(const value of [refs.oracleValue+' ',refs.oracleValue.replace('Hello','Changed'),refs.oracleValue.replace('45','44'),'{}',Promise.resolve(refs.oracleValue),null])deny(()=>htmlResult(value,refs.oracleValue));
for(const args of [[],[0]]){if(args.length===0)ck(scalarRunArguments('run',args),'Actual run() scalar');else deny(()=>scalarRunArguments('run',args));}deny(()=>scalarRunArguments('validate',[]));
const {parse}=await import(pathToFileURL(refs.parser.path)),oldAst=parse(await readFile(refs.generatedFiles['clock_v13.js'].path,'utf8'),{ecmaVersion:'latest',sourceType:'module'});
// Synthetic AST mutation tests checker shape only. NEVER generated/executed mapping.
const ast=structuredClone(oldAst),imports=[['monotonicClock','wallClock'],['poll']].map((names,i)=>({type:'ImportDeclaration',source:{type:'Literal',value:i?refs.shimIoUrl:refs.shimClocksUrl},specifiers:names.map(name=>({type:'ImportSpecifier',imported:{type:'Identifier',name},local:{type:'Identifier',name:'synthetic_'+name}}))}));ast.body=[...imports,...ast.body.filter(n=>n.type!=='ImportDeclaration')];
ck(mappedGlueModel(ast,refs).inlineCoreModules.length===3,'Actual four core bytes with synthetic mapped-import checker shape only');
for(const edit of [a=>a.body[0].source.value='node:fs',a=>a.body[0].specifiers.pop(),a=>a.body[1].specifiers[0].imported.name='streams',a=>a.body.push({type:'ExportAllDeclaration',source:{type:'Literal',value:'other'}}),a=>a.body.unshift({type:'ImportDeclaration',source:{type:'Literal',value:'wasi:random/random'},specifiers:[]})]){const x=structuredClone(ast);edit(x);deny(()=>mappedGlueModel(x,refs));}
const wrong=structuredClone(refs);wrong.inlineCoreModules[0].sha256='0'.repeat(64);deny(()=>mappedGlueModel(ast,wrong));
const ns=()=>Object.assign(Object.create(null),{run(){},_util:{}});ck(namespaceModel(ns()),'Synthetic ESM namespace');let reads=0;const n=ns();Object.defineProperty(n,'then',{get(){reads++;throw Error('never read');}});deny(()=>namespaceModel(n));ck(reads===0,'Then name denied before getter');
for(const edit of [n=>n.extra=1,n=>n.run=x=>x,n=>n._util.x=1]){const n=ns();edit(n);deny(()=>namespaceModel(n));}
let hooks=0;const opaque=new Proxy({}, {get(){hooks++;throw Error('no get');},ownKeys(){hooks++;throw Error('no ownKeys');},getPrototypeOf(){hooks++;throw Error('no proto');}});ck(observed(opaque).opaque&&hooks===0,'Opaque unexpected value untouched');
for(const kind of ['return','nonstring','throw','write','throw-write']){
 const x={kind:'original'},y={kind:'writer'},seq={attempted:0,written:0},records=[];let failure;
 try{await capturedRun(()=>{if(kind.startsWith('throw'))throw x;return kind==='nonstring'?opaque:refs.oracleValue;},async(p,r)=>{if(kind==='write'||kind==='throw-write')throw y;records.push({p,r:JSON.parse(JSON.stringify(r))});},seq);}catch(error){failure=error;}
 ck(seq.attempted===1&&seq.written===(kind==='write'||kind==='throw-write'?0:1),'Honest raw attempts/writes');
 if(kind==='throw-write')ck(failure instanceof AggregateError&&failure.errors[0]===x&&failure.errors[1]===y,'Combined original throw and writer error both preserved');
 else if(kind==='throw')ck(failure===x,'Original throw identity after durable memory sink');else if(kind==='return')ck(failure===undefined&&records[0].r.observed.value===refs.oracleValue,'Whole string retained before any await of value');else ck(failure!==undefined,'Unexpected/capture failure refuses');
}
ck(hooks===0,'No opaque getters/proxy introspection across capture');
const wave='"'+refs.oracleValue.replaceAll('\\','\\\\').replaceAll('"','\\"')+'"\n';ck(parseScalarStringOutput({stdoutBytes:Buffer.from(wave),rawDurablyRetained:true})===refs.oracleValue,'Whole strict WAVE decode to same Node string');
for(const bytes of [Buffer.from(wave+'\n'),Buffer.from('1\n'),Buffer.from('"\\u0041"\n'),Buffer.from([0xff])])deny(()=>parseScalarStringOutput({stdoutBytes:bytes,rawDurablyRetained:true}));deny(()=>parseScalarStringOutput({stdoutBytes:Buffer.from(wave),rawDurablyRetained:false}));
const terminal={closed:true,status:0,signal:null,ownedGroupGone:true,terminalExitZeroObserved:true,spawnError:null,timedOut:false,externalSignal:null,outputLimitExceeded:false,errors:[],signals:[],signalCount:0};ck(terminalModel(terminal),'Pure terminal model');for(const[k,v]of [['status',1],['timedOut',true],['ownedGroupGone',false],['signals',[1]],['errors',[1]]])deny(()=>terminalModel({...terminal,[k]:v}));
console.log(JSON.stringify({schemaVersion:1,state:'CLOCK_V13_REACTDOM_PURE_SOURCE_MODELS_PASSED_V1',checks,syntheticMappedAstExecuted:false,jcoApiOrStandardShimImported:false,generatedApplicationModuleImported:false,nativePreflightOrWorkerOrWasmtimeCalled:false,applicationExportsInvoked:false}));
