// Normal entropy-OFF follow-ons only. The reviewed common pins remain null.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyProductionTicks,verifyInputClosure,requireFreshOutput,hash} from '../production-regression-candidate-v5/preflight.mjs';
import {selectDependencyIndex} from '../production-regression-candidate-v5/dependency-bindings.mjs';
export {requireFreshOutput};
const here=dirname(fileURLToPath(import.meta.url));
export async function verifyFollowonOff(){
  // FIRST operation: real fixed production admission, before loaders/fixtures.
  const production=await verifyProductionTicks({gcStress:false});
  const dependencyPath=join(here,'dependency-pins.json'),dependencyBytes=await readFile(dependencyPath),dependencySha256=hash(dependencyBytes);
  const commonIndex=selectDependencyIndex(JSON.parse(dependencyBytes),'commonIndexSha256');
  assert.equal(hash(await readFile(join(here,'../production-regression-candidate-v5/index.json'))),commonIndex);
  const inputClosure=await verifyInputClosure({manifestPath:join(here,'input-freeze.json')});
  const manifestPath=inputClosure.path,expectedManifestSha256=inputClosure.sha256;
  async function recheck(){
    // The common closure verifies captured primitive pin and manifest digests
    // before parsing/following changed data. Its actual artifact checks remain.
    await production.recheck();
    assert.equal(hash(await readFile(dependencyPath)),dependencySha256,'Parent index pins changed during run');
    await verifyInputClosure({manifestPath,expectedSha256:expectedManifestSha256});
  }
  return{report:{state:'normal-off-followon-source-and-fixed-production-admission-passed',
    production:production.report,commonIndex,inputClosure,runtimeProof:false},recheck};
}
export async function completeFollowon(variable,admission){
  await admission.recheck();
  await writeFile(join(resolve(process.env[variable]),'followon-admission-complete.json'),
    JSON.stringify({...admission.report,consumedInputsRecheckedAfterRun:true},null,2)+'\n',{flag:'wx'});
}
