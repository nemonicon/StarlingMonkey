// Pure extracted validation block; no codec/provider, bundle or guest runs.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {Buffer} from 'node:buffer';
import {bytesEqual,requireValue} from '../cost-guest-oracle-candidate-v1/contract.mjs';
import {ownedWindow,unchangedWindow} from '../cost-guest-oracle-candidate-v1/owned-window.mjs';
const root=new URL('../cost-guest-oracle-candidate-v1/',import.meta.url);
const raw=await readFile(new URL('runtime.mjs',root));
const sourceSha256=createHash('sha256').update(raw).digest('hex');
assert.equal(sourceSha256,'33456781163dc5a88448a1da5c4f1e0078e1b0525c9e054e86b366887fb6c56e');
const text=raw.toString(),begin=text.indexOf('  const previousComparable='),end=text.indexOf('  const result=',begin);
assert(begin>0&&end>begin);
const extracted=text.slice(begin,end);
assert(!extracted.includes('invoke(')&&!extracted.includes('provider.'));
const predicate=new Function('priorOutput','output','active','inputBefore','caseId','bytesEqual','unchangedWindow','requireValue',
  'const nonempty=output.length>0;\n'+extracted+'\nreturn {previousComparable,independentBacking,mutationProbe};');
const records=[];
for(const changedIndex of [0,1,63]){
  const original=Uint8Array.from({length:64},(_,i)=>i),prior=new Uint8Array(original),output=new Uint8Array(original);
  // Simulate only an intervening memory effect as ordinary data mutation.
  // No fake or real provider function is invoked.
  prior[changedIndex]^=255;
  const input=Uint8Array.of(7,8),window=ownedWindow(Buffer,input);
  const observed=predicate({caseId:0,output:prior},output,{window},new Uint8Array(input),0,bytesEqual,unchangedWindow,requireValue);
  assert.equal(observed.previousComparable,true);assert.equal(observed.independentBacking,true);
  assert.equal(observed.mutationProbe.currentFullBytesUnchanged,true);
  assert.equal(observed.mutationProbe.inputFullBytesUnchanged,true);
  assert.equal(observed.mutationProbe.previousRestored,true);
  assert(!bytesEqual(prior,original));assert(bytesEqual(output,original));
  records.push({changedIndex,allExistingOwnershipPredicatesPass:true,firstAndSecondSerializedBytesWouldMatch:true,heldPriorFullBytesCorrupted:true,observed});
}
const result={schemaVersion:1,state:'PURE_SOURCE_OUTPUT_STABILITY_COUNTEREXAMPLE_CONFIRMED',sourceSha256,extractedValidationBlock:extracted,records,codecOrProviderCalls:0,actualCodecDefectObserved:false};
await writeFile(process.argv[2],JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({counterexamples:records.length,codecCalls:0,sourceValidationGap:true}));
