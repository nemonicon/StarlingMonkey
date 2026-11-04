// Finite data plan only. No provider, guest, toolchain or codec is imported.
export const ARMS=Object.freeze(['native-on','fflate-on','fflate-off']);
export const PRIMARY_PROVIDERS=Object.freeze(['node-22.14.0','native-on','fflate-on']);
export const MAIN_DECODERS=Object.freeze(['node-22.14.0','native-on','fflate-on']);
export const FORMATS=Object.freeze(['zlib','gzip','raw']);
export const FIXTURES=Object.freeze(['empty','small-repeat','small-prng','large-repeat','large-prng']);
export const RETAINED_ROTATIONS=3;
export function primaryJobs(){
 const jobs=[];
 for(const arm of ARMS){
  jobs.push({kind:'retained-primary',arm,rotations:RETAINED_ROTATIONS,caseIds:Array.from({length:30},(_,i)=>i)});
  for(let caseId=0;caseId<30;caseId++)jobs.push({kind:'fresh-primary',arm,caseId,rotations:1});
 }
 return Object.freeze(jobs.map(Object.freeze));
}
export function primaryStreams(){return Object.freeze(PRIMARY_PROVIDERS.flatMap(provider=>FIXTURES.flatMap(fixture=>FORMATS.map(format=>Object.freeze({provider,fixture,format,streamId:provider+'.'+fixture+'.'+format})))));}
export function matrixJobs(){return Object.freeze(primaryStreams().flatMap(stream=>MAIN_DECODERS.map(decoder=>Object.freeze({kind:'main-crossdecode',...stream,decoder,freshActualDecodeRequired:true,reuseEarlierNodeOwnDecode:false}))));}
export function offJobs(){
 const encoding=FIXTURES.flatMap(fixture=>FORMATS.map(format=>Object.freeze({kind:'off-encoding',provider:'fflate-off',fixture,format,compareFullBytesWith:'fflate-on',actualOffRequired:true})));
 const node=encoding.map(row=>Object.freeze({kind:'off-node-crossdecode',provider:'fflate-off',fixture:row.fixture,format:row.format,decoder:'node-22.14.0',freshActualDecodeRequired:true}));
 const guest=primaryStreams().map(stream=>Object.freeze({kind:'off-guest-crossdecode',...stream,decoder:'fflate-off',actualOffRequired:true,freshActualDecodeRequired:true}));
 return Object.freeze({encoding:Object.freeze(encoding),node:Object.freeze(node),guest:Object.freeze(guest)});
}
export function assertCompletePlan(need){
 const streams=primaryStreams(),matrix=matrixJobs(),off=offJobs();
 need(streams.length===45&&new Set(streams.map(row=>row.streamId)).size===45,'exact45 primary streams');
 need(matrix.length===135&&new Set(matrix.map(row=>row.streamId+'->'+row.decoder)).size===135,'exact135 main edges');
 need(off.encoding.length===15&&off.node.length===15&&off.guest.length===45,'separate actual FF-OFF15+15+45');
 return {primaryStreams:45,mainEdges:135,offEncoding:15,offNodeEdges:15,offGuestEdges:45,retainedRotations:3,primaryJobs:primaryJobs().length,controlsOrTimingImplemented:false};
}
