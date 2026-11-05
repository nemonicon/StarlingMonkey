"""Own standard-library source derivation only; never import an owner helper."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PARENT = HERE.parent / 'native-integration-candidate-v2'
PAYLOAD = HERE.parent / 'ownership-secret-failure-candidate-v2'
PEER = HERE.parent / 'independent-ownership-secret-failure-v2-source-review-v1'
PREFIX = str(HERE.relative_to(REPO))
OLD_PREFIX = str(PARENT.relative_to(REPO))
SOURCE = '/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source'
WORK = '/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build'
FREEZE = '/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze'
VERSION = 'sm-webcrypto-secret-failure-owner-source-v2'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def desc(path):
    assert path.is_file() and not path.is_symlink(), path
    raw = path.read_bytes()
    return dict(path=str(path), sha256=sha(raw), bytes=len(raw))


def load(path):
    return json.loads(path.read_bytes())


def put(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value.encode() if isinstance(value, str) else (json.dumps(value, indent=2) + '\n').encode()
    path.write_bytes(raw)
    return desc(path)


derivations = []


def derived(name, source, edits):
    before = source.read_text()
    text = before
    entries = []
    for old, new in edits:
        count = text.count(old)
        assert count, (name, old[:150])
        assert old != new
        text = text.replace(old, new)
        entries.append(dict(before=old, after=new, count=count))
    reverted = text
    for entry in reversed(entries):
        assert reverted.count(entry['after']) == entry['count'], (name, entry)
        reverted = reverted.replace(entry['after'], entry['before'])
    assert reverted == before
    out = put(name, text)
    derivations.append(dict(output=name, donor=desc(source), after=out, edits=entries,
                            forwardAndReverseExact=True))
    return out


def main():
    parent = load(PARENT / 'policy.json')
    payload = load(PAYLOAD / 'source-contract.json')
    peer = load(PEER / 'results.json')
    assert desc(PARENT / 'index.json')['sha256'] == '68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'
    assert desc(PAYLOAD / 'index.json')['sha256'] == '26eddb871e6538277e4b98f3c3912bb4f1c86e9e59640488fb06d457930cce54'
    assert peer['state'] == 'INDEPENDENT_CRYPTO_OWNER355_SECRET_FAILURE_SOURCE_REVIEW_PASSED_V1'
    assert peer['sourceIndexSha256'] == desc(PAYLOAD / 'index.json')['sha256']
    assert peer['sourceOnly'] and peer['sourceReviewPassed'] and not peer['ownerActionsInvoked'] and not peer['runtimeActionsInvoked']
    before = {r['path']: r['sha256'] for r in parent['expectedNativeSourceManifest']}
    after = {r['path']: r['sha256'] for r in payload['expectedNativeSourceManifest']}
    changed = sorted(k for k in before if before[k] != after[k])
    assert len(before) == len(after) == 355 and before.keys() == after.keys()
    assert changed == payload['changedNativeFiles'] and len(changed) == 3
    changes = [dict(path=k, beforeSha256=before[k], afterSha256=after[k],
                    afterimage=desc(PAYLOAD / 'afterimages' / k)) for k in changed]
    source_policy = dict(version=VERSION, parent355Index=desc(PARENT / 'index.json'),
        parent355Policy=desc(PARENT / 'policy.json'), parent355Helper=desc(PARENT / 'layer-policy.py'),
        parent355Recipe=desc(PARENT / 'proposed/tests/node-compat/build-engine.sh'),
        payloadSourceIndex=desc(PAYLOAD / 'index.json'), payloadSourceContract=desc(PAYLOAD / 'source-contract.json'),
        payloadSourcePeer=dict(index=desc(PEER / 'index.json'), result=desc(PEER / 'results.json'),
                               contract=desc(PEER / 'result-contract.json')),
        sourceFiles=355, unchangedParentFiles=352, changedSourceFiles=3, changes=changes,
        inheritedOwnerPolicyRole='Immutable owner/prototype ancestry; current355 bytes are the complete sourceManifest plus this three-file layer',
        addsHostInterfaces=False, addsNodeApi=False, algorithmSurfaceChanged=False,
        lengthPolicyChanged=False, secretCopyPolicyChanged=False, runtimeValidation=None,
        faultInjectionObserved=False, allCopiesErasedClaim=False, operationalAdmission=False,
        parentHoldReview=payload['parentHoldReview'],
        parentRequiredCorrectionContract=payload['parentRequiredCorrectionContract'],
        mandatoryParentHistoryErratum=payload['mandatoryParentHistoryErratum'])
    policy = copy.deepcopy(parent)
    policy['version'] = 'sm-private-ticks-classic-trace-zlib-consumers-crypto-secret-failure-source-v1'
    policy['expectedNativeSourceManifest'] = payload['expectedNativeSourceManifest']
    for k in changed:
        assert policy['sourceLayer'][k]['afterSha256'] == before[k]
        policy['sourceLayer'][k]['afterSha256'] = after[k]
    policy['cryptoSecretFailureSourcePolicy'] = source_policy
    policy_desc = put('policy.json', policy)

    old = "    after={row['path']:row['sha256']for row in POLICY['expectedNativeSourceManifest']}"
    new = "    owner_parent=json.loads((HERE.parent/'native-integration-candidate-v2/policy.json').read_bytes())\n    after={row['path']:row['sha256']for row in owner_parent['expectedNativeSourceManifest']}"
    extra = '''def verify_secret_failure_ancestry():
    contract=POLICY['cryptoSecretFailureSourcePolicy']
    for role in ['parent355Index','parent355Policy','parent355Helper','parent355Recipe','payloadSourceIndex','payloadSourceContract']:
        row=contract[role]
        relative=Path(row['path']).relative_to(Path('/Users/dan/dev/StarlingMonkey'))
        path=HERE.parents[3]/relative
        assert path.is_file() and not path.is_symlink() and path.stat().st_size==row['bytes'] and digest(path)==row['sha256']
    base=json.loads((HERE.parent/'native-integration-candidate-v2/policy.json').read_bytes())
    payload=json.loads((HERE.parent/'ownership-secret-failure-candidate-v2/source-contract.json').read_bytes())
    before={r['path']:r['sha256']for r in base['expectedNativeSourceManifest']}
    after={r['path']:r['sha256']for r in POLICY['expectedNativeSourceManifest']}
    assert len(before)==len(after)==355 and before.keys()==after.keys()
    assert payload['expectedNativeSourceManifest']==POLICY['expectedNativeSourceManifest']
    assert sum(before[k]==after[k]for k in before)==352 and len(contract['changes'])==3
    assert sorted(k for k in before if before[k]!=after[k])==sorted(r['path']for r in contract['changes'])
    for row in contract['changes']:assert before[row['path']]==row['beforeSha256'] and after[row['path']]==row['afterSha256']
    return True
verify_secret_failure_ancestry()
'''
    decoration = """    metadata['cryptoSecretFailureSourcePolicy']=copy.deepcopy(POLICY['cryptoSecretFailureSourcePolicy'])
    secret_cpp=[str(Path(repo)/r['path'])for r in POLICY['cryptoSecretFailureSourcePolicy']['changes']if r['path'].endswith('.cpp')]
    secret_commands=[r['command']for r in entries if r['file']in secret_cpp]
    assert len(secret_commands)==2
    metadata['cryptoSecretFailureBuildEvidence']={'version':'sm-webcrypto-secret-failure-build-evidence-v1','cryptoBuiltinEnabled':True,'changedNativeCompileCommands':secret_commands,'currentSourceManifestValidated':True,'faultInjectionObserved':False,'runtimeValidation':None}
