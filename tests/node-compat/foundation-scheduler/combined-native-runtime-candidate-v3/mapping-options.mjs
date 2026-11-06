// Own request boundary only. No Jco, generated application, provider or process.
import {need,IDS,mappingOptions} from './models.mjs';
const ownData=(value,keys,label)=>{
 need(value!==null&&typeof value==='object'&&Object.getPrototypeOf(value)===Object.prototype,label+' plain own object');const ds=Object.getOwnPropertyDescriptors(value),names=Reflect.ownKeys(ds);need(names.length===keys.length&&names.every(k=>typeof k==='string'&&keys.includes(k)),label+' exact own keys including nonenumerable/symbol refusal');for(const k of keys)need(ds[k]&&Object.hasOwn(ds[k],'value')&&ds[k].enumerable,label+' enumerable DATA only');return Object.fromEntries(keys.map(k=>[k,ds[k].value]));
};
function shimUrl(url,row){need(typeof url==='string'&&row&&typeof row.path==='string','Explicit pinned standard shim URL/descriptor');const u=new URL(url);need(u.protocol==='file:'&&u.host===''&&u.search===''&&u.hash===''&&decodeURIComponent(u.pathname)===row.path,'Exact physical standard shim path; no remote/query/fragment/path change');}
export function snapshotRequestedOptions(refs,id,candidate=mappingOptions(refs,id)){
 need(IDS.includes(id)&&id!=='init-fatal','Only accepted positive/fatal component fixture IDs');shimUrl(refs.shimClocksUrl,refs.shimClocks);shimUrl(refs.shimIoUrl,refs.shimIo);
 const v=ownData(candidate,['name','wasiShim','map'],'requested options'),map=ownData(v.map,['wasi:clocks/*','wasi:io/*'],'requested map'),expected=mappingOptions(refs,id);
 need(v.name===expected.name&&/^[A-Za-z0-9_]+$/.test(v.name)&&v.wasiShim===false,'Exact nonpath output name/explicit mapping mode');for(const k of Object.keys(expected.map))need(map[k]===expected.map[k],'Only exact requested standard clock/io map '+k);
 return Object.freeze({name:v.name,wasiShim:false,map:Object.freeze({...map})});
}
export async function prepareRequestedOptions(out,refs,id,candidate){
 const requested=snapshotRequestedOptions(refs,id,candidate),workCopy={name:requested.name,wasiShim:requested.wasiShim,map:{...requested.map}};
 // This durable JSON is the request. The compiler receives a separate mutable
 // plain work object with a separate nested map, never the retained snapshot.
 const row=await out.write('requested-mapping-options.json',requested,{json:true});return{requested,workCopy,row};
}
export function typedPostCallOptions(value){
 const seen=new Set();let nodes=0;
 function describe(v,depth=0){const type=typeof v;if(v===null||type==='string'||type==='boolean')return{type,value:v};if(type==='undefined')return{type};if(type==='number')return Number.isFinite(v)?{type,value:v}:{type,nonfinite:true};if(type!=='object')return{type,opaque:true,fullValueClaim:false};if(seen.has(v))return{type,circular:true,fullValueClaim:false};if(depth>4||++nodes>256)return{type,boundedObservationOnly:true,fullValueClaim:false};seen.add(v);const descriptors=Object.getOwnPropertyDescriptors(v),properties=[];for(const key of Reflect.ownKeys(descriptors)){const d=descriptors[key],name=typeof key==='string'?{key}:{keyType:'symbol',opaque:true};properties.push({...name,enumerable:d.enumerable,configurable:d.configurable,...(Object.hasOwn(d,'value')?{kind:'data',writable:d.writable,observed:describe(d.value,depth+1)}:{kind:'accessor',getterPresent:typeof d.get==='function',setterPresent:typeof d.set==='function'})});}seen.delete(v);return{type,properties,fullValueClaim:false};}
 return{schemaVersion:1,meaning:'typed own-property observation AFTER compiler return; not the supplied input wire or a sanitized JSON options object',observed:describe(value),inputWireClaim:false,optionsMutatedOrSanitizedByObserver:false};
}
export function requestedPublicationFields(boundary,root,postRow){
 need(boundary&&Object.isFrozen(boundary.requested)&&Object.isFrozen(boundary.requested.map)&&boundary.row.path==='requested-mapping-options.json'&&postRow.path==='mapping-options-postcall-shape.json','Actual retained boundary/diagnostic file roles');
 return{mappingOptions:boundary.requested,mappingOptionsMeaning:'pristine-request-retained-before-Jco-call',requestedMappingOptions:{...boundary.row,path:root+'/'+boundary.row.path},postCallOptionsShape:{...postRow,path:root+'/'+postRow.path},postCallOptionsInputWireClaim:false};
}
