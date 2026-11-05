// Pure DATA check only; no host crypto/oracle producer imports.
import {EXPECTED} from './checks.mjs';
import {need} from '../ownership-component-candidate-v1/authority.mjs';
export function checkOracle(v){need(v?.node==='v22.14.0'&&v.tagHex===EXPECTED&&v.keys.length===2,'Pinned Node full known-answer');for(const k of v.keys)need(k.tagHex===EXPECTED&&k.valid===true&&k.invalid===false&&k.type==='secret'&&k.algorithm.name==='HMAC'&&k.algorithm.length===160&&k.algorithm.hash.name==='SHA-256'&&k.usages.join(',')==='sign,verify'&&k.extractable===(k.format==='jwk'),'Node raw/JWK full selected semantics');return true;}
