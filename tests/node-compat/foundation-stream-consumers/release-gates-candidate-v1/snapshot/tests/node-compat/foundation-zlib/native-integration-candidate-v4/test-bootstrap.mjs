// Fresh owned scratch refusals only; no Python verifier, artifact or loader runs.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {zlibBootstrapPreflight} from './artifact-tools/bootstrap-preflight.mjs';
assert.equal(process.version,'v22.14.0');assert(!process.env.NODE_OPTIONS);assert.equal(process.argv.length,3);
const here=dirname(fileURLToPath(import.meta.url)),output=resolve(process.argv[2]);assert(output.startsWith('/tmp/starling-node-compat/'));
await mkdir(output);const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),checks=[];
const source=await readFile(join(here,'bootstrap-pins.json')),pinsPath=join(output,'pins.json'),reviewPath=join(output,'review.json');
await writeFile(pinsPath,source,{flag:'wx'});await writeFile(reviewPath,'{}',{flag:'wx'});
const options={variant:'normal-off',reviewedPinsPath:pinsPath,reviewedPinsSha256:hash(source),rootReviewPath:reviewPath,rootReviewSha256:hash('{}')};
async function refused(name,options){await assert.rejects(()=>zlibBootstrapPreflight(options));checks.push(name);}
await refused('checked-in null pins fail before own index/Python/artifacts',options);
await refused('pin digest checked before JSON',{...options,reviewedPinsSha256:'0'.repeat(64)});
const reviewed=JSON.parse(source);reviewed.state='ROOT_REVIEWED_ZLIB350_VALIDATION_BOOTSTRAP_V1';const bytes=JSON.stringify(reviewed);
const reviewedPath=join(output,'reviewed-null.json');await writeFile(reviewedPath,bytes,{flag:'wx'});
await refused('requested reviewed null still fails before Python',{...options,reviewedPinsPath:reviewedPath,reviewedPinsSha256:hash(bytes)});
await refused('unknown variant cannot select a pin',{...options,reviewedPinsPath:reviewedPath,reviewedPinsSha256:hash(bytes),variant:'invented'});
reviewed.variants['normal-off']={state:'unreviewed-zlib350-production-freeze-pin-candidate',reviewRequired:true};const unreviewed=JSON.stringify(reviewed),unreviewedPath=join(output,'unreviewed.json');await writeFile(unreviewedPath,unreviewed,{flag:'wx'});
await refused('unreviewed exporter cannot reach verifier',{...options,reviewedPinsPath:unreviewedPath,reviewedPinsSha256:hash(unreviewed)});
await refused('Root review digest required',{...options,rootReviewSha256:'0'.repeat(64)});
const linked=join(output,'pins-link.json');await symlink(pinsPath,linked);await refused('authority symlink refused',{...options,reviewedPinsPath:linked});
const malformed=join(output,'malformed.json');await writeFile(malformed,'not json',{flag:'wx'});await refused('malformed changed pins rejected before parse',{...options,reviewedPinsPath:malformed,reviewedPinsSha256:'0'.repeat(64)});
const result={schemaVersion:1,state:'BOOTSTRAP_JS_NULL_AND_TAMPER_REFUSALS_PASSED',count:checks.length,checks,pythonVerifierOrArtifactOrGuestOrLoaderExecuted:false};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({checks:checks.length,output}));
