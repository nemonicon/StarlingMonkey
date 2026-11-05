"""Dormant two-phase tooling guard; no custom imports or actions at import."""
from pathlib import Path
import hashlib,importlib.util,json,sys,os
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/ownership-gc-pin-tooling-candidate-v1'
NATIVE=REPO/'tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v2'
NATIVE_SHA='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05'
SOURCE='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source'
WORK='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build'
FREEZE='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze'
TOOLS=SOURCE+'/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools'
NORMAL='/private/tmp/starling-node-compat/crypto-owner-source-v2'
BUILD_OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build-root'
NATIVE_RELATIVE='tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools/artifact_common.py'
HELPER_SHA='fff7bed72aec0c592e7a788060a5c1ecf6a0b0694ca519dbfa00e230584123ab'
PEER_STATE='INDEPENDENT_CRYPTO_OWNER355_GC_PIN_TOOLING_SOURCE_REVIEW_PASSED_V1'

def checked(row):
    assert type(row) is dict and set(row) == {'path', 'sha256', 'bytes'}
    assert type(row['path']) is str and type(row['bytes']) is int and row['bytes'] >= 0
    assert type(row['sha256']) is str and len(row['sha256']) == 64 and all(c in '0123456789abcdef' for c in row['sha256'])
    path = Path(row['path'])
    assert path.is_absolute() and '..' not in path.parts
    physical = Path('/private' + str(path)) if str(path).startswith('/tmp/') else path
    for ancestor in (physical, *physical.parents):
        assert not ancestor.is_symlink()
    before = physical.stat()
    assert physical.is_file()
    digest = hashlib.sha256()
    with physical.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = physical.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    assert before.st_size == row['bytes'] and digest.hexdigest() == row['sha256']
    return path

def read(row):
    assert row['bytes'] <= 32 * 1024 * 1024
    path = checked(row)
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    return json.loads(raw)

def family(row):
    index = read(row)
    root = Path(row['path']).parent
    rows = [row]
    names = set()
    for member in index['files']:
        name = member['path']
        assert name not in names and name and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        child = dict(path=str(root / name), sha256=member['sha256'], bytes=member['bytes'])
        checked(child)
        rows.append(child)
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'}
    return rows

def recheck(captured, family_indices):
    for row in captured:
        checked(row)
    for row in family_indices:
        family(row)

def select_helper(inputs, configured, tools, normal):
    assert str(Path(tools) / 'artifact_common.py') == str(Path(configured) / NATIVE_RELATIVE)
    matches = [r for r in inputs['files'] if r['path'] == NATIVE_RELATIVE]
    assert len(matches) == 1, 'Exactly one full-relative crypto helper row is required'
    row = matches[0]
    assert row['original'] == dict(path=str(Path(normal) / NATIVE_RELATIVE),sha256=HELPER_SHA,bytes=19299)
    return dict(path=str(Path(configured) / NATIVE_RELATIVE),sha256=HELPER_SHA,bytes=19299)

