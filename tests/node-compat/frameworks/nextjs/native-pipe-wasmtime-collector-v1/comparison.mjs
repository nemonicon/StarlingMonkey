// Pure DATA validation/comparison only. Never imports or invokes the pipe suite.
import assert from 'node:assert/strict';
import {isDeepStrictEqual} from 'node:util';
const keys=(value,names)=>{assert(value!==null&&typeof value==='object'&&!Array.isArray(value));assert.deepEqual(Object.keys(value).sort(),[...names].sort());};
const bool=value=>assert.equal(typeof value,'boolean');
const count=value=>assert(Number.isSafeInteger(value)&&value>=0&&value<=65536);
const strings=value=>{assert(Array.isArray(value)&&value.length<=16);for(const x of value)assert.equal(typeof x,'string');};
const locks=value=>{assert(Array.isArray(value)&&value.length===2);value.forEach(bool);};
function rejection(value){keys(value,['rejected','same','type',...(Object.hasOwn(value,'name')?['name']:[])]);bool(value.rejected);bool(value.same);assert(['object','boolean','null','string','number','undefined','function','symbol','bigint'].includes(value.type));if(Object.hasOwn(value,'name'))assert.equal(typeof value.name,'string');}
function failure(value){
 assert(value!==null&&typeof value==='object'&&!Array.isArray(value));
 assert(['undefined','object','boolean','string','number','function','symbol','bigint'].includes(value.type));bool(value.isNull);
 for(const key of Object.keys(value))assert(['type','isNull','value','name','message','code'].includes(key));
 if(value.isNull)assert.equal(value.value,null);
 for(const key of ['name','message','code'])if(Object.hasOwn(value,key)){const v=value[key];assert(v&&typeof v.type==='string');if(Object.hasOwn(v,'value'))assert(['string','number','boolean'].includes(typeof v.value));}
}
export function validate(value,call,contract){
 keys(value,['schemaVersion','suite','call','caseCount','records','applicationImported','fullNextClaim']);
 assert.equal(value.schemaVersion,1);assert.equal(value.suite,'NATIVE_SIGNAL_PIPE_REGRESSION_V1');assert.equal(value.call,call);
 assert.equal(value.caseCount,12);assert.equal(value.applicationImported,false);assert.equal(value.fullNextClaim,false);
 assert.equal(contract.length,12);assert(Array.isArray(value.records));assert.equal(value.records.length,12);
 assert.deepEqual(value.records.map(r=>r.id),contract.map(r=>r.id));
 for(let i=0;i<12;i++){
  const record=value.records[i];bool(record.completed);
  if(!record.completed){keys(record,['id','completed','error']);failure(record.error);continue;}
  keys(record,['id','completed','value']);const v=record.value;
  switch(i){
   case 0:keys(v,['log','readLocked','writeLocked']);strings(v.log);bool(v.readLocked);bool(v.writeLocked);break;
   case 1:keys(v,['log','closed','locks']);strings(v.log);count(v.closed);locks(v.locks);break;
   case 2:case 3:keys(v,['result',i===2?'aborts':'cancels','locks']);rejection(v.result);assert(Array.isArray(v[i===2?'aborts':'cancels']));v[i===2?'aborts':'cancels'].forEach(bool);locks(v.locks);break;
   case 4:keys(v,['result','log','locks']);rejection(v.result);assert(Array.isArray(v.log)&&v.log.length<=4);for(const e of v.log){assert(Array.isArray(e)&&e.length===2);assert(['abort','cancel'].includes(e[0]));bool(e[1]);}locks(v.locks);break;
   case 5:case 6:keys(v,['result','locks']);rejection(v.result);locks(v.locks);break;
   case 7:keys(v,['result','cancelled','aborted','locks']);rejection(v.result);count(v.cancelled);count(v.aborted);locks(v.locks);break;
   case 8:keys(v,['before','log','result','locks']);strings(v.before);strings(v.log);rejection(v.result);locks(v.locks);break;
   case 9:keys(v,['before','reads','writes','locks']);keys(v.before,['reads','writes']);count(v.before.reads);count(v.before.writes);count(v.reads);count(v.writes);locks(v.locks);break;
   case 10:case 11:keys(v,['rejected','locks',...(Object.hasOwn(v,'name')?['name']:[])]);bool(v.rejected);if(Object.hasOwn(v,'name'))assert.equal(typeof v.name,'string');locks(v.locks);break;
  }
 }
 return value;
}
export function compare(actual,node,call,contract){
 validate(actual,call,contract);validate(node,call,contract);
 return actual.records.map((value,i)=>({call,id:value.id,classification:value.completed&&node.records[i].completed&&isDeepStrictEqual(value,node.records[i])?'matches-node-selected-semantics':'difference-requires-review',actual:value,node:node.records[i]}));
}
export function parseOracle(text,contract){
 assert.equal(typeof text,'string');const frames=text.trim().split('\n').map(x=>JSON.parse(x));assert.equal(frames.length,4);
 const identity=frames[0];keys(identity,['kind','node','v8','suite','candidateInstalled','guestExecuted']);
 assert.equal(identity.kind,'node-oracle-identity');assert.equal(identity.node,'v22.14.0');assert.equal(identity.v8,'12.4.254.21-node.22');
 assert.equal(identity.suite,'NATIVE_SIGNAL_PIPE_REGRESSION_V1');assert.equal(identity.candidateInstalled,false);assert.equal(identity.guestExecuted,false);
 const values=[];
 for(let call=1;call<=3;call++){const frame=frames[call];keys(frame,['call','kind','value']);assert.equal(frame.call,call);assert.equal(frame.kind,'string');assert.equal(typeof frame.value,'string');const value=validate(JSON.parse(frame.value),call,contract);assert(value.records.every(r=>r.completed),'Oracle unexpected case failure cannot serve as a passing baseline');values.push(value);}
 return{identity,frames,values};
}
