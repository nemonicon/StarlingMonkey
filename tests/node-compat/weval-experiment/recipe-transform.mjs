import assert from 'node:assert/strict';

// Applied only after the caller verifies the exact baseline recipe digest.
// No production CMake or original recipe is mutated.
export function wevalRecipe(baseline){
  let recipe=baseline;
  function replace(before,after,count=1){assert.equal(recipe.split(before).length-1,count,`Recipe pattern changed: ${before}`);recipe=recipe.split(before).join(after);}
  replace('spidermonkey_archive_sha=c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b','spidermonkey_archive_sha=f108286a1b9c35aeee89a803b073175a077633ffea5bbe4c3b85fcc85230dba0');
  replace('sm_variant=release\n','sm_variant=release_weval\n');
  replace('spidermonkey_dir="$work_root/spidermonkey-dist-$sm_variant"','spidermonkey_dir="$work_root/spidermonkey-dist-weval"');
  replace('-DWEVAL=OFF -DUSE_WASM_OPT=ON','-DWEVAL=ON -DUSE_WASM_OPT=OFF -DWEVAL_BIN="$NODE_COMPAT_WEVAL_BIN" -DWASM_OPT="$NODE_COMPAT_WEVAL_WASM_OPT"');
  replace("'WEVAL': 'OFF', 'USE_WASM_OPT': 'ON'","'WEVAL': 'ON', 'USE_WASM_OPT': 'OFF'");
  replace('engine_output=starlingmonkey_embedding.wasm','engine_output=starlingmonkey_embedding_weval.wasm');
  replace('artifact_name=starlingmonkey_embedding.','artifact_name=starlingmonkey_embedding.weval.',3);
  return recipe;
}
