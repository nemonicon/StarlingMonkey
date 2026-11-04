import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {classicPreflight} from '../integration-candidate-v1/runtime-preflight.mjs';
const observations=[];
for (const variant of ['normal-off','normal-runtime','gc-off','disabled-off']) {
  let error;
  try { await classicPreflight({variant}); } catch (caught) { error=caught; }
  assert(error && /null|pin|review/i.test(error.message),variant);
  observations.push({variant,errorName:error.name,message:error.message});
}
const result={state:'ROOT_FOUR_NULL_PREFLIGHT_GATES_REFUSED',node:process.version,
  observations,componentizerInvoked:false,engineRead:false,guestInvoked:false};
await writeFile(new URL('./null-preflight-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
