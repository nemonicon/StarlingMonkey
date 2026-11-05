// Differential oracle runs on the pinned HOST Node test process, never in guest.
import {createHmac,webcrypto} from 'node:crypto';
import {EXPECTED} from './checks.mjs';
import {need} from '../ownership-component-candidate-v1/authority.mjs';
export async function nodeOracle(){
 const raw=new Uint8Array(20).fill(11),message=new Uint8Array([72,105,32,84,104,101,114,101]),tagHex=createHmac('sha256',raw).update(message).digest('hex'),keys=[];
 for(const format of ['raw','jwk']){
  const key=await webcrypto.subtle.importKey(format,format==='raw'?raw:{kty:'oct',k:'CwsLCwsLCwsLCwsLCwsLCwsLCws',alg:'HS256',key_ops:['sign','verify'],ext:true},{name:'HMAC',hash:'SHA-256'},format==='jwk',['sign','verify']);
  const tag=new Uint8Array(await webcrypto.subtle.sign('HMAC',key,message)),bad=new Uint8Array(tag);bad[0]^=1;
  keys.push({format,type:key.type,extractable:key.extractable,algorithm:key.algorithm,usages:[...key.usages],tagHex:Buffer.from(tag).toString('hex'),valid:await webcrypto.subtle.verify('HMAC',key,tag,message),invalid:await webcrypto.subtle.verify('HMAC',key,bad,message)});
 }
 return {schemaVersion:1,node:process.version,tagHex,keys,hostTestOracleOnly:true,guestNodeCryptoExportsAdded:false};
}
export function checkOracle(v){need(v?.node==='v22.14.0'&&v.tagHex===EXPECTED&&v.keys.length===2,'Pinned Node full known-answer');for(const k of v.keys)need(k.tagHex===EXPECTED&&k.valid===true&&k.invalid===false&&k.type==='secret'&&k.algorithm.name==='HMAC'&&k.algorithm.length===160&&k.algorithm.hash.name==='SHA-256'&&k.usages.join(',')==='sign,verify'&&k.extractable===(k.format==='jwk'),'Node raw/JWK full selected semantics');return true;}
