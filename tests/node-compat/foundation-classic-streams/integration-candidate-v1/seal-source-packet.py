"""Seal source and observed host-only reports. Never admits or executes an engine."""
from pathlib import Path
import datetime
import hashlib
import json
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def document(name):return json.loads((HERE/name).read_bytes())
def main():
    assert not(HERE/'index.json').exists()and not(HERE/'source-receipt.json').exists()
    policy=document('policy.json');pins=document('admission-pins.json');patch=document('patch-files.json')
    for row in policy['parentExpectedNativeSourceManifest']:assert sha(REPO/row['path'])==row['sha256']
    for row in document('input-freeze.json')['inputs']:assert sha((HERE/row['path']).resolve())==row['sha256']
    artifact=HERE/'artifact-tools';artifact_index=json.loads((artifact/'index.json').read_bytes())
    for row in artifact_index['files']:assert sha(artifact/row['path'])==row['sha256']
    indices=[HERE.parent/'implementation-candidate-v1/index.json',HERE.parent/'implementation-candidate-v1-allocation-order-amendment/index.json',HERE.parent/'implementation-syntax-v1/index.json',artifact/'index.json']
    receipt={'schemaVersion':1,'state':'UNAPPLIED_CLASSIC342_INTEGRATION_SOURCE_ONLY_ALL_ACTUAL_PINS_NULL',
      'preparedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parentNativeSources':306,'nativeSources':342,
      'sourceDelta':{'additions':36,'replacements':2,'productionPatchFiles':41,'newFiles':patch['newFiles'],'replacedFiles':patch['replacedFiles']},
      'currentLive306VerifiedUnchanged':True,
      'patch':{'path':'classic-streams.UNAPPLIED.patch','sha256':sha(HERE/'classic-streams.UNAPPLIED.patch'),'gitApplyCheckExitCode':0,'whitespaceMode':'error'},
      'productionRecipeSha256':pins['productionRecipeSha256'],'policySha256':sha(HERE/'policy.json'),'helperSha256':sha(HERE/'layer-policy.py'),
      'admissionSha256':sha(HERE/'source/tests/node-compat/classic-streams-admission.mjs'),'selectorSha256':sha(HERE/'source/tests/node-compat/module-selection.mjs'),
      'parent306AdmissionModuleSha256':pins['current306AdmissionSha256'],'reverseRecipeEdits':21,'reverseSelectorEdits':4,
      'hostOnlyChecks':{'nodeSourceModels':document('host-test-results.json')['checks'],'pythonSourceModels':document('python-host-test-results.json')['checks'],
        'enabledBundles':8,'disabledBundlerRefusals':8,'actualNullPreflightRejections':4,'runtimeInputFiles':373,'artifactPython':74,'artifactNode':23},
      'actualSdkSyntaxEvidence':{'indexPath':str(indices[2].relative_to(REPO)),'indexSha256':sha(indices[2]),
        'correctedRegisterSha256':'2848f059fb5693aa37c54945bff685444c8431007ceaec59d3335d01f7aced4a','scope':'Prior actual SDK30/SM147 fsyntax-only; no object or new engine'},
      'immutableAncestry':[{'path':str(path.relative_to(REPO)),'sha256':sha(path)}for path in indices],
      'artifactTools':{'path':'artifact-tools/index.json','sha256':sha(artifact/'index.json'),'labels':['normal-off','normal-runtime','gc-off','disabled-off'],
        'launcherMainsRun':False,'freezerMainsRun':False,'exporterMainsRun':False,'startFreeBytes':2147483648,'stopBelowFreeBytes':838860800,
        'nativeJobs':1,'normalOffFreezeRequiredBeforeGC':True,'exportedPinState':'UNREVIEWED only'},
      'sourcePolicyObservation':{'nativeCommandsWhenTicksAndWebOn':61,'strictNativeCommands':4,'separateEmbeddingCommands':1,'privateTargetCommands':5,
        'privateTargetCommandsWhenStreamWebOff':4,'classicMacroCountWhenDisabled':0,'noAdditionalEmbeddingPatch':True,'parentEmbeddingAfterSha256':policy['embedding']['afterSha256']},
      'actualEnginePins':{key:None for key in ['normal-off','normal-runtime','gc-off','disabled-off']},
      'nativeBuildPerformed':False,'guestPerformed':False,'hostInstantiationPerformed':False,'newPerformanceEvidence':False,
      'costScope':'Large captured guest JavaScript state machines; existing native byte primitives; unmeasured classic size/memory/throughput.',
      'limitations':['Full Node streams compatibility not claimed','Queue reset/cancellation teardown and ALS/request propagation remain open',
        'Inherited callback-return then-getter and Symbol registry gaps remain','GC future corpus is a combined-owner check, not a queue-root isolation proof',
        'Web bridges/function stages/operators/async disposal remain explicit failures','Discard stream after declared state-limit failure; no total heap bound',
        'No stopped DEBUG/OOM/fault/raw-memory work resumed']}
    with(HERE/'source-receipt.json').open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    rows=[]
    for path in sorted(HERE.rglob('*')):
        if not path.is_file():continue
        assert not path.is_symlink();assert path.suffix not in['.wasm','.o','.a','.pyc'],path
        if path==HERE/'index.json':continue
        rows.append({'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size})
    index={'schemaVersion':1,'state':'SEALED_UNAPPLIED_CLASSIC342_SOURCE_INTEGRATION_ALL_ACTUAL_PINS_NULL','sourceReceiptSha256':sha(HERE/'source-receipt.json'),
      'files':rows,'actualEnginePins':None,'accepted':False,'nativeBuildOrGuestRun':False}
    with(HERE/'index.json').open('x')as stream:json.dump(index,stream,indent=2);stream.write('\n')
    print(json.dumps({'files':len(rows),'indexSha256':sha(HERE/'index.json'),'receiptSha256':sha(HERE/'source-receipt.json'),'bytes':sum(row['bytes']for row in rows)}))
if __name__=='__main__':main()
