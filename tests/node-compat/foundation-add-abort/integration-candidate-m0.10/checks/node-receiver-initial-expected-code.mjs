// Ordinary pinned Node only. Never invoke a Starling guard-absent path.
import assert from 'node:assert/strict';
import {addAbortListener} from 'node:events';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const results=[];
function rejected(name,fn){let error;try{fn();}catch(caught){error=caught;}assert(error instanceof TypeError);assert.equal(error.code,'ERR_INVALID_THIS');results.push({name,nameOfError:error.name,code:error.code});}
for(const [label,prototype] of [['EventTarget',EventTarget.prototype],['AbortSignal',AbortSignal.prototype]]){
 rejected(label+'.prototype.addEventListener',()=>Reflect.apply(EventTarget.prototype.addEventListener,prototype,['x',()=>{}]));
 rejected(label+'.prototype.removeEventListener',()=>Reflect.apply(EventTarget.prototype.removeEventListener,prototype,['x',()=>{}]));
 rejected(label+'.prototype.dispatchEvent',()=>Reflect.apply(EventTarget.prototype.dispatchEvent,prototype,[new Event('x')]));
 const previous=Object.getOwnPropertyDescriptor(prototype,'aborted');
 try{
  Object.defineProperty(prototype,'aborted',{configurable:true,value:false});
  rejected('structural addAbortListener '+label+'.prototype',()=>addAbortListener(prototype,()=>{}));
 }finally{if(previous)Object.defineProperty(prototype,'aborted',previous);else Reflect.deleteProperty(prototype,'aborted');}
}
{
 let calls=0,correctReceiver=true;
 const target=new EventTarget(),controller=new AbortController();
 target.addEventListener('x',function(){calls++;correctReceiver&&=this===target;},{once:true});target.dispatchEvent(new Event('x'));
 addAbortListener(controller.signal,function(){calls++;correctReceiver&&=this===controller.signal;});controller.abort();
 assert.equal(calls,2);assert.equal(correctReceiver,true);results.push({name:'initialized EventTarget and native-derived AbortSignal',calls,correctReceiver});
}
const bytes=await readFile(fileURLToPath(import.meta.url));
const report={state:'PINNED_NODE_ONLY_NO_GUEST_EXECUTION',node:process.version,driverSha256:createHash('sha256').update(bytes).digest('hex'),results,passed:results.length,
 targetCodeDeviation:'Proposed native guard provides TypeError without ERR_INVALID_THIS; component tests must require the declared bounded TypeError policy, not claim the Node code.'};
await writeFile(new URL('./node-receiver-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:results.length,state:report.state}));
