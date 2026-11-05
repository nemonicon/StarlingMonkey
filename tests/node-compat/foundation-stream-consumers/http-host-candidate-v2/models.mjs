// Pure finite host/controller contracts. No process, network or owner calls.
import {need} from '../http-host-candidate-v1/authority.mjs';
export const OUTPUT='/private/tmp/starling-node-compat/consumers355-http-both-hosts-v2';
export const SIX=Object.freeze(['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:random/random@0.2.10']);
export const EXPORTS=Object.freeze(['wasi:http/incoming-handler@0.2.10']);
export const ENV=Object.freeze({PATH:'/usr/bin:/bin:/usr/sbin:/sbin',LANG:'C',LC_ALL:'C',TZ:'UTC',RAYON_NUM_THREADS:'1',BINARYEN_CORES:'1',CARGO_BUILD_JOBS:'1',PYTHONDONTWRITEBYTECODE:'1'});
export const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export function inheritedHomePaths(env){const out={};for(const k of ['HOME','home','CODEX_HOME'])if(env[k]!==undefined)out[k]=env[k];return out;}
export function readinessRetryAllowed(receivedHeaders,errorName){return receivedHeaders===false&&['TypeError','TimeoutError'].includes(errorName);}
export function interfaceModel(a){need(a?.entropyPolicy==='runtime-only'&&same(a.emittedImports,SIX)&&same(a.allowedImports,SIX)&&same(a.emittedExports,EXPORTS),'Exact six standard0.2.10 interfaces/sole incoming handler');need(a.clockDependency?.typeOnly===true&&same(a.clockDependency.callableImports,[])&&same(a.clockDependency.coreClockImports,[]),'Nominal duration type only/no callable or core clocks');}
export function rootModel(v,sha){
 need(v?.schemaVersion===1&&v.state==='ROOT_REVIEWED_CONSUMERS355_HTTP_BOTH_HOSTS_V2'&&v.sourceIndexSha256===sha&&v.actionAllowed===true&&v.hostRequestsAllowed===true,'New explicit host-only Root authority');
 need(v.outputRoot===OUTPUT&&v.sourceFiles===355&&v.variant==='normal-runtime'&&v.requestsPerHost===3&&v.workerTimeoutMs===600000,'Fixed355 RuntimeOnly/output/request/controller bounds');
 for(const k of ['wireBodyAdapterAllowed','metadataProjection','ordinary350Admission','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed'])need(v[k]===false,'Closed nonselected scope '+k);
 for(const k of ['sourceIndependentReview','actualComponentReview','constructionConfig','componentPhase','hostController'])need(v[k]&&typeof v[k]==='object','Actual separate proof '+k);
}
export function componentProofModel(v,p){
 need(v?.schemaVersion===1&&v.state==='INDEPENDENT_CONSUMERS355_HTTP_COMPONENT_REVIEW_PASSED_V1'&&v.verifiedPassed===true,'Independent actual component artifact review');
 need(v.constructionSourceIndexSha256===p.constructionSourceIndex.sha256&&v.sourceFiles===355&&v.engineSha256===p.engineSha256&&v.engineMetadataSha256===p.engineMetadataSha256,'Actual355 component/source/native identity');
 need(v.externalParentExitCode===0&&v.rawWorkerExitCode===0&&v.ownedGroupGone===true&&v.hostRequestsInvoked===false&&v.operationalAdmission===false&&v.runtimeAcceptanceClaim===false,'Actual clean construction0 without host acceptance');
 interfaceModel({...v,entropyPolicy:'runtime-only',allowedImports:v.selectedInterfaces,clockDependency:{typeOnly:v.clockTypeOnly,callableImports:v.callableClockImports,coreClockImports:v.coreClockImports}});
}
export function loopback(value){need(typeof value==='string'&&/^http:\/\/127\.0\.0\.1:[1-9][0-9]{0,4}$/.test(value),'Exact loopback HTTP origin');const n=Number(value.slice(value.lastIndexOf(':')+1));need(n<=65535,'Bounded port');return value;}
export function signalGroup(pid,self){need(Number.isSafeInteger(pid)&&pid>1&&pid!==self,'Only newly owned positive child PID');return -pid;}
export function washConfig(component,address){loopback('http://'+address);return{version:'2.11.0',build:{command:'test -f "$WASH_COMPONENT_PATH"',component_path:component},dev:{address,command:'test -f "$WASH_COMPONENT_PATH"',component_path:component,service:false,volumes:[],components:[],plugins:[],host_plugins:[]},workload:{allowedHosts:[],allowedIpNameLookups:[],allowedHostLoopbackPorts:[],config:{}},wit:{skip_fetch:true}};}
export function effectiveWash(v,address){need(v?.dev?.address===address,'Exact effective loopback address');for(const k of ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts'])need(same(v.workload?.[k],[]),'No outgoing host/IP/loopback allowlist');for(const k of ['volumes','plugins','components','host_plugins'])need(same(v.dev[k]??[],[]),'No selected host extension '+k);}
export function gracefulServer(v){need(v?.closed===true&&v.status===0&&v.signal===null&&v.spawnError===null&&v.thrown===null&&v.ownedGroupGone===true&&v.timedOut===false&&v.outputLimitExceeded===false&&v.externalSignal===null&&v.errors.length===0&&v.shutdownSignals.length===1&&v.shutdownSignals[0]==='SIGINT','Actual graceful0/owned group gone, no forced/error adoption');}
