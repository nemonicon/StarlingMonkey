import {Buffer} from 'node:buffer';
import {addAbortListener} from 'node:events';
import * as events from 'node:events';
import {nestedOnceCases} from './public-cases.mjs';
let calls=0,snapshotCalls=0;
const snapshot=new AbortController(),snapshotResource=addAbortListener(snapshot.signal,()=>snapshotCalls++);
function check(value,label){if(!value)throw new Error(label);}
export function run(){
 calls++;let completed=0,receiver=true,contextRestored=true,disposalCalls=0;const order=[],c=new AbortController();let eventRef,later;
 c.signal.addEventListener('abort',function(){receiver&&=this===c.signal;order.push('ordinary');});
 addAbortListener(c.signal,function(event){
  receiver&&=this===c.signal&&event.currentTarget===c.signal;eventRef=event;order.push('protected');
  for(let i=0;i<8;i++){check(Buffer.from('00017fff80','hex').toString('hex')==='00017fff80','valid native hex roundtrip');completed++;}
  // All target/listener/disposer/key owners remain alive across those genuine
  // rooted-boundary Shrink collections. Check public post-GC registration and
  // nested event context without asserting ALS/AsyncResource behavior.
  const after=new AbortController();let afterCalls=0;
  after.signal.addEventListener('abort',event=>event.stopImmediatePropagation());
  const r=addAbortListener(after.signal,function(inner){afterCalls++;receiver&&=this===after.signal&&inner.currentTarget===after.signal;contextRestored&&=event.currentTarget===c.signal;});
  after.signal.dispatchEvent(new Event('abort'));check(afterCalls===1,'post-GC protected registration');r[Symbol.dispose]();
  const disposed=addAbortListener(after.signal,()=>disposalCalls++);disposed[Symbol.dispose]();after.signal.dispatchEvent(new Event('abort'));
  contextRestored&&=event.currentTarget===c.signal;later[Symbol.dispose]();
 });
 c.signal.addEventListener('abort',function(){receiver&&=this===c.signal;order.push('ordinary-once');},{once:true});
 later=addAbortListener(c.signal,()=>order.push('disposed-later'));
 c.signal.dispatchEvent(new Event('abort'));check(eventRef.currentTarget===null,'currentTarget cleared after dispatch');c.signal.dispatchEvent(new Event('abort'));
 check(completed===8,'eight valid native roundtrips');check(receiver&&contextRestored&&disposalCalls===0,'receiver/context/disposal retained');
 check(JSON.stringify(order)===JSON.stringify(['ordinary','protected','ordinary-once','ordinary']),'ordinary/protected/once order');
 const snapshotBefore=snapshotCalls;snapshot.signal.dispatchEvent(new Event('abort'));snapshotResource[Symbol.dispose]();
 return JSON.stringify({calls,completed,receiver,contextRestored,disposalCalls,order,snapshot:{before:snapshotBefore,after:snapshotCalls},nestedOnceCases:nestedOnceCases(events)});
}
