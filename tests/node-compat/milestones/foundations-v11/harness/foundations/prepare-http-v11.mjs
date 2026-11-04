// Capture exact HTTP inputs BEFORE the separately authorized packaging step.
// This only reads source/engine receipts; it does not instantiate a guest.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { preflight } from '../foundation-add-abort/production-native-m0.10/preflight.mjs';
import { selectCoreExpectations } from '../core-expectations.mjs';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../..');
const root=resolve(process.env.NODE_COMPAT_HTTP_V11_ROOT??'/tmp/starling-node-compat/foundations-v11');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const admitted=await preflight();
assert.equal(admitted.metadata.entropyPolicy,'runtime-only');
assert.equal(admitted.report.engineSha256,'2e3731ce248be1d8ede0f5672dd87b48fb1731dfddb045bfaabaeea02534a36d');
assert.equal(admitted.report.engineMetadataSha256,'9adc95f3966ea5b12a4d2b6753b32f2f72ce736990e649d55bf367e808bbc07a');
const core=selectCoreExpectations(admitted.metadata,{sourceRoot:admitted.sourceRoot});
assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');
assert.equal(core.allocUnsafePolicy,'zeroed-no-pool-direct-u8-v1');
const paths=[
  'foundations/http-v11.mjs','foundations/assert-http-report.mjs',
  'foundations/assert-protected-abort-report.mjs','foundations/assert-stream-web-report.mjs',
  'foundations/prepare-http-v11.mjs','foundations/audit-http-v11.mjs',
  'wasmcloud/build-http.mjs','wasmcloud/http-stubbing.mjs','wasmcloud/type-audit.mjs',
  'wasmcloud/test-wasmtime-http.mjs','wasmcloud/run-host.mjs','wasmcloud/profile-runtime-entropy.wit',
  'foundation-add-abort/production-native-m0.10/component.mjs',
  'foundation-add-abort/production-native-m0.10/public-cases.mjs',
  'foundation-add-abort/production-native-m0.10/require.cjs',
  'foundation-add-abort/production-native-m0.10/node-results.json',
  'foundation-add-abort/production-native-m0.10/preflight.mjs',
  'core-expectations.mjs','module-selection.mjs','fixtures/component.mjs',
  'profile-bundler.mjs','componentizer.mjs','capability-policy.mjs','toolchain.mjs',
];
const sourceFiles=[];
for(const path of paths){const relative='tests/node-compat/'+path,bytes=await readFile(join(repository,relative));sourceFiles.push({path:relative,sha256:hash(bytes),bytes:bytes.length});}
const report={state:'HTTP_V11_INPUTS_FROZEN_BEFORE_PACKAGING',recordedAtUtc:new Date().toISOString(),repository,
  nativeAdmission:admitted.report,coreExpectations:core,sourceFiles,
  scope:'Complete HTTP-v10/schema5/protected29 body retained with core m0.11; this is input admission, not guest or host proof'};
const output=join(root,'http-v11-inputs.json');
await writeFile(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({output,sourceFiles:sourceFiles.length,engineSha256:admitted.report.engineSha256,coreVersion:core.coreVersion,packaged:false}));
