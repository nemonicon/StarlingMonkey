"""Seal proposal/current input bytes only. No producer or target action mains."""
from pathlib import Path
import ast
import hashlib
import json
import os
import stat
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
FAMILY=HERE.parent
def sha(data):return hashlib.sha256(data).hexdigest()
def encode(data):return (json.dumps(data,indent=2)+'\n').encode()
def main():
    assert not(HERE/'index.json').exists()and not(HERE/'input-freeze.json').exists()
    contract=json.loads((HERE/'contract.json').read_bytes())
    expected_indices={
      'trace-semantics-candidate-v1':'59c9233c5dd1c9f07c4da16a79abdb58abc9775b37c714f6af179e85f23f0631',
      'independent-trace-semantics-source-review-v1':'b00a6097c266d110a60ab7fcbe2ab72ed6cf4736192c19ebdc342660c964938f',
      'independent-stream-trace-component-review-v1':'7db35421ab2d46830e0d60b6eb007a0bda801207dc692e8bfd3bc8a83ee1ff84',
      'measurement-producer-candidate-v1':'35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc'}
    rows={};relocations=[]
    changed=json.loads((HERE/'policy.json').read_bytes())['classicTraceSourcePolicy']['changes']
    snapshots={(REPO/row['path']).resolve():(HERE/'ancestry/native-before'/row['path']).resolve()for row in changed}
    def add(path,role,digest=None,size=None,historical_preimage=False):
        path=Path(path).resolve(strict=True)
        if historical_preimage and path in snapshots:
            original=path;path=snapshots[path]
            relocations.append({'original':str(original),'snapshot':os.path.relpath(path,HERE),'role':role,'reason':'Explicit immutable preimage copy; original may later become the approved afterimage. No engine metadata is projected.'})
        before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
        raw=path.read_bytes();after=path.lstat()
        assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
        assert digest is None or sha(raw)==digest,str(path)
        assert size is None or len(raw)==size,str(path)
        key=str(path)
        row={'path':os.path.relpath(path,HERE),'sha256':sha(raw),'bytes':len(raw),'roles':[role]}
        if key in rows:
            old=rows[key];assert old['sha256']==row['sha256']and old['bytes']==row['bytes'];old['roles']=sorted(set(old['roles']+[role]))
        else:rows[key]=row
        return raw
    fix=FAMILY/'trace-semantics-candidate-v1'
    for name,digest in expected_indices.items():
        packet=FAMILY/name;index=json.loads(add(packet/'index.json','immutable-source-or-review-index',digest))
        for row in index['files']:add(packet/row['path'],'immutable-source-or-review-packet',row['sha256'],row['bytes'])
    fix_inputs=json.loads((fix/'input-freeze.json').read_bytes())
    assert len(fix_inputs['inputs'])==488
    for row in fix_inputs['inputs']:add(fix/row['path'],'reviewed-fix-consumed-preimage-or-ordinary-host-evidence',row['sha256'],row['bytes'],True)
    old=json.loads((HERE/'ancestry/policy.json').read_bytes())
    for row in old['expectedNativeSourceManifest']:add(REPO/row['path'],'previous342-source-preimage',row['sha256'],historical_preimage=True)
    tools=json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes())
    prefix='tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/'
    for row in tools['toolDependencies']:
        name=row['path']
        if name.startswith(prefix):path=HERE/name[len(prefix):]
        elif(HERE/'source'/name).is_file():path=HERE/'source'/name
        else:path=REPO/name
        add(path,'proposed-effective-tool-input',row['sha256'],row['bytes'])
    runtime=FAMILY/'production-runtime-activated-v3'
    pins=json.loads(add(runtime/'runtime-pins.json','historical-four-native-authority','c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'))
    add(runtime/'root-review-receipt.json','historical-four-native-root-authority','1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56')
    counts={}
    for label,pin in pins['variants'].items():
        assert len(pin['frozenFiles'])==405
        for row in pin['frozenFiles']:add(row['path'],'historical-unaltered-'+label+'-freeze',row['sha256'],row['bytes'])
        add(pin['freezeReceiptPath'],'historical-unaltered-'+label+'-freeze-receipt',pin['freezeReceiptSha256'])
        counts[label]=405
    root_path=FAMILY/'production-adoption-v1/stream-trace-component-root-results.json'
    root=json.loads(add(root_path,'Root-reported-old-semantics-reproduction','e53ded5e9cf00546bfab45f1603c7a3e529c33d86f975cf36271db48d8eeb6a2'))
    assert root['toolSession']==80465 and root['rawTerminalExitCodeObservedByRoot']==0 and root['nodeCompatibilityPassed']is False
    for row in root['evidence']:add(row['path'],'historical-old-semantics-reproduction-reference',row['sha256'],row['bytes'])
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            assert path.name not in ['index.json','input-freeze.json','source-receipt.json'];path.read_bytes().decode('utf-8')
            add(path,'new-owned-source-proof-or-test-evidence')
    document={'schemaVersion':1,'state':'EXACT_TRACE_INTEGRATION_SOURCE_PREIMAGES_AFTERIMAGES_AND_HISTORICAL_INPUT_CLOSURE',
      'inputs':sorted(rows.values(),key=lambda row:row['path']),'explicitHistoricalPreimageSnapshots':relocations,
      'reviewedFixOriginalConsumedInputs':488,'previousNativeSources':342,'oldFourFrozenCopyCounts':counts,
      'scope':'Source and recorded ordinary evidence closure only. Historical bytes/receipts are not accepted as new artifacts; all new engine pins remain NULL.'}
    raw=encode(document);(HERE/'input-freeze.json').write_bytes(raw)
    proof=json.loads((HERE/'transformations.json').read_bytes())
    tests={name:json.loads((HERE/'evidence'/name).read_bytes())for name in ['python-source-tests.json','node-source-tests.json','compile-flag-tests.json','external-capture-tests.json','syntax-results.json','generator-results.json']}
    assert [tests[name]['passed']for name in ['python-source-tests.json','node-source-tests.json','compile-flag-tests.json','external-capture-tests.json']]==[75,68,50,4]
    assert tests['syntax-results.json']['count']==9 and tests['generator-results.json']['exitCode']==0
    receipt={'schemaVersion':1,'state':'TRACE_INTEGRATION_SOURCE_READY_UNAPPLIED_ACTIONS_HELD','sourceContractVersion':'sm-classic-trace-source-v1',
      'inputFreezeSha256':sha(raw),'consumedInputFiles':len(rows),'nativeSourceFiles':342,'unchangedNativeSourcePaths':339,'changedNativeSourcePaths':3,
      'fixSourceIndexSha256':expected_indices['trace-semantics-candidate-v1'],'independentFixSourceReviewIndexSha256':expected_indices['independent-trace-semantics-source-review-v1'],
      'sourcePolicySha256':contract['sourcePolicySha256'],'sourceHelperSha256':contract['sourceHelperSha256'],'productionRecipeSha256':contract['productionRecipeSha256'],
      'toolPinsSha256':contract['toolPinsSha256'],'toolDependencies':len(tools['toolDependencies']),'fixedAfterimageDerivations':len(proof['files']),
      'fullStrictAndProtectedTagsUnchanged':True,'moduleProfileAndExportsUnchanged':True,'nodePrimaryPinsAndMitNoticePreservedInFrozenToolingPlan':True,
      'sourceTests':{'pythonSourceData':75,'nodeSyntheticParserAndRefusal':68,'syntheticCommandData':50,'externalTinyCopyCapture':4,'syntax':9,'genericFullGraphHeaderReconstructionExit':0},
      'oldFour405FreezesRehashedUnchanged':counts,
      'oldSemanticsReproduction':{'rootReceiptSha256':'e53ded5e9cf00546bfab45f1603c7a3e529c33d86f975cf36271db48d8eeb6a2','rawExitObservedByRoot':0,'rootSession':80465,'rawExitObservedByThisAuthor':False,'independentReviewIndexSha256':expected_indices['independent-stream-trace-component-review-v1'],'knownNodeGapIds':root['differenceIds'],'correctedGuestClaim':False},
      'newEngineHashes':None,'reviewedNewEnginePins':None,'liveApplicationApproved':False,'nativeBuildApproved':False,
      'configureCompilerFreezerActionExporterActionRuntimePreflightComponentizerGuestTargetHostOrTimingExecuted':False,
      'liveSource342RecipeOldPacketsOrPinsModified':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,
      'oldMeasurementProducerIndexSha256':expected_indices['measurement-producer-candidate-v1'],'measurementSuccessorRequired':True,
      'history':'Draft source/validation refinements and initial exact helper-occurrence counting stop preserved; no native attempt exists.'}
    (HERE/'source-receipt.json').write_bytes(encode(receipt))
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            data=path.read_bytes();data.decode('utf-8');files.append({'path':str(path.relative_to(HERE)),'sha256':sha(data),'bytes':len(data)})
    index={'schemaVersion':1,'state':'SEALED_UNAPPLIED_CLASSIC_TRACE_SOURCE_INTEGRATION_ACTIONS_HELD','files':files,'runtimeAcceptanceClaim':False}
    (HERE/'index.json').write_bytes(encode(index))
    print(json.dumps({'state':index['state'],'indexSha256':sha((HERE/'index.json').read_bytes()),'indexedUtf8Files':len(files),'consumedInputs':len(rows),'recipeSha256':contract['productionRecipeSha256']}))
if __name__=='__main__':main()
