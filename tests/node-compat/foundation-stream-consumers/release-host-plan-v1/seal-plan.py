"""Seal this source plan only; no proposed gate or native action is executed."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def row(path):
    return {'path':str(path.relative_to(HERE)), 'sha256':sha(path), 'bytes':path.stat().st_size}

def put(name, value):
    with (HERE/name).open('x') as stream:
        stream.write(json.dumps(value,indent=2)+'\n')

assert sha(HERE/'runtime-only-build.template.json') == '096ad77302cd8f0fcc0fd78a07e557af1dbad5b67d3b5a6e51f8f8dae8f680e1'
manifest=json.loads((HERE/'source-inputs.json').read_text())
assert len(manifest['files'])==295
for item in manifest['files']:
    path=Path(item['path'])
    assert sha(path)==item['sha256'] and path.stat().st_size==item['bytes']
assert (HERE/'stderr.log').read_text()==''
results=json.loads((HERE/'results.json').read_text())
assert results['state']=='CONSUMERS355_RELEASE_HOST_SOURCE_PLAN_CHECKS_PASSED_ACTIONS_HELD'
receipt={'schemaVersion':1,'state':'SEALED_CONSUMERS355_RELEASE_HOST_SOURCE_INTEGRATION_PLAN_ACTIONS_HELD',
    'results':row(HERE/'results.json'),'sourceInputs':row(HERE/'source-inputs.json'),
    'sourceReferences':295,'sourceCitations':49,'integrationRows':10,'dependencySteps':12,
    'reader':row(HERE/'verify-plan.py'),
    'readerExit':{'exitCode':0,'observedByThisReader':True,'stdout':row(HERE/'stdout.log'),'stderr':row(HERE/'stderr.log')},
    'freshSourceReferenceRecheckMatched':True,
    'heldRuntimeTemplateSha256':'096ad77302cd8f0fcc0fd78a07e557af1dbad5b67d3b5a6e51f8f8dae8f680e1',
    'existingProducerSupportsRuntimeOnlyWithoutCodeChange':True,
    'actualRuntimeBuildObservedOrCertifiedByThisPacket':False,
    'ownerFunctionOrPreflightOrBootstrapOrNativeOrBundleOrGuestOrHostOrTimingExecuted':False,
    'newActionOrPinAuthority':None,'runnableReadiness':False,'operationalAdmission':False,
    'acceptanceClaim':False,'performanceClaim':False}
put('source-receipt.json',receipt)
files=[]
for path in sorted(HERE.rglob('*')):
    if path.is_file() and path.name!='index.json':
        path.read_text()
        files.append(row(path))
put('index.json',{'schemaVersion':1,'state':receipt['state'],'files':files,
    'actionsAllowed':False,'operationalAdmission':False,'acceptanceClaim':False})
for item in files:
    assert sha(HERE/item['path'])==item['sha256']
print(json.dumps({'state':receipt['state'],'indexSha256':sha(HERE/'index.json'),
    'receiptSha256':sha(HERE/'source-receipt.json'),'resultsSha256':sha(HERE/'results.json'),
    'files':len(files),'sourceReferences':295,'sourceCitations':49}))
