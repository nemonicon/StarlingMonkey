// Fixed RuntimeOnly gate before loader/import of the private builder sibling.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {verifyProductionTicks,requireFreshOutput,completeRegression,hash} from './preflight.mjs';
const admission=await verifyProductionTicks({entropyPolicy:'runtime-only'});
assert(process.env.NODE_COMPAT_PRODUCTION_HTTP_ROOT);const root=resolve(process.env.NODE_COMPAT_PRODUCTION_HTTP_ROOT);
assert.equal(resolve(process.env.NODE_COMPAT_HTTP_OUTPUT),join(root,'http-joint'));
const inputsPath=join(root,'http-inputs.json'),inputsBytes=await readFile(inputsPath),inputsHash=hash(inputsBytes),inputs=JSON.parse(inputsBytes);
assert.equal(inputs.state,'CLASSIC342_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING');assert.equal(inputs.nativeAdmission.engineSha256,admission.pin.engineSha256);assert.equal(inputs.sourceInputClosure.sha256,admission.report.inputClosure.sha256);
await requireFreshOutput('NODE_COMPAT_HTTP_OUTPUT');
await import('./runners/http-build.mjs');
assert.equal(hash(await readFile(inputsPath)),inputsHash,'HTTP prepack seal changed');
await completeRegression('NODE_COMPAT_HTTP_OUTPUT',admission);
