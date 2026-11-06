// Pure retained-JSON tests: never import or execute the probe/oracle.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {compare,validate} from './comparison.mjs';
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,3);
const frames=(await readFile(process.argv[2],'utf8')).trim().split('\n').map(JSON.parse);
assert.equal(frames.length,4);assert.equal(frames[0].node,'v22.14.0');
const clone=x=>JSON.parse(JSON.stringify(x));let count=0;
const checks=[];
function check(name,fn){fn();checks.push(name);count++;}
const node=frames.slice(1).map((f,i)=>{assert.equal(f.call,i+1);assert.equal(f.kind,'string');return JSON.parse(f.value);});
for(let i=0;i<3;i++)check('actual Node JSON self-comparison '+(i+1),()=>{const before=JSON.stringify(node[i]);assert.equal(compare(node[i],node[i],i+1).nodeSelectedParity,true);assert.equal(JSON.stringify(node[i]),before);});
const n=node[0];
function negative(name,mutate){check(name,()=>{const a=clone(n);mutate(a);assert.equal(compare(a,n,1).nodeSelectedParity,false);});}
negative('capture descriptor change',a=>a.records[0].value.captureDescriptor.enumerable=true);
negative('stack own descriptor change',a=>a.records[0].value.stackOwnDescriptor.getType='undefined');
negative('string versus structured stack',a=>a.records[0].value.stack=clone(n.records[1].value.stack));
negative('missing callback invocation',a=>a.records[1].value.callbackInvocations=0);
negative('eager callback ordering',a=>a.records[1].value.events=['before-capture','callback','after-capture','before-stack-read','after-stack-read']);
negative('wrong callback target',a=>a.records[1].value.callbackTargetIdentity=false);
negative('frame method absent',a=>a.records[1].value.stack.frames[0].getFileName.methodType='undefined');
negative('zero frame line',a=>a.records[1].value.stack.frames[0].getLineNumber.return.value=0);
negative('wrong frame return type',a=>a.records[1].value.stack.frames[0].getColumnNumber.return.valueType='string');
negative('throw identity lost',a=>a.records[2].value.stackReadThrown.identity=false);
negative('throw hook skipped',a=>a.records[2].value.callbackInvocations=0);
negative('throw eager rather than lazy',a=>{a.records[2].value.captureThrown=a.records[2].value.stackReadThrown;a.records[2].value.stackReadThrown=null;a.records[2].value.captureReturned=false;a.records[2].value.stackReadReturned=true;});
negative('depd failure',a=>{a.records[3].value.depdLocationSucceeded=false;a.records[3].value.locationError={valueType:'object',isNull:false,isArray:false,name:{type:'string',value:'TypeError'},code:{type:'undefined'}};});
negative('depd location zero',a=>a.records[3].value.location.line=0);
negative('global restoration false',a=>a.errorGlobalsRestored=false);
function positive(name,mutate){check(name,()=>{const a=clone(n);mutate(a);assert.equal(compare(a,n,1).nodeSelectedParity,true);});}
positive('exact stack strings excluded',a=>{a.records[0].value.stack.string='different host callpath';a.records[0].value.stack.stringLength=a.records[0].value.stack.string.length;});
positive('exact frame filenames excluded',a=>{for(const r of a.records){const v=r.value;for(const s of [v.stack,v.callbackFrames])if(s?.frames)for(const f of s.frames)f.getFileName.return.value='different/source.js';}a.records[3].value.selectedFrame.getFileName.return.value='different/source.js';a.records[3].value.location.file='different/source.js';});
positive('positive line column values excluded',a=>{for(const r of a.records){const v=r.value;for(const s of [v.stack,v.callbackFrames])if(s?.frames)for(const f of s.frames){f.getLineNumber.return.value=987;f.getColumnNumber.return.value=654;}}a.records[3].value.selectedFrame.getLineNumber.return.value=987;a.records[3].value.selectedFrame.getColumnNumber.return.value=654;a.records[3].value.location.line=987;a.records[3].value.location.column=654;});
positive('exact frame counts excluded',a=>{for(const r of a.records)for(const s of [r.value.stack,r.value.callbackFrames])if(s?.frames)s.frameCount+=1;});
positive('exact function names excluded',a=>{for(const r of a.records)for(const s of [r.value.stack,r.value.callbackFrames])if(s?.frames)for(const f of s.frames)if(f.getFunctionName.return.valueType==='string')f.getFunctionName.return.value='differentName';a.records[3].value.location.name='differentName';a.records[3].value.selectedFrame.getFunctionName.return.value='differentName';});
for(const [name,mutate] of [['missing record',a=>a.records.pop()],['wrong ordinal',a=>a.call=2],['missing method shape',a=>delete a.records[1].value.stack.frames[0].getFileName]])check(name,()=>{const a=clone(n);mutate(a);assert.throws(()=>validate(a,1));});
console.log(JSON.stringify({schemaVersion:1,state:'STACKTRACE_COMPARISON_PURE_DATA_TESTS_PASSED_V1',passed:true,checks:count,names:checks,actualOracleCallsRead:3,probeExecuted:false,oracleExecuted:false,guestExecuted:false}));