"""
    helper_desc = derived('layer-policy.py', PARENT / 'layer-policy.py', [
        ('Explicit342 source/compile layer; parent306 data is ancestry, never projection.',
         'Exact355 secret-failure source/compile layer; old owner355 is ancestry DATA.'),
        ("POLICY_SHA256='" + sha((PARENT / 'policy.json').read_bytes()) + "'", "POLICY_SHA256='" + policy_desc['sha256'] + "'"),
        (old, new),
        ('verify_crypto_ancestry()\nverify_consumers_ancestry()', extra + 'verify_crypto_ancestry()\nverify_consumers_ancestry()'),
        ("    metadata['cryptoKeyOwnershipPolicy']=copy.deepcopy(POLICY['cryptoKeyOwnershipSourcePolicy'])\n    return metadata",
         "    metadata['cryptoKeyOwnershipPolicy']=copy.deepcopy(POLICY['cryptoKeyOwnershipSourcePolicy'])\n" + decoration + '    return metadata'),
        ('Exact355 consumer source policy verified; no compiler or guest ran',
         'Exact355 secret-failure source policy verified; no compiler or guest ran')])

    recipe = PARENT / 'proposed/tests/node-compat/build-engine.sh'
    guard = '''# This source-only family supports one future initial normal-OFF build.
# An independently reviewed owned controller and fresh Root phase remain required.
[[ "$repo_root" == "''' + SOURCE + '''" ]] || { echo 'Exact separate configured secret source root required' >&2; exit 1; }
[[ "$stress" == 0 && "$entropy_mode" == OFF && "$build_type" == Release && "$oom" == 0 ]] || { echo 'Only initial ordinary Release normal-OFF is implemented in this source candidate' >&2; exit 1; }
[[ "$work_root" == "''' + WORK + '''" ]] || { echo 'Exact separate secret work root required' >&2; exit 1; }
'''
    recipe_desc = derived('proposed/tests/node-compat/build-engine.sh', recipe, [
        ('/tmp/starling-node-compat/crypto-owner-v2-build', WORK),
        (OLD_PREFIX, PREFIX), ('keyowner-v2.', 'secretfailure-v1.'),
        (sha((PARENT / 'layer-policy.py').read_bytes()), helper_desc['sha256']),
        (sha((PARENT / 'policy.json').read_bytes()), policy_desc['sha256']),
        ('layer_root="$repo_root/tests/node-compat/foundation-zlib/native-integration-candidate-v4"',
         guard + 'layer_root="$repo_root/tests/node-compat/foundation-zlib/native-integration-candidate-v4"')])
    pins = copy.deepcopy(load(PARENT / 'admission-pins.json'))
    pins.update(state='UNAPPLIED_CRYPTO_OWNER355_SECRET_FAILURE_BUILD_ONLY_SOURCE_CONTRACT',
        productionRecipeSha256=recipe_desc['sha256'], policySha256=policy_desc['sha256'],
        helperSha256=helper_desc['sha256'], sourceContractVersion=VERSION,
        sourceToolingSuccessor='crypto-owner355-secret-integration-v1',
        secretFailurePayloadIndexSha256=desc(PAYLOAD / 'index.json')['sha256'])
    pins_desc = put('admission-pins.json', pins)
    new_check = """ assert.deepEqual(metadata.cryptoSecretFailureSourcePolicy,policy.cryptoSecretFailureSourcePolicy,'Exact secret-failure layer required');
 const secretEvidence=metadata.cryptoSecretFailureBuildEvidence;
 assert.equal(secretEvidence?.version,'sm-webcrypto-secret-failure-build-evidence-v1');
 assert.equal(secretEvidence.cryptoBuiltinEnabled,true);assert.equal(secretEvidence.currentSourceManifestValidated,true);
 assert.equal(secretEvidence.faultInjectionObserved,false);assert.equal(secretEvidence.runtimeValidation,null);
 assert.deepEqual([...secretEvidence.changedNativeCompileCommands].sort(),policy.cryptoSecretFailureSourcePolicy.changes.filter(row=>row.path.endsWith('.cpp')).map(row=>layout.get(row.path)).sort());
