#!/usr/bin/env python3
"""Source-only independent Python reader. Never executes reviewed JS or producers."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import stat
import traceback

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
REPOSITORY = FAMILY.parents[2]
ACTUAL = FAMILY/'production-regression-activated-v2'
AMENDMENT = FAMILY/'registrar-ancestry-oracle-amendment-v1'
PRODUCER = FAMILY/'replay-activation-candidate-v2'
PARENT = FAMILY/'production-regression-candidate-v1'
SHA = {
    'actual':'a011b0431691a670f3f67a965a1a6360528bea68b9997cd803b40be11f748ecf',
    'amendment':'7462f1255f4fd5048e345a96d58908c8e6251158bf36e5ab4450dab97be193b4',
    'producer':'afd5a7148f0a7737e919d84cf8e97d224e4f8e5126b8e46e498444ac3f3cf4f5',
    'parent':'81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029',
    'producerParent':'118999fade2d96cd10fe88445245e4eaf86392809ff21551a912f1e3030adcad',
    'tickPolicy':'98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0',
    'tickPatch':'e286ebeb3f09b438999422dbc2059fed565ef71b98d9f7f62b09291fb5eb5491',
    'classicPolicy':'137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f',
    'classicPatch':'0574b88e1126e616e4adaac2d7dea4435657c70e2d07a429531218aff24bd73c',
    'beforeRegistrar':'19eef9879c94e5232238f6df738d57057d384fa025849ee319fcf51eb06eda2b',
    'afterRegistrar':'2848f059fb5693aa37c54945bff685444c8431007ceaec59d3335d01f7aced4a',
}
ORACLES = {
    'assert':('cbb3bcb3f6bc9e97b12b1a61167483ac0f949de199ae6bd0172926419f4c01a3',['assert.mjs','assert-strict.mjs','assert-factories.generated.h','export-manifest.assert.node-v22.14.0.json']),
    'querystring':('e59e05a7cb470970d9bcce230f359cf74bf62a00b094510a2df16d4ab3f901a4',['querystring.mjs','querystring-factories.generated.h','export-manifest.querystring.node-v22.14.0.json']),
    'util':('489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816',['util.mjs','util-types.mjs','util-core.mjs','util-metadata.mjs','util-unsupported.mjs','export-manifest.util.node-v22.14.0.json','generate-util-factories.mjs','util-factories.generated.h']),
}
checked = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def regular(path, expected=None, size=None):
    path = Path(os.path.abspath(path))
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), str(path)
    assert size is None or before.st_size == size, str(path)
    data = path.read_bytes()
    after = path.lstat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns) == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns), str(path)
    row = {'path':str(path),'sha256':digest(data),'bytes':len(data)}
    assert expected is None or row['sha256'] == expected, str(path)
    assert str(path) not in checked or checked[str(path)] == row
    checked[str(path)] = row
    return data


def document(path, expected=None):
    return json.loads(regular(path,expected))


def indexed(root, expected, count):
    index = document(root/'index.json',expected)
    rows = {row['path']:row for row in index['files']}
    assert len(rows) == len(index['files']) == count
    for name,row in rows.items():
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        path = root/relative
        cursor = path
        while cursor != root:
            assert not cursor.is_symlink(), str(cursor)
            cursor = cursor.parent
        assert not root.is_symlink()
        regular(path,row['sha256'],row['bytes'])
    return index


def transform(before, edits):
    after = before
    applications = []
    for edit in edits:
        assert edit['old'], 'No ambiguous empty source match'
        assert after.count(edit['old']) == edit.get('occurrences',1), edit['old']
        positions = [match.start() for match in re.finditer(re.escape(edit['old']),after)]
        delta = len(edit['new'])-len(edit['old'])
        applications.append((edit,[position+number*delta for number,position in enumerate(positions)],after))
        after = after.replace(edit['old'],edit['new'])
    reverse = after
    for edit,positions,previous in reversed(applications):
        for position in reversed(positions):
            assert reverse[position:position+len(edit['new'])] == edit['new']
            reverse = reverse[:position]+edit['old']+reverse[position+len(edit['new']):]
        assert reverse == previous
    assert reverse == before
    return after


def unified(text):
    lines = text.splitlines(keepends=True)
    result = {}
    cursor = 0
    while cursor < len(lines):
        assert lines[cursor].startswith('--- ')
        old_name = lines[cursor][4:].strip()
        cursor += 1
        assert lines[cursor].startswith('+++ ')
        new_name = lines[cursor][4:].strip()
        cursor += 1
        name = new_name[2:] if new_name.startswith('b/') else new_name
        hunks = []
        while cursor < len(lines) and not lines[cursor].startswith('--- '):
            match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[cursor])
            assert match, lines[cursor]
            old_start,old_count,new_start,new_count = [int(value) if value is not None else 1 for value in match.groups()]
            cursor += 1
            body = []
            while cursor < len(lines) and not lines[cursor].startswith(('@@ ','--- ')):
                assert lines[cursor][0] in ' +-'
                body.append(lines[cursor])
                cursor += 1
            assert sum(line[0] in ' -' for line in body) == old_count
            assert sum(line[0] in ' +' for line in body) == new_count
            hunks.append((old_start,old_count,new_start,new_count,body))
        assert name not in result
        result[name] = {'old':old_name,'new':new_name,'hunks':hunks}
    return result


def patched(data, patch, reverse=False):
    source = data.decode().splitlines(keepends=True)
    result, cursor = [],0
    for old_start,old_count,new_start,new_count,body in patch['hunks']:
        start,count = (new_start,new_count) if reverse else (old_start,old_count)
        offset = start - 1 if count else start
        assert cursor <= offset <= len(source)
        result += source[cursor:offset]
        expected = [line[1:] for line in body if line[0] in (' +' if reverse else ' -')]
        replacement = [line[1:] for line in body if line[0] in (' -' if reverse else ' +')]
        assert source[offset:offset+count] == expected
        result += replacement
        cursor = offset+count
    result += source[cursor:]
    return ''.join(result).encode()


def main():
    indexed(ACTUAL,SHA['actual'],81)
    indexed(AMENDMENT,SHA['amendment'],18)
    indexed(PRODUCER,SHA['producer'],13)
    indexed(PARENT,SHA['parent'],174)
    prior_producer = FAMILY/'replay-activation-candidate-v1'
    indexed(prior_producer,SHA['producerParent'],17)
    source = document(ACTUAL/'source-receipt.json')
    assert source['parentIndexSha256'] == SHA['parent'] and source['producerIndexSha256'] == SHA['producer']
    assert source['registrarOracleAmendmentIndexSha256'] == SHA['amendment']
    assert source['inheritedBodies'] == 64 and source['oldBodiesByteIdentical'] == 62 and source['changedHostHarnessBodies'] == 2
    assert source['guestSemanticBodiesChanged'] is source['guestOrHostExecuted'] is source['runtimeAcceptanceClaim'] is False
    amendment_proof = document(AMENDMENT/'transformation-proof.json')
    assert regular(ACTUAL/'registrar-ancestry-proof.json') == regular(AMENDMENT/'transformation-proof.json')
    expected_changed = {'release/helpers/native-scalar-harness.mjs','release/runners/path.mjs'}
    assert {row['path'] for row in amendment_proof['records']} == expected_changed
    assert amendment_proof['oldBodiesByteIdentical'] == 62 and amendment_proof['changedHostHarnessBodies'] == 2
    assert amendment_proof['guestSemanticBytesChanged'] is amendment_proof['oracleDocumentsChanged'] is False
    afterimages = {}
    for row in amendment_proof['records']:
        name = row['path']
        before = regular(AMENDMENT/'before'/name,row['beforeSha256'])
        assert before == regular(PARENT/name,row['beforeSha256'])
        after = regular(AMENDMENT/'proposed'/name,row['afterSha256'])
        assert transform(before.decode(),row['edits']).encode() == after
        assert regular(ACTUAL/name,row['afterSha256']) == after
        afterimages[name] = row['afterSha256']
    derivations = document(ACTUAL/'derivations.json')
    assert regular(ACTUAL/'derivations.json') == regular(PARENT/'derivations.json')
    records = derivations['records']
    assert len({row['destinationPath'] for row in records}) == len(records) == 64
    unchanged,changed = [],[]
    for row in records:
        original = regular(REPOSITORY/row['sourcePath'],row['beforeSha256'])
        before = regular(PARENT/row['destinationPath'],row['afterSha256'])
        assert transform(original.decode(),row['edits']).encode() == before
        actual = regular(ACTUAL/row['destinationPath'])
        expected = afterimages.get(row['destinationPath'],row['afterSha256'])
        assert digest(actual) == expected == source['publishedBodyHashes'][row['destinationPath']]
        assert source['inheritedBodyHashes'][row['destinationPath']] == row['afterSha256']
        (unchanged if actual == before else changed).append(row['destinationPath'])
    assert len(unchanged) == 62 and set(changed) == expected_changed
    producer_proof = document(PRODUCER/'derivation-proof.json')
    before = regular(prior_producer/'activate.py',producer_proof['beforeProducerSha256'])
    after = regular(PRODUCER/'activate.py',producer_proof['afterProducerSha256'])
    assert transform(before.decode(),producer_proof['edits']).encode() == after
    for row in producer_proof['unchangedBackendFiles']:
        assert regular(PRODUCER/row['path'],row['sha256']) == regular(prior_producer/row['path'],row['sha256'])
    # Extract the exact finite guard afterimage and inspect its fail-closed checks.
    helper = regular(ACTUAL/'release/helpers/native-scalar-harness.mjs').decode()
    begin = '// BEGIN FINITE CLASSIC REGISTRAR ORACLE ANCESTRY\n'
    end = '// END FINITE CLASSIC REGISTRAR ORACLE ANCESTRY\n'
    guard = helper[helper.index(begin):helper.index(end)+len(end)]
    reference = regular(AMENDMENT/'guard-source.mjs').decode()
    assert guard == reference[reference.index(begin):reference.index(end)+len(end)]
    required_guard_fragments = [
        "assert(Object.hasOwn(documents,kind)", "assert.equal(hash(proof.oracleBytes),expected.sha",
        "assert.deepEqual(oracle,JSON.parse(proof.oracleBytes)","assert.deepEqual([...requiredNames].sort(),[...expected.required].sort()",
        "assert.equal(oracle.registrarSha256,before)", "assert(!Object.hasOwn(tick.sourceLayer,path)",
        "assert.equal(classic.parentPolicySha256,hash(proof.tickPolicyBytes))",
        "assert.deepEqual(classic.parentExpectedNativeSourceManifest,tick.expectedNativeSourceManifest)",
        "assert.equal(metadata.buildRecipeSha256,'71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7')",
        "assert.notEqual(metadata.syntheticMetadataOnly,true);assert.notEqual(metadata.diagnosticOnly,true)",
        "assert.equal(metadata.classicStreamsEnabled,true);assert.equal(metadata.internalTicksEnabled,true)",
        "assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release')",
        "assert.equal(new Set(rows.map(row=>row.path)).size,342)",
        "assert.deepEqual(rows,classic.expectedNativeSourceManifest",
        "assert.equal(hash(registrar),after", "assert.match(registrar,/options\\.setForceStrictMode\\(\\)/",
        "assert.equal(rows.find(row=>row.path==='builtins/node-compat/'+name)?.sha256,oracle.sources[name]",
    ]
    assert all(fragment in guard for fragment in required_guard_fragments)
    parse_position = guard.index('const tick=JSON.parse(proof.tickPolicyBytes),classic=JSON.parse(proof.classicPolicyBytes);')
    for field,key in [('tickPolicyBytes','tickPolicy'),('tickPatchBytes','tickPatch'),('classicPolicyBytes','classicPolicy'),('classicPatchBytes','classicPatch')]:
        token = "assert.equal(hash(proof."+field+"),'"+SHA[key]+"')"
        assert token in guard and guard.index(token) < parse_position
    assert 'metadataProjection' not in helper and not re.search(r'\bmetadata\.\w+\s*=(?!=)',guard)
    assert "const metadataBytes = await readFile(engine+'.build.json'), metadata = JSON.parse(metadataBytes);" in helper
    assert 'evidence.registrarOracleAncestry = verifyClassicRegistrarOracle({kind,oracle,requiredNames,registrar,metadata,proof:registrarProof});' in helper
    # Independently authenticate and reconstruct the recorded native lineage.
    compat = REPOSITORY/'tests/node-compat'
    tick = document(compat/'foundation-scheduler/integration-candidate-v1/policy.json',SHA['tickPolicy'])
    classic = document(FAMILY/'integration-candidate-v1/policy.json',SHA['classicPolicy'])
    tick_patch = unified(regular(compat/'foundation-scheduler/taskqueue-owner-v2/starling-taskqueue-ticks.UNAPPLIED.patch',SHA['tickPatch']).decode())
    classic_patch = unified(regular(FAMILY/'implementation-candidate-v1-allocation-order-amendment/native-integration.corrected.UNAPPLIED.patch',SHA['classicPatch']).decode())
    registrar_name = 'builtins/node-compat/register.cpp'
    assert tick['version'] == 'sm-private-ticks-source-v1' and registrar_name not in tick['sourceLayer'] and registrar_name not in tick_patch
    assert tick['nativePatchSha256'] == SHA['tickPatch'] and classic['nativePatchSha256'] == SHA['classicPatch']
    assert classic['parentPolicySha256'] == SHA['tickPolicy']
    assert classic['parentRecipeSha256'] == '869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
    assert classic['parentExpectedNativeSourceManifest'] == tick['expectedNativeSourceManifest']
    parent_map = {row['path']:row['sha256'] for row in tick['expectedNativeSourceManifest']}
    after_map = {row['path']:row['sha256'] for row in classic['expectedNativeSourceManifest']}
    assert len(parent_map) == 306 and len(after_map) == 342
    assert parent_map[registrar_name] == SHA['beforeRegistrar'] and after_map[registrar_name] == SHA['afterRegistrar']
    rebuilt = dict(parent_map)
    for name,row in classic['sourceLayer'].items():
        assert rebuilt.get(name) == row['beforeSha256']
        rebuilt[name] = row['afterSha256']
    assert rebuilt == after_map and len(classic['addedSourcePaths']) == 36
    freeze = Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze')
    metadata = document(freeze/'normal-off.engine.wasm.build.json','873c47f7d75776d836f642a971164b8751c6a53d56430c3a84f0cf3c161b8f58')
    assert [{key:row[key] for key in ['path','sha256']} for row in metadata['sourceManifest']] == classic['expectedNativeSourceManifest']
    native_bytes = {name:regular(freeze/'source'/name,sha) for name,sha in after_map.items()}
    assert b'options.setForceStrictMode()' in native_bytes[registrar_name]
    tick_bytes = {name:data for name,data in native_bytes.items() if name in parent_map}
    patch_reconstructions = []
    for name,patch in classic_patch.items():
        before = patched(native_bytes[name],patch,reverse=True)
        assert digest(before) == parent_map[name] and patched(before,patch) == native_bytes[name]
        tick_bytes[name] = before
        patch_reconstructions.append({'path':name,'beforeSha256':digest(before),'afterSha256':digest(native_bytes[name]),'roundTripExact':True})
    assert set(classic_patch) == {registrar_name,'cmake/builtins.cmake'}
    assert len(tick_patch) == 7 and set(tick_patch) == set(tick['sourceLayer'])
    for name,patch in tick_patch.items():
        after = tick_bytes[name]
        assert digest(after) == tick['sourceLayer'][name]['afterSha256']
        before = patched(after,patch,reverse=True)
        expected = tick['sourceLayer'][name]['beforeSha256']
        assert (before == b'' if expected is None else digest(before) == expected)
        assert patched(before,patch) == after
    oracle_results = []
    for kind,(sha,names) in ORACLES.items():
        oracle_path = compat/('foundation-'+kind)/'native-node-results.json'
        oracle = document(oracle_path,sha)
        assert oracle['node'] == 'v22.14.0' and oracle['registrarSha256'] == SHA['beforeRegistrar']
        assert all(after_map['builtins/node-compat/'+name] == oracle['sources'][name] for name in names)
        for name,source_sha in oracle['sources'].items():
            regular(freeze/'source/builtins/node-compat'/name,source_sha)
            regular(REPOSITORY/'builtins/node-compat'/name,source_sha)
        runner = regular(ACTUAL/('release/runners/'+kind+'.mjs')).decode()
        assert 'verifyOracleSources(oracle,' in runner
        oracle_results.append({'kind':kind,'document':checked[str(oracle_path)],'guardRequiredFacadeFiles':len(names),'allOracleSourceHashesUnchanged':len(oracle['sources']),'oldRegistrar':SHA['beforeRegistrar']})
    # Path subprocesses select existing sealed safe copies; every write target in
    # those exact pinned sources is the explicit fresh oracleOutput directory.
    path_runner = regular(ACTUAL/'release/runners/path.mjs').decode()
    assert "const oracleScripts = resolve(here, '../foundation-scheduler/production-release-runner-v3/oracles');" in path_runner
    assert "const oracleOutput = join(output, 'node-oracles');" in path_runner
    assert "await mkdir(oracleOutput, { recursive: false });" in path_runner
    assert "{ cwd: repository, encoding: 'utf8', timeout: 30000, env: { ...process.env, NODE_COMPAT_PATH_ORACLE_OUTPUT: oracleOutput } }" in path_runner
    assert path_runner.count("hash(await readFile(join(oracleScripts,file))),oracleSourcePins[file]") == 2
    safe_scripts = []
    for name,sha,writes in [('semantic.mjs','23fe6d8eed334a3eae580655d9a859a048f0097bcd957259cf4218a230701cbf',2),('glob.mjs','befc3e984b1b82e33ad008943e85a2461dca424e9f1d27561edfdeda455df619',3)]:
        path = compat/'foundation-scheduler/production-release-runner-v3/oracles'/name
        text = regular(path,sha).decode()
        assert sha in path_runner and "assert(process.env.NODE_COMPAT_PATH_ORACLE_OUTPUT, 'Explicit fresh oracle output required');" in text
        assert "const oracleOutput = resolve(process.env.NODE_COMPAT_PATH_ORACLE_OUTPUT);" in text
        assert text.count('await writeFile(') == text.count('await writeFile(join(oracleOutput,') == writes
        assert not re.search(r'writeFile\(join\(here\b',text)
        safe_scripts.append(checked[str(path)])
    # The five historical output bytes are evidence, not regenerated here.
    amendment_inputs = document(AMENDMENT/'input-freeze.json')
    historic_names = {'lexical-vectors.json','semantic-results.json','glob-vectors.json','glob-results.json','glob-differences.json'}
    historical = []
    for row in amendment_inputs['inputs']:
        path = Path(row['path'])
        if path.parent == compat/'foundation-path' and path.name in historic_names:
            regular(path,row['sha256'],row['bytes'])
            historical.append(checked[str(path)])
    assert len(historical) == 5
    for root,key in [(ACTUAL,'actual'),(AMENDMENT,'amendment'),(PRODUCER,'producer')]:
        regular(root/'index.json',SHA[key])
    return {
        'schemaVersion':1,'state':'SUPPLEMENTARY_ACTIVATED_REGRESSION_V2_SOURCE_REVIEW_PASSED',
        'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'actualIndex':checked[str(ACTUAL/'index.json')],'amendmentIndex':checked[str(AMENDMENT/'index.json')],
        'producerIndex':checked[str(PRODUCER/'index.json')],
        'indexedFilesRehashed':{'actual':81,'amendment':18,'producer':13,'parent':174,'producerParent':17},
        'inheritedDerivationsReconstructedForwardAndReverse':64,'oldBodiesByteIdentical':62,
        'changedHostHarnessBodies':sorted(changed),'exactAmendmentAfterimages':afterimages,
        'producerEditsReconstructedForwardAndReverse':len(producer_proof['edits']),
        'finiteGuard':{'sourceSha256':digest(guard.encode()),'exactGuardAfterimage':True,'supportedKinds':list(ORACLES),'unknownKindRejectedByOwnPropertyAssertion':True,'unknownNativeLineageRejectedByExact342ManifestAssertion':True,'policyAndPatchAuthenticationPrecedesParsing':True,'guardMetadataProjection':False,'oldRegistrarSha256':SHA['beforeRegistrar'],'actualRegistrarSha256':SHA['afterRegistrar'],'tickSourceRows':306,'classicSourceRows':342,'classicSourcesRehashed':342,'classicNativePatchRoundTrips':patch_reconstructions,'tickNativePatchExactRoundTrips':7},
        'oracleAndFacadeEvidence':oracle_results,'safePathOracleScripts':safe_scripts,'historicalPathOutputsUnchanged':historical,
        'guestSemanticBodiesChanged':False,'oracleDocumentsChanged':False,'reviewedCodeExecuted':False,
        'nodeGuestHostBuildTranspilePreflightOrProducerExecuted':False,
        'limitations':['Assertions were inspected and source/data relationships were checked with independent Python. This reader did not dynamically exercise the JavaScript guard or spawn Path oracles.','Historical Node test results and native build metadata are preserved evidence, not executions observed by this reader.','Only source lineage and finite afterimages are reviewed here; root/capability input seals and native tuple authorization belong to the enclosing review.'],
    }


if __name__ == '__main__':
    previous = []
    result_path = HERE/'supplementary-source-results.json'
    if result_path.exists():
        prior = json.loads(result_path.read_bytes())
        previous = prior.get('readerMistakesPreserved',[])
    try:
        result = main()
    except Exception:
        mistake = {'readerSha256':digest(Path(__file__).read_bytes()),'readerSource':Path(__file__).read_text(),'traceback':traceback.format_exc()}
        previous.append(mistake)
        result_path.write_text(json.dumps({'schemaVersion':1,'state':'SUPPLEMENTARY_SOURCE_READER_FAILED_REQUIRES_CORRECTION','readerMistakesPreserved':previous},indent=2)+'\n')
        raise
    verified = {'schemaVersion':1,'files':sorted(checked.values(),key=lambda row:row['path'])}
    data = (json.dumps(verified,indent=2)+'\n').encode()
    (HERE/'supplementary-source-verified-files.json').write_bytes(data)
    result['verifiedFiles'] = {'path':'supplementary-source-verified-files.json','sha256':digest(data),'bytes':len(data),'count':len(verified['files'])}
    result['readerMistakesPreserved'] = previous
    result_path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['state','inheritedDerivationsReconstructedForwardAndReverse','oldBodiesByteIdentical','changedHostHarnessBodies']}))
