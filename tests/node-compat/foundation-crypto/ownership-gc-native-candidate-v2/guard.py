"""No producer imports. Genuine per-phase authority and complete source checks."""
from pathlib import Path
import importlib.util,json,sys
import context as C
from data_io import descriptor,indexed,read,regular,safe
DONOR_SHA=C.DONOR_SHA
def protection(document):
    for r in document['originals']:regular(r['original']);regular(r['frozen'])
    for r in document['frozenCopyEntries']:regular(r)
    root=Path(document['freezeReceipt']['path']).parent
    if str(root).startswith('/tmp/'):root=Path('/private'+str(root))
    regular(document['freezeReceipt'])
    assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(document['requiredNormalFreezeMembership'])
def recheck(frame):
    # Bind the actual frame field to the authenticated config and captured Root row.
    assert frame['rootAuthority']==read(frame['captured'][0])['rootAuthority']
    assert frame['rootAuthority']==frame['captured'][1]
    for row in frame['captured']:regular(row)
    protection(frame['normalProtection'])
def authorize(config_descriptor,phase):
    config=read(config_descriptor);own_row=config['sourceIndex'];assert own_row['path']==C.OWN+'/index.json'
    own,own_rows=indexed(own_row);assert own['sourceOnly']is True
    own_root=Path(C.OWN)
    assert {p.relative_to(own_root).as_posix()for p in own_root.rglob('*')if p.is_file()}=={r['path']for r in own['files']}|{'index.json'}
    assert all(not p.is_symlink()for p in own_root.rglob('*'))
    root_row=config['rootAuthority'];root=read(root_row);C.phase_model(root,phase,own_row['sha256'])
    peer=root['independentSourceReview'];_,peer_rows=indexed(peer['index']);data=read(peer['result'])
    assert sum(r==peer['result']for r in peer_rows)==1
    assert data['state']==C.PEER_STATE and data['sourceIndexSha256']==own_row['sha256']and data['sourceOnly']is True and data['sourceReviewPassed']is True and data['ownerActionsInvoked']is False
    inputs=read(next(r for r in own_rows if r['path']==C.OWN+'/stage-inputs.json'))
    assert len(inputs['files'])==1311 and len({r['path']for r in inputs['files']})==1311
    for r in inputs['files']:
        safe(r['path']);assert r['original']['path']==C.NORMAL_SOURCE+'/'+r['path']and type(r['mode'])is int and 0<=r['mode']<=0o777
    normal=read(next(r for r in own_rows if r['path']==C.OWN+'/normal-protection.json'))
    refs=read(next(r for r in own_rows if r['path']==C.OWN+'/references.json'))
    captured=[config_descriptor,root_row,*own_rows,*peer_rows]
    for r in refs['pinnedInputs']:regular(r);captured.append(r)
    for row in inputs['files']:regular(row['original']);captured.append(row['original'])
    if phase!='stage':
        stage_result=read(root['actualStageResult']);assert stage_result['state']=='CRYPTO_OWNER355_GC_SOURCE_STAGE_COMPLETE_UNREVIEWED_V1' and stage_result['sourceIndexSha256']==own_row['sha256']and stage_result['destination']==C.SOURCE
        stage_peer=root['independentStageReview'];_,stage_peer_rows=indexed(stage_peer['index']);stage_peer_data=read(stage_peer['result'])
        assert sum(r==stage_peer['result']for r in stage_peer_rows)==1 and stage_peer_data['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_STAGE_REVIEW_PASSED_V1'and stage_peer_data['verifiedPassed']is True and stage_peer_data['actualStageResult']==root['actualStageResult']and stage_peer_data['sourceIndexSha256']==own_row['sha256']and stage_peer_data['configuredSourceRoot']==C.SOURCE
        captured += [root['actualStageResult'],*stage_peer_rows]
        for r in inputs['files']:
            d=dict(path=C.SOURCE+'/'+r['path'],sha256=r['original']['sha256'],bytes=r['original']['bytes']);regular(d);captured.append(d)
    if phase in ('freeze','export','bootstrap'):
        assert root['actualBuildResult']['path']==C.BUILD_OUTPUT+'/result.json'
        built=read(root['actualBuildResult']);assert built['sourceIndexSha256']==own_row['sha256']and built['state']=='native-build-completed-runtime-pending'and built['rawChildExitCode']==0 and built['lifecycleComplete']is True and built['ownedGroupCleanup']['complete']is True and built['allOriginalNormalAndStageBytesPreserved']is True
        outer=read(root['actualBuildExternalTerminal']);assert outer['rawExitCode']==0 and outer['timeout']is False and outer['parentOwnedGroupGone']is True and outer['authority']==built['rootAuthority']
        regular(outer['stdout']);regular(outer['stderr']);assert outer['stderr']['bytes']==0
        captured += [root['actualBuildResult'],root['actualBuildExternalTerminal'],outer['stdout'],outer['stderr']]
    frame=dict(root=root,rootAuthority=root_row,sourceIndex=own_row,peerIndex=peer['index'],peerResult=peer['result'],captured=captured,normalProtection=normal,stageInputs=inputs,references=refs,configuredSourceRoot=C.SOURCE,artifactToolsRoot=C.TOOLS,freezeRoot=C.FREEZE,label='gc-off',capsules=[*own_rows,root_row,*peer_rows])
    recheck(frame);return frame
def load_common(frame):
    recheck(frame);path=Path(C.TOOLS)/'artifact_common.py'
    expected=next(r for r in frame['stageInputs']['files']if r['path'].endswith('/artifact-tools/artifact_common.py'))['original']
    regular(dict(path=str(path),sha256=expected['sha256'],bytes=expected['bytes']))
    spec=importlib.util.spec_from_file_location('isolated_gc_staged_artifact_common',path);common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
    assert common.HERE==Path(C.TOOLS)and common.REPO==Path(C.SOURCE)
    # The unchanged donor OUTPUT stays its historical default. Never rebind it.
    assert common.OUTPUT==Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
    common.tool_dependencies(common.REPO);recheck(frame);return common
def validate_admission(v):assert v['state']=='ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'and v['sourceFiles']==355 and v['engineBytesRead']is False
def validate_receipt_roles(receipt,active_sha,donor_sha):
    inventory={r['path']:r for r in receipt['copies']};active=receipt['activeFreezerTooling'];donor=receipt['donorFreezerTooling']
    assert active['path']==C.FREEZE+'/artifact-tools/freeze-engine.py'and active['sha256']==active_sha==receipt['helperSha256']
    assert donor['path']==C.FREEZE+'/artifact-tools/donor-data/freeze-engine.py'and donor['sha256']==donor_sha
    assert inventory[active['path']]['sha256']==active_sha and inventory[donor['path']]['sha256']==donor_sha
