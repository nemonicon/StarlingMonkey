// Pure models/report DATA only. No source guard, server, request or process calls.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {SIX,EXPORTS,inheritedHomePaths,readinessRetryAllowed,loopback,signalGroup,washConfig,effectiveWash,gracefulServer,rootModel,interfaceModel,componentProofModel} from './models.mjs';
import {validationAuditView,validateResponse,validateBoth} from './validate.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),p=JSON.parse(await readFile(join(HERE,'prerequisites.json')));let checks=0;
const check=fn=>{fn();checks++;},reject=fn=>check(()=>assert.throws(fn));
const homes={HOME:'/original/home',home:'/original/lower',CODEX_HOME:'/original/codex',UNRELATED:'not forwarded'},beforeHomes=JSON.stringify(homes);check(()=>assert.deepEqual(inheritedHomePaths(homes),{HOME:homes.HOME,home:homes.home,CODEX_HOME:homes.CODEX_HOME}));check(()=>assert.equal(JSON.stringify(homes),beforeHomes));check(()=>assert.deepEqual(inheritedHomePaths({}),{}));
for(const name of ['TypeError','TimeoutError'])check(()=>assert.equal(readinessRetryAllowed(false,name),true));for(const name of ['TypeError','TimeoutError','SyntaxError'])check(()=>assert.equal(readinessRetryAllowed(true,name),false));check(()=>assert.equal(readinessRetryAllowed(false,'SyntaxError'),false));
for(const v of ['http://127.0.0.1:1','http://127.0.0.1:65535'])check(()=>assert.equal(loopback(v),v));
for(const v of ['http://localhost:80','https://127.0.0.1:80','http://0.0.0.0:80','http://127.0.0.1:65536','http://127.0.0.1:0','http://127.0.0.1:80/path','http://127.0.0.1:80@evil'])reject(()=>loopback(v));
for(const pid of [0,1,-1,99,NaN,Infinity,1.5])reject(()=>signalGroup(pid,99));check(()=>assert.equal(signalGroup(123,99),-123));
const config=washConfig('/private/tmp/owned/component.wasm','127.0.0.1:12345');check(()=>effectiveWash(config,'127.0.0.1:12345'));
for(const key of ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts']){const x=structuredClone(config);x.workload[key]=['unselected'];reject(()=>effectiveWash(x,'127.0.0.1:12345'));}
for(const key of ['plugins','host_plugins','volumes','components']){const x=structuredClone(config);x.dev[key]=['unselected'];reject(()=>effectiveWash(x,'127.0.0.1:12345'));}
const terminal={closed:true,status:0,signal:null,spawnError:null,thrown:null,ownedGroupGone:true,timedOut:false,outputLimitExceeded:false,externalSignal:null,errors:[],shutdownSignals:['SIGINT']};check(()=>gracefulServer(terminal));
for(const [key,value] of [['status',1],['signal','SIGKILL'],['spawnError',{}],['thrown',{}],['ownedGroupGone',false],['timedOut',true],['outputLimitExceeded',true],['externalSignal','SIGINT'],['errors',[{}]],['shutdownSignals',['SIGINT','SIGKILL']]])reject(()=>gracefulServer({...terminal,[key]:value}));
const future=JSON.parse(await readFile(join(HERE,'future-authority.template.json')));reject(()=>rootModel(future,'a'.repeat(64)));
const actualProof=JSON.parse(await readFile(p.availableComponentReviewData.result.path)),proofBefore=JSON.stringify(actualProof);check(()=>componentProofModel(actualProof,p));
for(const [key,value] of [['sourceFiles',342],['externalParentExitCode',1],['rawWorkerExitCode',1],['ownedGroupGone',false],['hostRequestsInvoked',true],['clockTypeOnly',false],['selectedInterfaces',SIX.slice(1)],['callableClockImports',['now']],['engineSha256','0'.repeat(64)]])reject(()=>componentProofModel({...actualProof,[key]:value},p));
check(()=>assert.equal(JSON.stringify(actualProof),proofBefore));
const actualAudit=JSON.parse(await readFile(p.pureFixtureData.audit.path)),wt=JSON.parse(await readFile(p.pureFixtureData.wasmtime.path)),wash=JSON.parse(await readFile(p.pureFixtureData.wash.path));
const originalBytes=JSON.stringify({actualAudit,wt,wash});
// Explicit synthetic request-view fixture around existing raw JSON only. This
// is not an engine/component proof, Root authority or actual consumer execution.
const audit={state:'CONSUMERS355_HTTP_COMPONENT_AUDIT_V1',nativeSources:355,entropyPolicy:'runtime-only',operationalAdmission:false,componentSha256:actualAudit.componentSha256,allowedImports:[...SIX],emittedImports:[...SIX],emittedExports:[...EXPORTS],clockDependency:actualAudit.clockDependency,baselineAndClassic:actualAudit};
const wrap=r=>({...r,requestTag:r.requestTag??r.request,headers:{contentType:'application/json',cacheControl:'no-store'},body:{...r.body,native:{consumerCombinedSchema:1,joint:r.body.native,consumers:{schema:1,calls:r.body.componentInstanceRequestCount,text:'€',json:{consumer:true}}}}});
const wtv={...wt,responses:wt.responses.map(wrap)},washv={...wash,responses:wash.responses.map(wrap)};
const validators={combined:await import(pathToFileURL(p.validators.combined.path)),hosts:await import(pathToFileURL(p.validators.hosts.path))};
for(const response of [...wtv.responses,...washv.responses])check(()=>validateResponse(response,audit,validators.combined));
check(()=>interfaceModel(audit));check(()=>assert.deepEqual(validationAuditView(audit,SIX).selectedInterfaces,SIX));
check(()=>assert.equal(validateBoth({audit,selection:SIX,wasmtime:wtv,wash:washv},validators).consumerRequestFixtureGroups,2));
for(const mutate of [
 r=>{r.status=503;},r=>{r.headers.contentType='text/html';},r=>{r.headers.cacheControl='public';},r=>{r.body.requestTag='wrong';},
 r=>{r.body.native.consumers.text='wrong';},r=>{r.body.native.consumers.json.consumer=false;},r=>{r.body.native.consumers.calls++;},
 r=>{r.body.native.joint.classic.ordinary[0]={wrong:true};},r=>{r.body.native.joint.classic.identity.esmAliases=false;},
 r=>{r.body.native.joint.baseline.foundations.schema=1;},r=>{r.body.native.joint.baseline.bytes=0;}
]){const bad=structuredClone(wtv.responses[0]);mutate(bad);reject(()=>validateResponse(bad,audit,validators.combined));}
for(const flag of ['entropyIntegrationFixture','foundationsIntegrationFixture','expandedFoundationsFixture','utilFoundationsFixture','streamWebFoundationsFixture','protectedAbortFoundationsFixture']){const bad=structuredClone(audit);bad.baselineAndClassic[flag]=false;reject(()=>validateResponse(wtv.responses[0],bad,validators.combined));}
const bad=structuredClone(audit);bad.clockDependency.typeOnly=false;reject(()=>interfaceModel(bad));reject(()=>validationAuditView(audit,SIX.slice(1)));
check(()=>assert.equal(JSON.stringify({actualAudit,wt,wash}),originalBytes));
console.log(JSON.stringify({schemaVersion:1,state:'CONSUMERS355_HTTP_HOST_PURE_MODEL_AND_REPORT_VIEW_CHECKS_PASSED',checks,
 actualOldResponseDataUsedOnlyAsSyntheticWrapperFixtures:true,oldRawBodiesAndMetadataUnchanged:true,fullBaselineProtected29Classic19ValidatorsExercisedAsPureData:true,
 sourceGuardPreflightServerPortsCurlRequestsHostNativeComponentGuestCodecOrOtherActionsInvoked:false}));
