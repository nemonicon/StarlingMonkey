// Independent host facade protocol models only; this kernel performs no crypto.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const P='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/node-crypto-hash-hmac-candidate-v1';
const {createCryptoModule}=await import(pathToFileURL(P+'/crypto-facade.mjs'));
const manifest=JSON.parse(await readFile(P+'/node-export-manifest.json')),constants=JSON.parse(await readFile(P+'/constants-policy.json')).providedHeaderNumericSubset;
let checks=0;const check=(v,m)=>{assert(v,m);checks++;};const reject=(fn,code)=>{assert.throws(fn,e=>e?.code===code);checks++;};
const handles=[],updates=[],keys=[];let createFailure={present:false},updateFailure={present:false},digestFailure={present:false};
const kernel={constants:{...constants},createHash(){const h={kind:'hash',length:0,live:true};handles.push(h);return h;},createHmac(key){keys.push(key);if(createFailure.present)throw createFailure.value;const h={kind:'hmac',key:[...key],length:0,live:true};handles.push(h);return h;},update(h,input){assert(h.live);updates.push({input,offset:input.byteOffset,length:input.byteLength,bytes:input.length<=256?[...input]:null});if(updateFailure.present){h.live=false;throw updateFailure.value;}h.length+=input.byteLength;},digest(h){assert(h.live);h.live=false;if(digestFailure.present)throw digestFailure.value;return new Uint8Array(32).fill(h.length%256);}};
const webcrypto={nativeAliasModelOnly:true},subtle={nativeAliasModelOnly:true};const m=createCryptoModule({kernel,Buffer,webcrypto,subtle});
check(handles.length===0,'factory initialization creates no state');check(Object.keys(m).length===68&&Object.getOwnPropertyNames(m.default).length===71,'full names, no full implementation claim');
check(JSON.stringify(Object.keys(m))===JSON.stringify(manifest.esmNamedIncludingDefault),'exact official enumerable name order');check(Object.isFrozen(m)&&Object.isFrozen(m.default)&&Object.isFrozen(m.constants),'profile records frozen');
check(m.webcrypto===webcrypto&&m.subtle===subtle&&!Object.isFrozen(webcrypto),'existing native aliases not replaced/frozen in host model');
check(Object.keys(m.constants).length===9&&Object.entries(constants).every(([k,v])=>m.constants[k]===v&&Number.isInteger(v)),'meaningful typed9 constants');
check(m.getDiffieHellman===m.createDiffieHellmanGroup&&['prng','pseudoRandomBytes','rng'].every(k=>m.default[k]===m.randomBytes),'alias identities');
for(const n of manifest.unsupportedCallableNamed)reject(()=>m[n](),'ERR_SM_NODE_UNSUPPORTED');
for(const n of ['Hash','Hmac'])reject(()=>new m[n]('sha256','key'),'ERR_SM_NODE_UNSUPPORTED');
for(const a of ['sha1','sha-256','Sha256',null,{}])reject(()=>m.createHash(a),typeof a==='string'?'ERR_SM_NODE_UNSUPPORTED':'ERR_INVALID_ARG_TYPE');
reject(()=>m.createHash('sha256',{}),'ERR_SM_NODE_UNSUPPORTED');reject(()=>m.createHmac('sha256','key',{}),'ERR_SM_NODE_UNSUPPORTED');
for(const bad of [new DataView(new ArrayBuffer(2)),new Uint16Array(2),new ArrayBuffer(2),[1],new Proxy(new Uint8Array(2),{}),null])reject(()=>m.createHash('sha256').update(bad),'ERR_SM_NODE_UNSUPPORTED');
let conversions=0;reject(()=>m.createHash('sha256').update({get buffer(){conversions++;},toString(){conversions++;return'not data';}}),'ERR_SM_NODE_UNSUPPORTED');check(conversions===0,'no caller getters/conversion');
const source=Uint8Array.of(9,2,3,4,8),window=source.subarray(1,4),h=m.createHash('sha256');check(h.update(window)===h,'chain identity');source.fill(7);check(JSON.stringify(updates.at(-1).bytes)==='[2,3,4]'&&updates.at(-1).offset===1&&updates.at(-1).length===3,'exact view consumed synchronously by model');
h.update('\ud800');check(JSON.stringify(updates.at(-1).bytes)==='[239,191,189]','captured UTF8 conversion includes lone surrogate replacement');
reject(()=>h.digest('base64'),'ERR_SM_NODE_UNSUPPORTED');check(handles.at(-1).live,'invalid encoding refuses before consuming');const out=h.digest();check(Buffer.isBuffer(out)&&out.length===32,'owned bounded Buffer result');reject(()=>h.digest(),'ERR_CRYPTO_HASH_FINALIZED');reject(()=>h.update('x'),'ERR_CRYPTO_HASH_FINALIZED');
const keyed=Uint8Array.of(5,6,7),mac=m.createHmac('SHA256',keyed);keyed.fill(0);check(JSON.stringify(handles.at(-1).key)==='[5,6,7]','key snapshot model independent of caller mutation');mac.update(new Uint8Array(0));check(mac.digest('hex').length===64&&mac.digest('hex')===''&&Buffer.isBuffer(mac.digest())&&mac.digest().length===0,'Hmac empty repeated result distinct from Hash throw');reject(()=>mac.update('x'),'ERR_CRYPTO_HASH_FINALIZED');
for(const x of [false,0,'',null,Object.freeze({nativeFailureModel:true})]){
 createFailure={present:true,value:x};let caught=false;try{m.createHmac('sha256','secret');}catch(e){caught=true;check(e===x,'original native-create failure identity');}check(caught&&keys.at(-1).every(v=>v===0),'owned UTF8 key staging wiped despite native failure');
 createFailure={present:false};updateFailure={present:true,value:x};const a=m.createHash('sha256');caught=false;try{a.update('x');}catch(e){caught=true;check(e===x,'original native-update failure identity');}check(caught,'native update throw observed');reject(()=>a.update('retry'),'ERR_CRYPTO_HASH_FINALIZED');updateFailure={present:false};
 digestFailure={present:true,value:x};const b=m.createHash('sha256');caught=false;try{b.digest();}catch(e){caught=true;check(e===x,'original native-final failure identity');}check(caught,'native final throw observed');reject(()=>b.digest(),'ERR_CRYPTO_HASH_FINALIZED');digestFailure={present:false};
}
const cap=m.createHash('sha256'),chunk=new Uint8Array(16*1024*1024);for(let i=0;i<4;i++)cap.update(chunk);const count=updates.length;reject(()=>cap.update(Uint8Array.of(1)),'ERR_OUT_OF_RANGE');check(updates.length===count,'64MiB cumulative bound refuses before mock kernel');
for(const method of ['pipe','write','end','on','once','read','destroy','copy'])reject(()=>m.Hash.prototype[method].call(h),'ERR_SM_NODE_UNSUPPORTED');
process.stdout.write(JSON.stringify({schemaVersion:1,passed:true,checks,nonCryptographicMockKernelOnly:true,actualHashOrHmacCalls:0,nativeKernelCompiled:false,existingNativeAliasRuntimeObserved:false})+'\n');