"""
    admission_desc = derived('build-admission.mjs', PARENT / 'build-admission.mjs', [
        (sha((PARENT / 'admission-pins.json').read_bytes()), pins_desc['sha256']),
        (sha(recipe.read_bytes()), recipe_desc['sha256']),
        ('validateCryptoOwnerSourceModel', 'validateCryptoSecretFailureSourceModel'),
        ('validateCryptoOwnerSourceAdmission', 'validateCryptoSecretFailureSourceAdmission'),
        ('validateCryptoOwnerBuildSourceAdmission', 'validateCryptoSecretFailureBuildSourceAdmission'),
        (" assert.deepEqual(metadata.cryptoKeyOwnershipPolicy,policy.cryptoKeyOwnershipSourcePolicy,'Exact new ownership layer; same355 count is not authority');",
         new_check + " assert.deepEqual(metadata.cryptoKeyOwnershipPolicy,policy.cryptoKeyOwnershipSourcePolicy,'Exact inherited ownership ancestry required');"),
        ('CryptoOwner355 operational admission CLOSED:', 'CryptoSecretFailure355 operational admission CLOSED:')])

    frozen_source = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze/source')
    native = []
    for relative, checksum in sorted(after.items()):
        path = PAYLOAD / 'afterimages' / relative if relative in changed else frozen_source / relative
        row = desc(path)
        assert row['sha256'] == checksum
        native.append(dict(path=relative, original=row['path'], sha256=row['sha256'], bytes=row['bytes'],
                           role='CORRECTED_AFTERIMAGE' if relative in changed else 'GENUINE_UNCHANGED_OWNER355_FROZEN_SOURCE'))
    put('native-origins.json', dict(schemaVersion=1, sourceFiles=355, unchangedParentNativeFiles=352,
         changedNativeFiles=3, originalContext=str(frozen_source), files=native))

    # Original-context descriptors remain original. Destination is a separate field.
    tools = {r['path']: copy.deepcopy(r) for r in load(PARENT / 'tool-origins.json')['files']}
    tools['tests/node-compat/build-engine.sh'] = dict(path='tests/node-compat/build-engine.sh',
        original=recipe_desc['path'], sha256=recipe_desc['sha256'], bytes=recipe_desc['bytes'])
    families = [PARENT, PAYLOAD, PEER, HERE.parent/'ownership-secret-failure-candidate-v1',
                HERE.parent/'independent-ownership-secret-failure-source-review-v1']
    for family in families:
        index = load(family / 'index.json')
        names = ['index.json'] + [r['path'] for r in index['files']]
        for name in names:
            d = desc(family / name)
            relative = str((family / name).relative_to(REPO))
            row = dict(path=relative, original=d['path'], sha256=d['sha256'], bytes=d['bytes'])
            if relative in tools:
                assert tools[relative] == row
            tools[relative] = row
    erratum = PAYLOAD.parent/'ownership-secret-failure-candidate-v1-history-erratum.json'
    d = desc(erratum)
    tools[str(erratum.relative_to(REPO))] = dict(path=str(erratum.relative_to(REPO)), original=d['path'], sha256=d['sha256'], bytes=d['bytes'])
    for name in ['policy.json','layer-policy.py','admission-pins.json','build-admission.mjs']:
        d = desc(HERE / name)
        tools[PREFIX+'/'+name] = dict(path=PREFIX+'/'+name, original=d['path'], sha256=d['sha256'], bytes=d['bytes'])
    put('tool-origins.json', dict(schemaVersion=1, state='EXACT_SECRET_FAILURE_SOURCE_BUILD_TOOL_INPUTS',
        inheritedToolRows=922, activeArtifactCommon=None, activeFreezeHelper=None,
        oldArtifactToolRowsRole='Authenticated ancestry DATA; old owner recipe/classifier is not selected for new artifact',
        files=[tools[k] for k in sorted(tools)]))
    put('references.json', dict(schemaVersion=1, sourcePreparationOnly=True,
        families=[dict(index=desc(p/'index.json'), role='INHERITED_IMMUTABLE_SOURCE_DATA') for p in families],
        normalProtectionLedger=desc(HERE.parent/'ownership-secret-failure-candidate-v2/final-input-hashes.json'),
        normalProtection=desc(HERE.parent/'ownership-gc-native-candidate-v2/normal-protection.json'),
        sourcePeer=source_policy['payloadSourcePeer'], mandatoryHistoryErratum=desc(erratum),
        nativeBaseSourceIndex=desc(HERE.parent/'ownership-gc-native-candidate-v2/index.json'),
        inheritedRecipe=desc(recipe), sourceRootOriginal=str(frozen_source),
        configuredSourceRoot=SOURCE, workRoot=WORK, freezeRoot=FREEZE,
        artifactCommonSelector='Not implemented; future explicit complete relative path + exact descriptor only',
        reviewOrExecutionAuthority=False))
    put('derivations.json', dict(schemaVersion=1, exactTextDerivations=derivations,
        policyTransformation=dict(parent=desc(PARENT/'policy.json'), output=policy_desc,
            fieldsChanged=['version','expectedNativeSourceManifest','sourceLayer[three crypto files].afterSha256','cryptoSecretFailureSourcePolicy'],
            nativePathsPreserved=355, unchangedNativeHashes=352, correctedNativeHashes=3),
        policyAncestryNotEngineMetadata=True, globalContextRebinding=False))
    print(json.dumps(dict(prepared=True, ownActionsInvoked=False, nativeFiles=355,
        sourceFilesChanged=3, toolRows=len(tools), textDerivations=len(derivations))))


if __name__ == '__main__':
    main()
