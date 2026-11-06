// Inert host-side DATA capture. No componentizer, engine or guest imports.
import {createHash} from 'node:crypto';
import {open} from 'node:fs/promises';
import {join} from 'node:path';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function writeWhole(path,bytes){
  const data=Buffer.from(bytes); // immutable local byte snapshot before async I/O
  const fd=await open(path,'wx',0o600);
  try{await fd.chmod(0o600);await fd.writeFile(data);await fd.sync();}finally{await fd.close();}
  return {path,sha256:hash(data),bytes:data.byteLength};
}
export function typedOwnGraph(value,componentReference=null){
  const seen=new Map();let fields=0;
  function visit(value,depth=0){
    if(depth>64)throw new Error('Returned DATA depth exceeds64');
    if(value===null)return {type:'null'};
    const type=typeof value;
    if(type==='undefined')return {type};
    if(type==='string'||type==='boolean')return {type,value};
    if(type==='number')return {type,value:Number.isNaN(value)?'NaN':Object.is(value,-0)?'-0':String(value)};
    if(type==='bigint')return {type,value:String(value)};
    if(type==='symbol')return {type,description:value.description??null};
    if(type==='function')return {type,serializedCallable:false};
    if(seen.has(value))return {type:'reference',id:seen.get(value)};
    const id=seen.size;seen.set(value,id);
    if(value instanceof Uint8Array)return {type:'Uint8Array',id,byteLength:value.byteLength,sha256:hash(value),
      ...(componentReference&&value===componentReference.value?{file:componentReference.descriptor}:{} )};
    const properties=[];
    for(const key of Reflect.ownKeys(value)){
      if(++fields>100000)throw new Error('Returned DATA properties exceed100000');
      const d=Object.getOwnPropertyDescriptor(value,key);
      const item={key:typeof key==='symbol'?{symbol:key.description??null}:{string:key},enumerable:d.enumerable,configurable:d.configurable};
      if(Object.hasOwn(d,'value')){item.kind='data';item.writable=d.writable;item.value=visit(d.value,depth+1);}
      else{item.kind='accessor';item.get=typeof d.get;item.set=typeof d.set;}
      properties.push(item);
    }
    return {type:Array.isArray(value)?'Array':'object',id,properties};
  }
  return visit(value);
}
function ordinaryJSON(value,seen=new Set()){
  if(value===null||typeof value==='string'||typeof value==='boolean')return value;
  if(typeof value==='number'&&Number.isFinite(value))return value;
  if(typeof value!=='object'||seen.has(value))throw new Error('Imports must be ordinary acyclic JSON DATA');
  seen.add(value);
  const array=Array.isArray(value),keys=Reflect.ownKeys(value),out=array?[]:{};
  if(!array&&Object.getPrototypeOf(value)!==Object.prototype&&Object.getPrototypeOf(value)!==null)throw new Error('Imports object prototype unsupported');
  for(const key of keys){
    if(array&&key==='length')continue;
    if(typeof key!=='string'||(array&&!/^(0|[1-9][0-9]*)$/.test(key)))throw new Error('Imports own key unsupported');
    const d=Object.getOwnPropertyDescriptor(value,key);if(!Object.hasOwn(d,'value'))throw new Error('Imports accessor unsupported');
    Object.defineProperty(out,key,{value:ordinaryJSON(d.value,seen),enumerable:true,writable:true,configurable:true});
  }
  if(array&&out.length!==value.length)throw new Error('Imports sparse array unsupported');
  seen.delete(value);return out;
}
export async function captureComponentReturn(returned,output){
  // No semantic API/Wasm/import admission precedes these actual byte/shape writes.
  let component=null;const d=returned!==null&&typeof returned==='object'?Object.getOwnPropertyDescriptor(returned,'component'):null;
  if(d&&Object.hasOwn(d,'value')&&d.value instanceof Uint8Array){
    component=await writeWhole(join(output,'returned-component.wasm'),d.value);
  }
  const shape=typedOwnGraph(returned,component?{value:d.value,descriptor:component}:null);
  const ownShape=await writeWhole(join(output,'returned-own-shape.json'),JSON.stringify(shape,null,2)+'\n');
  // The full typed graph above keeps undefined/debug, accessors, extras and
  // malformed imports. Refusal below never removes already captured bytes.
  if(!component)throw new Error('API did not return an own Uint8Array component');
  const props=Object.getOwnPropertyDescriptors(returned);
  if(!Object.hasOwn(props,'imports')||!Object.hasOwn(props.imports,'value'))throw new Error('API imports is not own DATA');
  const imports=ordinaryJSON(props.imports.value);
  const importsFile=await writeWhole(join(output,'returned-imports.json'),JSON.stringify(imports,null,2)+'\n');
  if(!Array.isArray(imports)||!imports.every(pair=>Array.isArray(pair)&&pair.length===2&&pair.every(x=>typeof x==='string')))throw new Error('Unexpected genuine componentize imports shape');
  return {component,returnedImports:importsFile,returnedOwnShape:ownShape};
}
