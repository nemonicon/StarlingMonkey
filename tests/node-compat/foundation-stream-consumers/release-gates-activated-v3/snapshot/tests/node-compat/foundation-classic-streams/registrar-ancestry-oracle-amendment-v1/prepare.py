"""Derive two host-admission/orchestration corrections. No guest/tool loader."""
from pathlib import Path
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
PARENT = BASE/'production-regression-candidate-v1'
GUARD = r'''// BEGIN FINITE CLASSIC REGISTRAR ORACLE ANCESTRY
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
'''


def sha(data): return hashlib.sha256(data).hexdigest()


def main():
    records=[];patch=[]
    name='release/helpers/native-scalar-harness.mjs'
    before=(PARENT/name).read_text()
    insert="export const hash = value => createHash('sha256').update(value).digest('hex');\n"
    load="""  const registrarProof = {
    oracleBytes: await readFile(join(here,'native-node-results.json')),
    tickPolicyBytes: await readFile(join(repository,'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json')),
    tickPatchBytes: await readFile(join(repository,'tests/node-compat/foundation-scheduler/taskqueue-owner-v2/starling-taskqueue-ticks.UNAPPLIED.patch')),
    classicPolicyBytes: await readFile(join(repository,'tests/node-compat/foundation-classic-streams/integration-candidate-v1/policy.json')),
    classicPatchBytes: await readFile(join(repository,'tests/node-compat/foundation-classic-streams/implementation-candidate-v1-allocation-order-amendment/native-integration.corrected.UNAPPLIED.patch'))
  };
"""
    edits=[{'old':insert,'new':insert+'\n'+GUARD},
      {'old':'  const builtinManifests = selectedManifestsForEngine(metadata, { sourceRoot });\n',
       'new':'  const builtinManifests = selectedManifestsForEngine(metadata, { sourceRoot });\n'+load},
      {'old':"    assert.equal(hash(registrar), oracle.registrarSha256, 'Native registrar must match strict-script oracle receipt');",
       'new':'    evidence.registrarOracleAncestry = verifyClassicRegistrarOracle({kind,oracle,requiredNames,registrar,metadata,proof:registrarProof});'}]
    records.append(derive(name,before,edits,patch))
    name='release/runners/path.mjs';before=(PARENT/name).read_text()
    edits=[{'old':"const oracleScripts = resolve(dirname(fileURLToPath(import.meta.url)), '../oracles');",
      'new':"const oracleScripts = resolve(here, '../foundation-scheduler/production-release-runner-v3/oracles');\nconst oracleSourcePins = { 'semantic.mjs': '"+sha((BASE.parent/'foundation-scheduler/production-release-runner-v3/oracles/semantic.mjs').read_bytes())+"', 'glob.mjs': '"+sha((BASE.parent/'foundation-scheduler/production-release-runner-v3/oracles/glob.mjs').read_bytes())+"' };"},
      {'old':"  const result = spawnSync(process.execPath, [...flags, join(oracleScripts, file)], { encoding: 'utf8', timeout: 30000, env: { ...process.env, NODE_COMPAT_PATH_ORACLE_OUTPUT: oracleOutput } });",
       'new':"  assert.equal(hash(await readFile(join(oracleScripts,file))),oracleSourcePins[file],'Exact inherited Node oracle subprocess source');\n  const result = spawnSync(process.execPath, [...flags, join(oracleScripts, file)], { cwd: repository, encoding: 'utf8', timeout: 30000, env: { ...process.env, NODE_COMPAT_PATH_ORACLE_OUTPUT: oracleOutput } });\n  assert.equal(hash(await readFile(join(oracleScripts,file))),oracleSourcePins[file],'Node oracle source changed during subprocess');"}]
    edits.append({'old': "['lexical-vectors.json', 'glob-vectors.json'].includes(path) ? join(oracleOutput, path) : join(here, path)", 'new': "['lexical-vectors.json', 'glob-vectors.json'].includes(path) ? join(oracleOutput, path) : ['semantic.mjs', 'glob.mjs'].includes(path) ? join(oracleScripts, path) : join(here, path)", 'occurrences': 2})
    records.append(derive(name,before,edits,patch))
    (HERE/'guard-source.mjs').write_text("import assert from 'node:assert/strict';\nimport {createHash} from 'node:crypto';\nconst hash=bytes=>createHash('sha256').update(bytes).digest('hex');\n"+GUARD)
    (HERE/'host-oracle-admission.UNAPPLIED.patch').write_text(''.join(patch))
    (HERE/'transformation-proof.json').write_text(json.dumps({'schemaVersion':1,'state':'TWO_HOST_HARNESS_CORRECTIONS_NOT_GUEST_SEMANTICS','parentIndexSha256':'81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029','records':records,'oldBodiesByteIdentical':62,'changedHostHarnessBodies':2,'guestSemanticBytesChanged':False,'oracleDocumentsChanged':False},indent=2)+'\n')


def derive(name,before,edits,patch):
    after=before
    for edit in edits:
        assert after.count(edit['old'])==edit.get('occurrences',1)
        after=after.replace(edit['old'],edit['new'])
    reverse=after
    for edit in reversed(edits):
        assert reverse.count(edit['new'])==edit.get('occurrences',1)
        reverse=reverse.replace(edit['new'],edit['old'])
    assert reverse==before
    for root,data in [('before',before),('proposed',after)]:
        p=HERE/root/name;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('x')as stream:stream.write(data)
    patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    return {'path':name,'beforeSha256':sha(before.encode()),'afterSha256':sha(after.encode()),'edits':edits,'exactReverseProof':True}


if __name__=='__main__':main()