def validate_phase(value,config,native,phase):
    assert phase in ('export','bootstrap')
    assert value['schemaVersion']==1 and value['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_GC_PIN_TOOLING_PHASE_V1'
    assert value['phase']==phase and value['nativeSourceIndexed']==config['sourceIndex'] and value['nativeSourceIndexed']['sha256']==NATIVE_SHA
    assert value['toolingIndexed']==config['toolingIndex'] and value['nativeRootAuthority']==config['rootAuthority']
    assert value['configuredSourceRoot']==SOURCE and value['artifactToolsRoot']==TOOLS and value['workRoot']==WORK and value['freezeRoot']==FREEZE
    assert value['nativeSourceFiles']==355 and value['externalEmbeddingSources']==3
    assert value['artifactReview']==native['independentGcNativeReview']
    assert value['externalParentDeadlineSeconds']==native['externalParentDeadlineSeconds']==2400
    assert value['externalControllerIndex']==config['toolingIndex']
    assert value['externalControllerEntry']['path']==str(OWN/'controller.py') and value['externalControllerEntry'] in family(config['toolingIndex'])
    assert value['externalOutputRoot']=='/private/tmp/starling-node-compat/crypto-owner355-gc-pin-tooling-v1-'+phase+'-external-root'
    assert value['nativePhaseEntry']['path']==str(OWN/'action.py') and value['nativePhaseEntry'] in family(config['toolingIndex'])
    assert native['pinToolingEntry']==value['nativePhaseEntry'] and native['pinToolingSourceIndex']==config['toolingIndex']
    assert native['pinToolingReview']==value['independentSourceReview']
    assert native['schemaVersion']==1 and native['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1'
    assert native['phase']==phase and native['sourceIndexSha256']==NATIVE_SHA and native['variant']=='gc-off'
    assert native['configuredSourceRoot']==SOURCE and native['artifactToolsRoot']==TOOLS and native['workRoot']==WORK and native['freezeRoot']==FREEZE
    assert native['nativeSourceFiles']==355 and native['externalEmbeddingSources']==3
    for p in ('stage','build','freeze','export','bootstrap'):
        assert native[p+'Allowed']is(p==phase)
    for p in ('export','bootstrap'):assert value[p+'Allowed']is(p==phase)
    for k in ('engineExecutionAllowed','guestAllowed','keyOperationsAllowed','gcWorkloadAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'):
        assert value[k] is False
    for k in ('guestAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','componentAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed'):
        assert native[k] is False
    if phase=='export':
        assert value['actualExportReview'] is None
        assert value['pinCandidateOutput']==native['pinCandidateOutput']==BUILD_OUTPUT+'/gc-pin.UNREVIEWED.json'
        for k in ('reviewedGcPins','gcNativeRootReview'):
            assert value[k] is None and native[k] is None
    else:
        assert value['pinCandidateOutput'] is None and native['pinCandidateOutput'] is None
        assert value['reviewedGcPins']==native['reviewedGcPins'] and value['gcNativeRootReview']==native['gcNativeRootReview']
        assert isinstance(value['reviewedGcPins'],dict) and isinstance(value['gcNativeRootReview'],dict)
        assert isinstance(value['actualExportReview'],dict)


def validate_peer(value,own):
    assert value['schemaVersion']==1 and value['state']==PEER_STATE
    assert value['sourceIndexSha256']==own['sha256'] and value['nativeSourceIndexSha256']==NATIVE_SHA
    assert value['sourceOnly']is True and value['sourceReviewPassed']is True and value['ownerActionsInvoked']is False


def validate_artifact(proof,root,freeze,receipt_row):
    assert proof['schemaVersion']==1 and proof['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_ARTIFACT_REVIEW_PASSED_V1'
    assert proof['verifiedPassed']is True and proof['sourceIndexSha256']==NATIVE_SHA
    assert proof['nativeSourceFiles']==355 and proof['variant']=='gc-off'
    assert proof['engineSha256']==freeze['engineSha256']==root['engine']['sha256']
    assert proof['freezeReceiptSha256']==receipt_row['sha256']
    assert root['metadata']['sha256']==freeze['metadataSha256'] and root['engine']['bytes']==freeze['engineBytes']


def authorize(config_row,phase):
    config=read(config_row);own=config['toolingIndex']
    assert own['path']==str(OWN/'index.json') and config['sourceIndex']['path']==str(NATIVE/'index.json') and config['sourceIndex']['sha256']==NATIVE_SHA
    own_rows=family(own);native_rows=family(config['sourceIndex'])
    own_data=read(own);assert own_data['sourceOnly']is True
    root_row=config['rootAuthority'];root=read(root_row)
    tooling_row=config['toolingRootAuthority'];assert tooling_row!=root_row
    tooling=read(tooling_row);validate_phase(tooling,config,root,phase)
    captured=[config_row,root_row,tooling_row,*own_rows,*native_rows];families=[own,config['sourceIndex']]
    refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')))
    for item in refs['families']:
        captured+=family(item['index']);families.append(item['index'])
    for row in refs['files']:checked(row);captured.append(row)
    prep=read(next(r for r in own_rows if r['path']==str(OWN/'input-freeze.json')))
    assert len(prep['files'])==len({r['path']for r in prep['files']})
    for row in prep['files']:checked(row);captured.append(row)
    peer=tooling['independentSourceReview'];peer_rows=family(peer['index']);assert peer['result']in peer_rows
    validate_peer(read(peer['result']),own);captured+=peer_rows;families.append(peer['index'])
    artifact=tooling['artifactReview'];artifact_rows=family(artifact['index']);assert artifact['result']in artifact_rows
    proof=read(artifact['result']);freeze=read(refs['actualFreezeRootObservation']);receipt_row=refs['actualFreezeReceipt']
    assert tooling['actualFreezeRootObservation']==refs['actualFreezeRootObservation'] and tooling['freezeReceipt']==receipt_row
    validate_artifact(proof,root,freeze,receipt_row)
    checked(receipt_row);captured+=[*artifact_rows,receipt_row];families.append(artifact['index'])
    # Read-only pin authority is additional, not inherited from a normal/consumer pin.
    if phase=='bootstrap':
        for row in (root['reviewedGcPins'],root['gcNativeRootReview']):checked(row);captured.append(row)
    protection=read(next(r for r in own_rows if r['path']==str(OWN/'build-output-protection.json')))
    candidate_row=None
    if phase=='bootstrap':
        pair=tooling['actualExportReview'];export_rows=family(pair['index']);assert pair['result'] in export_rows
        exported=read(pair['result']);validate_export_proof(exported,own,tooling['artifactReview'])
        candidate_row=exported['candidate'];checked(candidate_row)
        captured += [*export_rows,candidate_row];families.append(pair['index'])
    protect_output(protection,candidate_row)
    for row in protection['files']:captured.append(row)
    recheck(captured,families)
    assert not any(k in sys.modules for k in ('context','data_io','guard','pin_model'))
    sys.path.insert(0,str(NATIVE))
    spec=importlib.util.spec_from_file_location('genuine_crypto_gc_native_guard',NATIVE/'guard.py')
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    assert Path(native.C.__file__).resolve()==NATIVE/'context.py'
    assert Path(sys.modules['data_io'].__file__).resolve()==NATIVE/'data_io.py'
    assert native.C.SOURCE==SOURCE and native.C.TOOLS==TOOLS and native.C.FREEZE==FREEZE
    frame=native.authorize(config_row,phase)
    assert frame['sourceIndex']==config['sourceIndex']
    frame['toolingFrame']=dict(index=own,rootAuthority=tooling_row,independentSourceReview=peer,artifactReview=artifact,captured=captured,families=families,phase=phase,protection=protection,expectedCandidate=candidate_row,actualExportReview=tooling['actualExportReview'])
    frame['_nativeGuard']=native
    frame['captured']+=captured
    recheck_frame(frame);return frame


def recheck_frame(frame):
    tooling=frame['toolingFrame'];config=read(tooling['captured'][0])
    assert frame['sourceIndex']==config['sourceIndex'] and frame['sourceIndex']['sha256']==NATIVE_SHA
    assert tooling['index']==config['toolingIndex'] and tooling['rootAuthority']==config['toolingRootAuthority']
    frame['_nativeGuard'].recheck(frame);recheck(tooling['captured'],tooling['families'])
    protect_output(tooling['protection'],tooling['expectedCandidate'])


def load_common(frame):
    recheck_frame(frame)
    row=select_helper(frame['stageInputs'],SOURCE,TOOLS,NORMAL);checked(row)
    spec=importlib.util.spec_from_file_location('genuine_staged_crypto_pin_tooling_common',row['path'])
    common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
    assert common.HERE==Path(TOOLS) and common.REPO==Path(SOURCE)
    assert common.OUTPUT==Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
    common.tool_dependencies(common.REPO)
    frame['selectedCommonHelper']=row
    recheck_frame(frame);return common


def provenance(frame):
    tooling=frame['toolingFrame']
    return dict(nativeSourceIndexed=frame['sourceIndex'],nativeRootAuthority=frame['rootAuthority'],
        toolingIndexed=tooling['index'],toolingRootAuthority=tooling['rootAuthority'],
        independentToolingSourceReview=tooling['independentSourceReview'],independentNativeArtifactReview=tooling['artifactReview'],
        selectedCommonHelper=frame['selectedCommonHelper'],actualExportReview=tooling['actualExportReview'],phase=tooling['phase'],engineExecuted=False,operationalAdmission=False)


def validate_export_proof(value,own,artifact):
    assert value['schemaVersion']==1 and value['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_PIN_EXPORT_REVIEW_PASSED_V1'
    assert value['verifiedPassed']is True and value['sourceIndexSha256']==own['sha256'] and value['nativeSourceIndexSha256']==NATIVE_SHA
    assert value['independentNativeArtifactReview']==artifact
    assert value['candidate']['path']==BUILD_OUTPUT+'/gc-pin.UNREVIEWED.json'
    assert value['engineExecuted']is False and value['operationalAdmission']is False and value['pinsAdopted']is False


def protect_output(document,candidate=None):
    assert document['schemaVersion']==1 and document['root']==BUILD_OUTPUT
    rows=document['files'];assert len(rows)==len({r['path']for r in rows})==3
    assert {Path(r['path']).name for r in rows}=={'build.log','launch.json','result.json'}
    for row in rows:assert str(Path(row['path']).parent)==BUILD_OUTPUT;checked(row)
    expected={r['path']for r in rows}
    if candidate is not None:
        assert candidate['path']==BUILD_OUTPUT+'/gc-pin.UNREVIEWED.json';checked(candidate);expected.add(candidate['path'])
    root=Path(BUILD_OUTPUT)
    assert not root.is_symlink()
    assert all(p.is_file() and not p.is_symlink() for p in root.iterdir())
    assert {str(p)for p in root.iterdir()}==expected,'Existing build output preserved; exactly one named candidate may be added'
