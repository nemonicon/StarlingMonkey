// Actual retained JSON only; no guard, process helper or guest is invoked.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const load=async p=>JSON.parse(await readFile(p));
const r=await load(new URL('../ownership-wasmtime-candidate-v1/references.json',import.meta.url));
const nr=await load(r.normalReview.result.path),ar=await load(r.artifactReview.result.path),nc=await load(r.normalContract.path),ac=await load(r.artifactContract.path);let checks=0;
for(const [data,contract]of [[nr,nc],[ar,ac]])for(const [k,v]of Object.entries(contract.requiredFixedValues)){assert.equal(JSON.stringify(data[k]),JSON.stringify(v),k);checks++;}
for(const [a,b]of [[nr.coverage,nc.requiredCoverage],[nc.artifacts,ac.artifacts],[r.artifacts,ac.artifacts]]){assert.equal(JSON.stringify(a),JSON.stringify(b));checks++;}
console.log(JSON.stringify({state:'ACTUAL_JS_CONTRACT_EQUALITY_CHECKS_PASSED',checks,wasmtimeOrGuestActionsInvoked:false}));
