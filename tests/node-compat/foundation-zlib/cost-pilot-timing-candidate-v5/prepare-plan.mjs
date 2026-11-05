// Read-only DATA publisher bootstrap: complete source authentication first.
import {readSmallJson,captureSourceFamilies} from './source-families.mjs';
export const PLAN_OUTPUT='/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v5';
export async function preparePlan(options){
 const root=await readSmallJson(options.planAuthority);if(root.sourceIndexSha256!==options.sourceIndex?.sha256)throw Error('plan Root/source mismatch');
 const source=await captureSourceFamilies(options.sourceIndex);
 try{const body=await import('./prepare-plan-body.mjs');return await body.preparePlan(options,source);}finally{await source.recheck();}
}
