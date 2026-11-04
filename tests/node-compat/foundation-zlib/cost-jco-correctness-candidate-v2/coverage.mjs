// Data-only final-coverage model. Actual terminal/component/proof admission is
// intentionally NOT represented by these booleans; it is a future loader cut.
import {primaryJobs,matrixJobs,offJobs} from './plan.mjs';
import {need} from './transport.mjs';
function unique(rows,key,label){const seen=new Set();for(const row of rows){const id=key(row);need(!seen.has(id),'Duplicate '+label);seen.add(id);}return seen;}
function complete(actual,expected,key,label){const a=unique(actual,key,label),e=new Set(expected.map(key));need(a.size===e.size&&[...a].every(id=>e.has(id)),'Complete exact '+label);}
export function requireCoverage({primary,mainEdges,offEncodings,offNodeEdges,offGuestEdges}){
 need([primary,mainEdges,offEncodings,offNodeEdges,offGuestEdges].every(Array.isArray),'All actual coverage arrays required');
 const expected=primaryJobs().flatMap(job=>job.kind==='retained-primary'?Array.from({length:3},(_,rotation)=>job.caseIds.map(caseId=>({kind:job.kind,arm:job.arm,caseId,rotation}))).flat():[{...job,rotation:0}]);
 complete(primary,expected,row=>[row.kind,row.arm,row.caseId,row.rotation].join(':'),'360 primary case observations');
 complete(mainEdges,matrixJobs(),row=>row.streamId+'->'+row.decoder,'135 fresh primary crossdecoder edges');
 const off=offJobs();complete(offEncodings,off.encoding,row=>row.provider+'.'+row.fixture+'.'+row.format,'15 separate FF-OFF encodings');
 complete(offNodeEdges,off.node,row=>row.provider+'.'+row.fixture+'.'+row.format+'->'+row.decoder,'15 separate fresh Node FF-OFF edges');
 complete(offGuestEdges,off.guest,row=>row.streamId+'->'+row.decoder,'45 separate FF-OFF guest edges');
 return{primaryObservations:360,mainCrossdecodeEdges:135,offEncodings:15,offNodeEdges:15,offGuestEdges:45,coverageOnlyNotRuntimeProof:true,timing:false};
}
