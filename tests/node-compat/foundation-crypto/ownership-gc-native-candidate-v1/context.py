"""Pure, versioned physical execution contexts; no helper imports or I/O."""
from pathlib import PurePosixPath
ORIGINAL='/Users/dan/dev/StarlingMonkey'
OWN=ORIGINAL+'/tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v1'
NORMAL_SOURCE='/private/tmp/starling-node-compat/crypto-owner-source-v2'
SOURCE='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-source'
WORK='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-build'
FREEZE='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-freeze'
BUILD_OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-build-root'
JOURNAL='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-stage.json'
TOOLS=SOURCE+'/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools'
DONOR_SHA='68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'
RECIPE_SHA='eec3245841fff07e5bf9c3ff7b488106c94b71705262b22272d60a8ea4d7bfb3'
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
NODE='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
NODE_SHA='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
PHASES=('stage','build','freeze','export','bootstrap')
AUTHORITY_STATE='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1'
PEER_STATE='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V1'

def canonical(p):
    assert isinstance(p,str)and p.startswith('/')and '\\'not in p and '\0'not in p
    if p.startswith('/tmp/'):p='/private'+p
    assert str(PurePosixPath(p))==p and all(x not in ('','.','..')for x in p.split('/')[1:])
    return p

def contexts(value):
    expected=dict(configuredSourceRoot=SOURCE,workRoot=WORK,freezeRoot=FREEZE,artifactToolsRoot=TOOLS)
    assert {k:canonical(value[k])for k in expected}==expected
    assert canonical(value['configuredSourceRoot'])!=canonical(value.get('sourceRoot',FREEZE+'/source'))
    return expected.copy()

def phase_model(root,phase,index_sha):
    assert root['schemaVersion']==1 and root['state']==AUTHORITY_STATE
    assert phase in PHASES and root['phase']==phase and root['sourceIndexSha256']==index_sha
    assert root['variant']=='gc-off';contexts(root)
    for p in PHASES:assert root[p+'Allowed']is(p==phase)
    for p in ['guestAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','componentAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:assert root[p]is False
    assert root['nativeSourceFiles']==355 and root['externalEmbeddingSources']==3
    return True

def metadata_model(metadata):
    assert metadata['gcStress']is True and metadata['entropyPolicy']=='off'and metadata['oomTesting']is False
    assert metadata['buildRecipeSha256']==RECIPE_SHA
    assert len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3
    assert metadata['cryptoKeyOwnershipPolicy']['sourceFiles']==355
    assert metadata['cryptoKeyOwnershipPolicy']['runtimeValidation']is None
    for key in ['cmakeCachePath','compileCommandsPath']:
        assert canonical(metadata[key])==metadata[key]and metadata[key].startswith(WORK+'/')
    assert len(metadata['sourceManifest'])==len({r['path']for r in metadata['sourceManifest']})
    return True
