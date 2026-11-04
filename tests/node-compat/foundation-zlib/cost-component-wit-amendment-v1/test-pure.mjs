// Pure amendment identities/ABI/source values only. No tool/codec/guest action.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {authorityModel,OUTPUTS,TOOLING_SHA,GUEST_SHA,PUBLICATION,COMPONENT_BASE_SHA} from './guard.mjs';
import {parsePublicWit} from './abi.mjs';
const here=dirname(fileURLToPath(import.meta.url)),before=await readFile(join(here,'../cost-component-candidate-v1/public-abi.wit'),'utf8'),after=await readFile(join(here,'public-abi.wit'),'utf8');
let checks=0;const yes=fn=>{fn();checks++;},no=fn=>{assert.throws(fn);checks++;};
yes(()=>assert.equal(after,before.replaceAll('record: string','input: string')));yes(()=>assert(!/\bfunc\(record\s*:/.test(after)));yes(()=>assert.equal((after.match(/input: string/g)??[]).length,2));
const emitted=wit=>wit.replace('package starling:codec-cost-proposal;','package root:component;').replace('world codec-cost-proposal','world root');yes(()=>assert.deepEqual(parsePublicWit(emitted(after)),parsePublicWit(emitted(before))));
const H='a'.repeat(64),row={path:'/private/tmp/unconfigured.json',sha256:H,bytes:100},proof={index:row,result:row},value={schemaVersion:1,state:'ROOT_REVIEWED_ZLIB_COST_COMPONENT_BUILD_V1',action:'component-build',actionAllowed:true,componentSourceIndexSha256:H,componentBaseSourceIndexSha256:COMPONENT_BASE_SHA,toolingCandidateIndexSha256:TOOLING_SHA,guestSourceIndexSha256:GUEST_SHA,arm:'native-on',outputRoot:OUTPUTS['native-on'],nativeInputs:350,metadataProjection:false,operationalAdmission:false,sourcePromotionAllowed:false,workerTimeoutMs:600000,maxComponentBytes:67108864,ordinaryGuestExportCallsAllowed:false,pilotOrTimingAllowed:false,publicationIndex:PUBLICATION,sourcePublicationCompletion:row,sourcePublicationProof:proof,nodeOracleRenderProof:proof,rootReviewedPair:proof,actualBundleReview:proof,componentSourceReview:proof};
yes(()=>authorityModel(value,{componentSourceIndexSha256:H,arm:'native-on'}));
no(()=>authorityModel({...value,componentBaseSourceIndexSha256:undefined},{componentSourceIndexSha256:H,arm:'native-on'}));
no(()=>authorityModel({...value,componentBaseSourceIndexSha256:'b'.repeat(64)},{componentSourceIndexSha256:H,arm:'native-on'}));
no(()=>authorityModel({...value,outputRoot:value.outputRoot.replace('component-v2-','component-v1-')},{componentSourceIndexSha256:H,arm:'native-on'}));
process.stdout.write(JSON.stringify({schemaVersion:1,state:'WIT_PARAMETER_AMENDMENT_PURE_DATA_CHECKS_PASSED',checks,typeArityWireProtocolUnchanged:true,actualParserInvokedByAuthor:false,authorityModelSyntheticOnly:true,ownerActionOrGuestOrCodecOrToolInvoked:false})+'\n');
