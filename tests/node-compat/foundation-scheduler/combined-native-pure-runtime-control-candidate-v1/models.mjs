// Pure checks only. No fixture, generated module, native API or process call.
import {isDeepStrictEqual as same} from 'node:util';
export const need=(v,m)=>{if(!v)throw Error(m);};
export function pureValue(value,ordinal){
 need(typeof value==='string'&&value.length<=2097152,'Complete ordinary bounded string; no await/coercion');
 const parsed=JSON.parse(value);
 need(same(parsed,{schemaVersion:1,initial:0,calls:ordinal,hex:'c3a92201',timerRequested:false}),'Whole pure schema/types/counter/bytes');
 return value;
}
export function equalValue(value,oracle,ordinal){
 pureValue(value,ordinal);pureValue(oracle,ordinal);
 need(value===oracle&&Buffer.from(value).equals(Buffer.from(oracle)),'Exact whole actual Node string/UTF8 bytes');return true;
}
export function namespaceModel(ns,kind){
 need(ns!==null&&typeof ns==='object'&&Object.getPrototypeOf(ns)===null,'Real ESM namespace shape');
 const keys=Object.getOwnPropertyNames(ns).sort(),wanted=kind==='oracle'?['run']:['_util','run'];
 need(same(keys,wanted)&&!Object.hasOwn(ns,'then'),'Exact namespace names, no then assimilation');
 const d=Object.getOwnPropertyDescriptors(ns);
 need(Object.hasOwn(d.run,'value')&&typeof d.run.value==='function'&&Object.getOwnPropertyDescriptor(d.run.value,'length')?.value===0,'Own scalar function/arity DATA, no getter read');
 if(kind!=='oracle'){
  need(Object.hasOwn(d._util,'value'),'Own helper DATA property');const u=d._util.value;
  need(u!==null&&typeof u==='object'&&Object.getPrototypeOf(u)===Object.prototype&&Reflect.ownKeys(u).length===0,'Exactly empty ordinary helper');
 }
 return d.run.value;
}
export function terminalModel(t){
 need(t?.closed===true&&t.status===0&&t.signal===null&&t.spawnError===null&&t.timedOut===false&&t.externalSignal===null&&t.outputLimitExceeded===false&&t.ownedGroupGone===true&&t.terminalExitZeroObserved===true&&t.signalCount===0&&t.errors.length===0&&t.signals.length===0,'Owned actual raw0/full streams/no timeout/cleanup');return true;
}
export const VALUE_SCHEDULE=Object.freeze({oracle:3,retained:3,fresh:1,wasmtime:3,componentStrings:7,totalStrings:10});
