import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
// BEGIN FINITE CLASSIC REGISTRAR ORACLE ANCESTRY
export function verifyClassicRegistrarOracle({kind, oracle, requiredNames, registrar, metadata, proof}) {
  const path='builtins/node-compat/register.cpp';
  const before='19eef9879c94e5232238f6df738d57057d384fa025849ee319fcf51eb06eda2b';
  const after='2848f059fb5693aa37c54945bff685444c8431007ceaec59d3335d01f7aced4a';
  const documents={
    assert:{sha:'cbb3bcb3f6bc9e97b12b1a61167483ac0f949de199ae6bd0172926419f4c01a3',required:['assert.mjs','assert-strict.mjs','assert-factories.generated.h','export-manifest.assert.node-v22.14.0.json']},
    querystring:{sha:'e59e05a7cb470970d9bcce230f359cf74bf62a00b094510a2df16d4ab3f901a4',required:['querystring.mjs','querystring-factories.generated.h','export-manifest.querystring.node-v22.14.0.json']},
    util:{sha:'489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816',required:['util.mjs','util-types.mjs','util-core.mjs','util-metadata.mjs','util-unsupported.mjs','export-manifest.util.node-v22.14.0.json','generate-util-factories.mjs','util-factories.generated.h']}
  };
  assert(Object.hasOwn(documents,kind),'Only three pinned strict-script oracles have this registrar ancestry');
  const expected=documents[kind];
  assert.equal(hash(proof.oracleBytes),expected.sha,'Exact unchanged Node oracle document required');
  assert.deepEqual(oracle,JSON.parse(proof.oracleBytes),'Caller oracle differs from captured bytes');
  assert.deepEqual([...requiredNames].sort(),[...expected.required].sort(),'Exact facade-source check set required');
  assert.equal(oracle.registrarSha256,before);
  // Authenticate both policy documents and both exact native patches BEFORE
  // parsing policy rows. The Tick patch never changes register.cpp.
  assert.equal(hash(proof.tickPolicyBytes),'98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0');
  assert.equal(hash(proof.tickPatchBytes),'e286ebeb3f09b438999422dbc2059fed565ef71b98d9f7f62b09291fb5eb5491');
  assert.equal(hash(proof.classicPolicyBytes),'137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f');
  assert.equal(hash(proof.classicPatchBytes),'0574b88e1126e616e4adaac2d7dea4435657c70e2d07a429531218aff24bd73c');
  const tick=JSON.parse(proof.tickPolicyBytes),classic=JSON.parse(proof.classicPolicyBytes);
  assert.equal(tick.version,'sm-private-ticks-source-v1');
  assert.equal(tick.nativePatchSha256,hash(proof.tickPatchBytes));
  assert(!Object.hasOwn(tick.sourceLayer,path),'Tick registrar must remain unchanged');
  assert.equal(classic.parentPolicySha256,hash(proof.tickPolicyBytes));
  assert.equal(classic.parentRecipeSha256,'869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173');
  assert.deepEqual(classic.parentExpectedNativeSourceManifest,tick.expectedNativeSourceManifest);
  assert.equal(tick.expectedNativeSourceManifest.length,306);
  assert.equal(tick.expectedNativeSourceManifest.find(row=>row.path===path)?.sha256,before);
  assert.deepEqual(classic.sourceLayer[path],{beforeSha256:before,afterSha256:after});
  assert.equal(classic.nativePatchSha256,hash(proof.classicPatchBytes));
  assert.equal(classic.expectedNativeSourceManifest.length,342);
  assert.equal(classic.expectedNativeSourceManifest.find(row=>row.path===path)?.sha256,after);
  assert.equal(metadata.buildRecipeSha256,'71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7');
  assert.notEqual(metadata.syntheticMetadataOnly,true);assert.notEqual(metadata.diagnosticOnly,true);
  assert.equal(metadata.classicStreamsEnabled,true);assert.equal(metadata.internalTicksEnabled,true);
  assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
  assert.equal(metadata.classicStreamsPolicy.policyFileSha256,hash(proof.classicPolicyBytes));
  assert.equal(metadata.classicStreamsPolicy.nativePatchSha256,hash(proof.classicPatchBytes));
  assert.equal(metadata.internalTickPolicy.parentPrivateTickPolicyFileSha256,hash(proof.tickPolicyBytes));
  assert.equal(metadata.internalTickPolicy.policyFileSha256,hash(proof.classicPolicyBytes));
  assert.equal(metadata.sourceManifest.length,342);
  const rows=metadata.sourceManifest.map(row=>({path:row.path,sha256:row.sha256}));
  assert.equal(new Set(rows.map(row=>row.path)).size,342);
  assert.deepEqual(rows,classic.expectedNativeSourceManifest,'Actual342 source manifest must match the pinned Classic afterimage');
  assert.equal(hash(registrar),after,'Captured actual registrar must be the exact342 afterimage');
  assert.match(registrar,/options\.setForceStrictMode\(\)/,'Force-strict compilation must remain');
  for(const name of requiredNames)
    assert.equal(rows.find(row=>row.path==='builtins/node-compat/'+name)?.sha256,oracle.sources[name],'Unchanged oracle facade/source '+name);
  return {version:'exact-classic342-registrar-oracle-ancestry-v1',kind,oracleSha256:expected.sha,
    oracleRegistrarSha256:before,actualRegistrarSha256:after,tickRegistrarChanged:false,
    classicPatchSha256:hash(proof.classicPatchBytes),oracleRewritten:false,metadataProjected:false};
}
// END FINITE CLASSIC REGISTRAR ORACLE ANCESTRY
