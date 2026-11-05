// M1 correction: bounded small reads; exact-role streamed large binary only.
import {descriptor,regular} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {streamHash} from '../cost-tooling-candidate-v3/context.mjs';
import {descriptorsIn} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
import {need} from '../cost-pilot-timing-candidate-v1/planner.mjs';
export const MAX_REGULAR_BYTES=64*1024*1024;
export const PINNED_LARGE_ROWS=Object.freeze([Object.freeze({
 path:'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',
 sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024,
 role:'actual-pinned-node-22.14.0-executable'
})]);
const canonicalAlias=path=>path.replace(/^\/tmp(?=\/|$)/,'/private/tmp');
export function descriptorReadPlan(value){
 const row=descriptor(value);need(Number.isSafeInteger(row.bytes)&&row.bytes>=0,'finite descriptor byte count');
 if(row.bytes<=MAX_REGULAR_BYTES)return Object.freeze({row,mode:'bounded-regular',maximumBytes:MAX_REGULAR_BYTES});
 const pinned=PINNED_LARGE_ROWS.find(r=>canonicalAlias(row.path)===r.path&&row.sha256===r.sha256&&row.bytes===r.bytes);
 need(pinned,'oversized descriptor must match exact known large role/path/hash/size; unknown or future rows refuse');
 return Object.freeze({row,mode:'streamed-pinned-executable',maximumBytes:pinned.bytes,role:pinned.role});
}
export async function verifyContractDescriptor(value){
 const plan=descriptorReadPlan(value); // capture immutable primitives before await
 if(plan.mode==='bounded-regular')await regular(plan.row,{maxBytes:plan.maximumBytes});
 else await streamHash(plan.row,{maximumBytes:plan.maximumBytes});
 return Object.freeze({descriptor:plan.row,mode:plan.mode,role:plan.role??null});
}
export function captureProofDescriptors(result,contract){
 return Object.freeze(descriptorsIn([result,contract.requiredExactDescriptors]).map(descriptor));
}
export async function verifyDescriptorList(values){
 need(Array.isArray(values)&&values.length>0&&values.length<=4096,'finite actual nested descriptor traversal');
 const rows=Object.freeze(values.map(descriptor)),plans=[];
 for(const row of rows)plans.push(await verifyContractDescriptor(row));
 const recheck=async()=>{for(const row of rows)await verifyContractDescriptor(row);};
 return Object.freeze({rows,plans:Object.freeze(plans),recheck});
}
