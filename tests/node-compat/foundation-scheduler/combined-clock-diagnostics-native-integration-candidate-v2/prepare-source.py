"""Source derivation only; never stages, imports a producer, or builds native code."""
from pathlib import Path
import copy,hashlib,json
OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
PARENT=OWN.parent/'combined-native-build-controller-candidate-v2'
PRIOR=OWN.parent/'combined-clock-diagnostics-native-integration-candidate-v1'
DIAG=OWN.parent/'combined-clock-diagnostics-candidate-v2'
SOURCE='/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-source'
WORK='/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-build'
FREEZE='/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-freeze'
ANCESTRY='/private/tmp/starling-node-compat/combined-native355-v2-freeze/source'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(path):
 path=Path(path);b=path.read_bytes();return dict(path=str(path),sha256=sha(b),bytes=len(b))
def read(path):return json.loads(Path(path).read_bytes())
def save(name,value):
 p=OWN/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
DERIVATIONS=[]
def derived(name,original,edits):
 before=Path(original).read_text();after=before
 for old,new,count in edits:
  assert after.count(old)==count,(name,old,after.count(old),count)
  after=after.replace(old,new)
 reverse=after
 for old,new,count in reversed(edits):
  assert reverse.count(new)==count,(name,'reverse',new,reverse.count(new),count)
  reverse=reverse.replace(new,old)
 assert reverse==before
 (OWN/name).write_text(after)
 DERIVATIONS.append(dict(path=name,original=row(original),after=row(OWN/name),edits=[dict(before=a,after=b,count=c)for a,b,c in edits],forwardAndInverseVerified=True))

