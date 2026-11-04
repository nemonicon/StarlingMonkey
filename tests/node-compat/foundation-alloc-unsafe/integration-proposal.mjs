// Emits an explicitly unassigned proposal; never rewrites a production manifest.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../..');
const manifestPath = 'builtins/node-compat/export-manifest.node-v22.14.0.json';
const receipt = JSON.parse(await readFile('/tmp/starling-node-compat/foundations-v6/native-freeze/off-foundations.engine.wasm.build.json'));
const hash = value => createHash('sha256').update(value).digest('hex');
const files = ['buffer-facade.mjs', 'buffer.cpp', 'factories.generated.h', 'unsupported.mjs', 'export-manifest.node-v22.14.0.json'];
const productionUnchanged = [];
for (const name of files) {
  const path = 'builtins/node-compat/'+name, digest = hash(await readFile(join(repository, path)));
  assert.equal(digest, receipt.sourceManifest.find(item => item.path === path)?.sha256, 'Production core must stay at v6 input '+name);
  productionUnchanged.push({ path, sha256: digest });
}
const base = JSON.parse(await readFile(join(repository, manifestPath)));
assert.equal(base.profileVersion, 'sm-node-22.14.0-m0.1');
assert(base.modules['node:buffer'].unsupportedStatic.includes('allocUnsafe'));
const node = JSON.parse(await readFile(join(here, 'node-results.json')));
const component = JSON.parse(await readFile(join(here, 'component-results.json')));
const proposal = { schema: 'source-integration-proposal-v1', proposalVersion: 'buffer-allocunsafe-zeroed-v1',
  productionImplemented: false, productionUnchanged, baseManifest: { path: manifestPath,
    profileVersion: base.profileVersion, sha256: productionUnchanged.at(-1).sha256 },
  nextCoreProfileVersion: null, versionAssignment: 'Coordinator must assign a new core profile version before integration; no global version reserved by this experiment',
  selectedManifestPolicy: 'Replace the selected core revision coherently; do not overlay two manifests that both define node:buffer',
  semanticDelta: {
    addSupportedStatic: 'allocUnsafe(size:number-finite-nonnegative<=16777216): floor length, fresh zeroed owned Buffer, no pool',
    removeUnsupportedStaticOnly: 'allocUnsafe', keepDeferred: ['allocUnsafeSlow', 'copyBytesFrom', 'of', 'compare', 'concat'],
    unchangedExports: base.modules['node:buffer'].exports, unchangedPrototypeMethodGate: 91,
    unchangedLimits: base.modules['node:buffer'].limits, requiredHostInterfaces: [],
    newDeviations: [
      'All visible bytes are guaranteed zero; do not assert reference allocUnsafe initial contents',
      'No slab/pool or shared backing between independent allocations, including positive fractions truncating to zero; byteOffset0 and backing length equals result length',
      'Mutable Buffer.poolSize does not select a pool; current profile default remains0',
      'Cap applies to raw requested numeric size before truncation, so16777216.25 rejects despite reference truncated length16777216',
      'Only allocUnsafe admits positive fractional size truncation; existing alloc size policy remains unchanged',
      'Detailed validation messages differ; TypeError/ERR_INVALID_ARG_TYPE and RangeError/ERR_OUT_OF_RANGE are tested',
      'No allocUnsafeSlow or legacy Buffer constructor expansion follows from this dependency experiment',
    ],
  },
  implementationRoute: [
    'Inside existing createBufferModule, capture the supported native Buffer.alloc value after its definition and before application code; use the candidate validation and Math.trunc contract',
    'Assign a normal constructible function named allocUnsafe with arity1 to the existing constructor slot; remove only that name from the deferred-static installation list',
    'Leave native kernel/allocator ownership and all91 prototype refusals intact; regenerate core factory header via the existing generator',
    'Update the coordinated core version/selection receipt and build a new isolated engine; preserve all old v6 inputs/reports and old-version gates',
    'Synchronize unsupported.mjs::PROFILE_VERSION with the assigned core version, since Buffer/child_process refused-operation errors carry it; version-select the old hardcoded fixture expectation while retaining all91 prototype checks',
  ],
  evidence: { nodeReport: 'node-results.json', nodeReportSha256: hash(await readFile(join(here, 'node-results.json'))),
    componentReport: 'component-results.json', componentReportSha256: hash(await readFile(join(here, 'component-results.json'))),
    differentialGroups: node.differentialGroups, candidateGroups: node.candidateCases.length,
    componentSha256: component.fixture.componentSha256, engineSha256: component.engineSha256,
    hostImports: component.fixture.interfaceAudit.emittedImports, temporaryPatchRestored: true, classicStreamInstalled: false },
  nextGates: ['Coordinator source/contract review and version assignment', 'Actual production factory/schema/generator and new engine gates',
    'Old-version unsupported gate plus next-version allocUnsafe tests selected by receipt', 'Joint host gate and final import audit',
    'Performance/component-size measurements if any speed/memory claim is proposed'],
  remainingClassicStreamDependencies: ['Node abort-listener semantics', 'Boundary-sensitive tick/resource scheduler', 'Declared encoding/backing/remaining Buffer demands'],
  scope: 'Concrete source-based proposed manifest/facade delta only. This file is not a schema-valid selected production manifest and changes no production file.' };
await writeFile(join(here, 'integration-proposal.json'), JSON.stringify(proposal, null, 2)+'\n');
console.log(JSON.stringify({ productionCoreFilesUnchanged: productionUnchanged.length, nextCoreProfileVersion: null,
  proposedStaticOnly: 'allocUnsafe', requiredHostInterfaces: [], component: component.fixture.componentSha256 }));