def main():
 plan=read(PRIOR/'integration-plan.json');inventory=read(DIAG/'proposed-source-inventory.json')
 native=[dict(path=r['path'],sha256=r['origin']['sha256'])for r in inventory['native']]
 external=[dict(path=r['path'],sha256=r['origin']['sha256'])for r in inventory['externalEmbedding']]
 base=read(PARENT/'policy.json')
 assert len(native)==357 and len(external)==3 and len(plan['sharedNativeTUs'])==6
 parent={r['path']:r['sha256']for r in base['expectedNativeSourceManifest']};current={r['path']:r['sha256']for r in native}
 changes=[dict(path=p,beforeSha256=parent[p],afterSha256=current[p])for p in sorted(parent)if parent[p]!=current[p]]
 added=[dict(path=p,sha256=current[p])for p in sorted(current.keys()-parent.keys())]
 assert len(changes)==6 and len(added)==2 and sum(parent[p]==current[p]for p in parent)==349
 extension=read(PRIOR/'recipe-insertions.json')
 # The entire unchanged 300KB parent policy remains authenticated ancestry DATA.
 spec=dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_OWN_SOURCE_POLICY_V2',basePolicy=row(PARENT/'policy.json'),
  contexts=dict(configuredSourceRoot=SOURCE,workRoot=WORK,freezeRoot=FREEZE),
  expectedNativeSourceManifest=native,expectedComponentizeSourceManifest=external,
  expectedRawMetadataFields=sorted(plan['sourceDerivedBaseMetadataFields']+plan['newTopLevelMetadataFields']),
  diagnosticSourcePolicy=dict(version='sm-clock-lifecycle-diagnostic357-source-v2',diagnosticOnly=True,
   parentExpectedNativeSourceManifest=base['expectedNativeSourceManifest'],changes=changes,added=added,
   sourceIndex=row(DIAG/'index.json'),sourcePeerIndex=row(OWN.parent/'independent-combined-clock-diagnostics-v2-source-review-v1/index.json'),
   sdkSyntaxIndex=row(OWN.parent/'combined-clock-diagnostics-sdk-syntax-v2/index.json'),
   sharedNativeTUs=plan['sharedNativeTUs'],externalSharedTU='embedding/embedding.cpp',
   privateBuiltin='starling:test-clock-lifecycle',publicSelectedWholeManifests=base['selectedModuleManifests'],
   privateModuleAddedToPublicManifest=False,sourceDefaultsOff=True,namedBuildDiagnosticsOn=True,
   parentEmbedding=base['expectedComponentizeSourceManifest'],externalManifest=external,
   embeddingPatch=row(PRIOR/'embedding-diagnostic.UNAPPLIED.patch'),
   fullSeventeenGatesAccepted=False,runtimeValidation=None,operationalAdmission=False))
 assert len(spec['expectedRawMetadataFields'])==len(set(spec['expectedRawMetadataFields']))==82
 model=Path(PARENT/'native-admission-model.py')
 model_edits=[('Pure full355 metadata-shape gate','Pure own357/82 diagnostic metadata-shape gate',1),
  ("== 355","== 357",1),("== 68","== 69",1),("== 62","== 63",2),
  ("'ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'","'ACTUAL_FRESH_CLOCK_DIAGNOSTIC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V2'",1),
  ("    return {'state':'FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',\n            'nativeFiles':355,'engineRead':False,'runtimeAccepted':False,'grantsAuthority':False}",
   "    validate_diagnostic_fields(metadata,policy)\n    assert set(metadata)==set(policy['expectedRawMetadataFields']) and len(metadata)==82\n    return {'state':'FINITE_CLOCK_DIAGNOSTIC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V2',\n            'nativeFiles':357,'rawMetadataFields':82,'engineRead':False,'runtimeAccepted':False,'grantsAuthority':False}",1)]
 derived('native-admission-model.py',model,model_edits)
 with(OWN/'native-admission-model.py').open('a')as f:f.write((OWN/'model-extension.template.py').read_text())
 # The extension is a literal independent implementation in the NEW model.
 spec['admissionModelSha256']=row(OWN/'native-admission-model.py')['sha256'];save('policy.json',spec)
 policy_sha=row(OWN/'policy.json')['sha256']
 helper=(PARENT/'layer-policy.py').read_text()
 top=helper[helper.index('REPO='):helper.index('\ndef expected(')]
 new_top="""REPO=Path('SOURCE')
ANCESTRY=Path('ANCESTRY')
DONOR_INPUTS=ANCESTRY/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/donor-inputs.json'
POLICY_SHA256='POLICY_HASH'
AUTH_SHA256='c837e8eb61329370775e0a24b0c914a6efe6bfcb3e51a03a8ed2ecd41fa807db'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert digest(HERE/'policy.json')==POLICY_SHA256
SPEC=json.loads((HERE/'policy.json').read_bytes())
base_path=Path(SPEC['basePolicy']['path']);assert base_path.is_file()and not base_path.is_symlink()
assert base_path.stat().st_size==SPEC['basePolicy']['bytes']and digest(base_path)==SPEC['basePolicy']['sha256']
PARENT_POLICY=json.loads(base_path.read_bytes())
model_path=HERE/'native-admission-model.py';assert digest(model_path)==SPEC['admissionModelSha256']
model_spec=importlib.util.spec_from_file_location('own_clock357_source_policy_model',model_path)
model=importlib.util.module_from_spec(model_spec);model_spec.loader.exec_module(model)
POLICY=model.assemble_policy(SPEC,PARENT_POLICY)
def authenticate_inputs():
    assert digest(DONOR_INPUTS)==AUTH_SHA256
    rows=json.loads(DONOR_INPUTS.read_bytes())['files']
    assert len(rows)==len({r['path']for r in rows})
    for r in rows:
        path=ANCESTRY
        for part in r['path'].split('/'):
            assert part and part not in('.','..');path/=part;assert not path.is_symlink(),path
        assert path.is_file()and path.stat().st_size==r['bytes']and digest(path)==r['sha256'],path
    return True
authenticate_inputs()
BASE_ROOT=ANCESTRY/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1'
BASE=json.loads((BASE_ROOT/'policy.json').read_bytes())
ANCESTOR_ROOT=ANCESTRY/'tests/node-compat/foundation-scheduler/integration-candidate-v1'
ANCESTOR=json.loads((ANCESTOR_ROOT/'policy.json').read_bytes())
assert BASE['expectedNativeSourceManifest']==PARENT_POLICY['combinedSourcePolicy']['parentExpectedNativeSourceManifest']
parent_before={r['path']:r['sha256']for r in BASE['expectedNativeSourceManifest']}
parent_after={r['path']:r['sha256']for r in PARENT_POLICY['expectedNativeSourceManifest']}
assert len(parent_before)==len(parent_after)==355 and parent_before.keys()==parent_after.keys()
assert sum(parent_before[p]==parent_after[p]for p in parent_before)==348
for r in PARENT_POLICY['combinedSourcePolicy']['changes']:assert parent_before[r['path']]==r['beforeSha256']and parent_after[r['path']]==r['afterSha256']
for key in ('cryptoKeyOwnershipSourcePolicy','cryptoSecretFailureSourcePolicy','streamConsumersSourcePolicy','zlibSourcePolicy'):
    assert POLICY[key]==BASE[key]
assert POLICY['parentExpectedNativeSourceManifest']==ANCESTOR['expectedNativeSourceManifest']
""".replace("'SOURCE'",repr(SOURCE)).replace("'ANCESTRY'",repr(ANCESTRY)).replace('POLICY_HASH',policy_sha)
 # Parent source resolution is preserved, then the explicit diagnostic delta applies.
 old_expected=helper[helper.index('def expected('):helper.index('\ndef resolved(')]
 new_expected=old_expected.replace('    if entry is None:return parent\n    assert entry[\'beforeSha256\']==parent,\'Actual306 source ancestry mismatch: \'+relative\n    return entry[\'afterSha256\']',"    if entry is not None:\n        assert entry['beforeSha256']==parent,'Actual306 source ancestry mismatch: '+relative\n        parent=entry['afterSha256']\n    diagnostic={r['path']:r for r in POLICY['diagnosticSourcePolicy']['changes']}.get(relative)\n    if diagnostic is not None:\n        assert diagnostic['beforeSha256']==parent\n        parent=diagnostic['afterSha256']\n    return parent")
 assert new_expected!=old_expected
 new_decorate="""    classification=model.classify_diagnostic_commands(POLICY,database,embedding_commands,metadata['requestedCMakeOptions'],metadata['observedCMakeOptions'])
    namespace='NS_DEF(diagnostics::clock_lifecycle)'
    assert install_text.count(namespace)==1
    metadata['clockLifecycleDiagnosticSourcePolicy']=copy.deepcopy(POLICY['diagnosticSourcePolicy'])
    metadata['clockLifecycleDiagnosticBuildEvidence']={'diagnosticOnly':True,'actualSharedCompileCommands':classification,'actualInstallation':{'path':str(install),'sha256':digest(install),'namespace':namespace,'count':1,'performanceTargetEnabled':values['ENABLE_BUILTIN_WEB_PERFORMANCE']=='ON'},'actualPolicyCpp':len(native),'actualDatabaseRows':len(database),'actualNodePrivateCpp':len(private),'actualSeparateEmbeddingCpp':len(embedding_commands),'actualLinkedInlineStateIdentityProved':False,'actualStrongGetterLinkProved':False,'nativeClockOrSelectorRuntimeInvoked':False,'fullSeventeenGateAccepted':False,'runtimeValidation':None,'operationalAdmission':False}
    authenticate_inputs()
    return metadata"""
 helper_edits=[('Full current355 source/compile producer','Full own diagnostic357 source/compile producer',1),(top,new_top,1),(old_expected,new_expected,1),
  ("assert len(rows)==len({r['path']for r in rows})==355","assert len(rows)==len({r['path']for r in rows})==357",1),("'Unreviewed combined355 source: '","'Unreviewed clock diagnostic357 source: '",1),
  ("path=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py'","path=ANCESTRY/'tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py'",1),
  ('assert len(cpp)==62','assert len(cpp)==63',1),
  ("assert digest(Path(source_dir)/'embedding/embedding.cpp')==POLICY['embedding']['afterSha256']","assert digest(Path(source_dir)/'embedding/embedding.cpp')==POLICY['expectedComponentizeSourceManifest'][0]['sha256']",1),
  ('==68','==69',1),('len(native)==62','len(native)==63',1),
  ("'actualCompileDatabaseRows':68","'actualCompileDatabaseRows':69",1),
  ('ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1','ACTUAL_FRESH_CLOCK_DIAGNOSTIC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V2',1),
  ('    authenticate_inputs()\n    return metadata',new_decorate,1)]
 derived('layer-policy.py',PARENT/'layer-policy.py',helper_edits)
 helper_sha=row(OWN/'layer-policy.py')['sha256']
 recipe=(PARENT/'build-engine.sh').read_text()
 patch_hash=spec['diagnosticSourcePolicy']['embeddingPatch']['sha256'];ext_sha=external[0]['sha256']
 recipe_edits=[('/private/tmp/starling-node-compat/combined-native355-v1-source',SOURCE,2),
  ('/private/tmp/starling-node-compat/combined-native355-v2-build',WORK,2),
  (str(PARENT),str(OWN),2),('combined355-v2.','clock-diagnostic357-v2.',2),
  ('ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1','ACTUAL_FRESH_CLOCK_DIAGNOSTIC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V2',1),
  (row(PARENT/'layer-policy.py')['sha256'],helper_sha,5),(row(PARENT/'policy.json')['sha256'],policy_sha,2),
  ("classification==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False)","classification==dict(state='FINITE_CLOCK_DIAGNOSTIC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V2',nativeFiles=357,rawMetadataFields=82,engineRead=False,runtimeAccepted=False,grantsAuthority=False)",1),
  ("\n\nsm_variant=release",'\nclock_patch="$consumers_layer_root/embedding-diagnostic.UNAPPLIED.patch"\n[[ "$(sha256_file "$clock_patch")" == '+patch_hash+' ]] || exit 1\npatch -p1 -d "$source_dir" < "$clock_patch"\n[[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == '+ext_sha+' ]] || exit 1\n\nsm_variant=release',1),
  ("'sha256':'9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205'","'sha256':'"+ext_sha+"'",1),
  ('-DENABLE_BUILTIN_WEB_TIMERS=ON -DENABLE_BUILTIN_WEB_CRYPTO=ON \\','-DENABLE_BUILTIN_WEB_TIMERS=ON -DENABLE_BUILTIN_WEB_CRYPTO=ON \\\n  -DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=ON -DENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE=ON -DENABLE_BUILTIN_WEB_PERFORMANCE=ON \\',1),
  ("    'CMAKE_C_COMPILER_LAUNCHER':'', 'CMAKE_CXX_COMPILER_LAUNCHER':'',","    'CMAKE_C_COMPILER_LAUNCHER':'', 'CMAKE_CXX_COMPILER_LAUNCHER':'',\n    'NODE_COMPAT_LIFECYCLE_DIAGNOSTICS':'ON','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE':'ON','ENABLE_BUILTIN_WEB_PERFORMANCE':'ON',",1),
  ("assert digest(pathlib.Path(source_dir) / 'embedding/embedding.cpp') == layer.POLICY['embedding']['afterSha256']","assert digest(pathlib.Path(source_dir) / 'embedding/embedding.cpp') == layer.POLICY['expectedComponentizeSourceManifest'][0]['sha256']\nmetadata['componentizeJsPatches'].append({'name':'clock-lifecycle-same-tu-diagnostics-v2','path':str(layer.HERE/'embedding-diagnostic.UNAPPLIED.patch'),'sha256':digest(layer.HERE/'embedding-diagnostic.UNAPPLIED.patch'),'baseRevision':componentize,'applied':True,'files':['embedding/embedding.cpp']})",1)]
 derived('build-engine.sh',PARENT/'build-engine.sh',recipe_edits)
 text=(OWN/'build-engine.sh').read_text()
 # The parent gate precedes the last real field. Move the new exact82 gate AFTER
 # privateRustupBootstrapPolicy construction; no old80/83 frame is transformed.
 start=text.index('# New355-only raw metadata shape gate')
 end=text.index('before_rustup=',start)
 gate=text[start:end].replace('New355-only','Own diagnostic357/82').replace('actual_combined355_metadata_shape','actual_clock_diagnostic357_metadata_shape')
 text=text[:start]+text[end:]
 anchor="with open(artifact + '.build.json', 'x') as output:"
 assert text.count(anchor)==1;text=text.replace(anchor,gate+anchor)
 (OWN/'build-engine.sh').write_text(text)
 (OWN/'embedding-diagnostic.UNAPPLIED.patch').write_bytes((PRIOR/'embedding-diagnostic.UNAPPLIED.patch').read_bytes())
 for d in DERIVATIONS:
  d['intermediate']=d.pop('after');d['after']=row(OWN/d['path'])
 save('derivations.json',dict(schemaVersion=1,files=DERIVATIONS,recipeFinalGateRelocation='Exact82 classifier moved after real last Rustup field and before exclusive sidecar publication',modelLiteralExtension=row(OWN/'model-extension.template.py')))
 save('contexts.json',dict(schemaVersion=1,sourceRoot=SOURCE,workRoot=WORK,freezeRoot=FREEZE,ancestryRoot=ANCESTRY,baselineRevision='54b3329b3ce818fd1f244e871e9c259b63667cda',metadataFields=82,nativeFiles=357,externalEmbeddingSources=3,selectedWholeManifests=11,rootAuthority=None,sourcePeer=None,actualStage=None,actualBuild=None,actualMetadata=None))
 print(json.dumps(dict(policy=row(OWN/'policy.json'),helper=row(OWN/'layer-policy.py'),recipe=row(OWN/'build-engine.sh'),model=row(OWN/'native-admission-model.py'))))
if __name__=='__main__':main()
