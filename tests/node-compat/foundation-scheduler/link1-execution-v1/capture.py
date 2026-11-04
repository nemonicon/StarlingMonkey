"""Capture completed text evidence. Never build, run a guest, or copy binaries."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent
PACKETS = HERE.parent
EXTERNAL = Path('/tmp/starling-node-compat')
RUN = EXTERNAL/'foundation-scheduler-link1-v1'
FREEZE = RUN/'native-freeze'
copied = []
existing = []
binary_refs = {}

def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            value.update(block)
    return value.hexdigest()

def regular(path):
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and not path.is_symlink(),path
    return info

def binary_reference(path, expected=None, role='external-binary-reference'):
    info = regular(path)
    value = digest(path)
    if expected is not None:
        assert value == expected,path
    previous = binary_refs.get(str(path))
    row = {'path':str(path),'sha256':value,'bytes':info.st_size,'role':role,
           'aggregateRehashed':True,'copiedIntoRepository':False}
    if previous:
        assert previous['sha256'] == value and previous['bytes'] == info.st_size
    else:
        binary_refs[str(path)] = row
    return row

def capture(source, destination, role, expected=None):
    regular(source)
    assert source.suffix not in ['.wasm','.o','.a','.cwasm'],source
    data = source.read_bytes()
    data.decode('utf-8')
    assert 0 not in data and data[:4].hex() not in ['0061736d','7f454c46','cffaedfe','cefaedfe','feedface','feedfacf'],source
    value = hashlib.sha256(data).hexdigest()
    if expected is not None:
        assert value == expected,source
    target = HERE/destination
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:
        stream.write(data)
    assert digest(target) == value and digest(source) == value
    copied.append({'path':destination,'source':str(source),'sha256':value,'bytes':len(data),
                   'role':role,'byteExactCopy':True})

assert not (HERE/'capture-inventory.json').exists(),'Capture is exclusive; preserve previous attempts'
for source in sorted(HERE.iterdir()):
    if source.is_file() and source.name != 'capture.py':
        regular(source)
        existing.append({'path':source.name,'sha256':digest(source),'bytes':source.stat().st_size,
                         'role':'preexisting-root-receipt-or-copied-preflight-output','preservedUnchanged':True})

independent = {
 'normal':('link1-ordinary-release-verification-v1','7459eb2d741ec764941c0ba0279973edd39fe782d8d1ae90e6abc9d29ff0be71'),
 'gc':('link1-gc-verification-v1','caca4d68cf3bb2c831e9292e3c855a005fad7d2f9e35b65e45137ed6f9142a96'),
}
independent_refs = []
for variant,(name,expected) in independent.items():
    base = PACKETS/name
    assert digest(base/'results.json') == expected
    index_bytes = (base/'index.json').read_bytes()
    index = json.loads(index_bytes)
    for row in index['files']:
        assert digest(base/row['path']) == row['sha256']
        capture(base/row['path'],'independent/'+variant+'/'+row['path'],'independent-read-only-verification',row['sha256'])
    capture(base/'index.json','independent/'+variant+'/index.json','independent-verification-index')
    independent_refs.append({'variant':variant,'path':str(base),'indexSha256':hashlib.sha256(index_bytes).hexdigest(),
                             'resultsSha256':expected,'reexecutedByAggregate':False})
    checked = json.loads((base/'results.json').read_bytes())
    for row in checked['verifiedFiles']:
        path = Path(row['path'])
        if path.suffix in ['.wasm','.o','.a','.cwasm']:
            binary_reference(path,row['sha256'],'independently-verified-external-component-core-engine-or-source-asset')

variants = []
for variant,label,driver,raw in [
 ('normal','diagnostic-release','ordinary-release-driver32-v1','release'),
 ('gc','diagnostic-gc','gc-driver32-v1','gc'),
]:
    build = RUN/'builds'/label
    launch_result = json.loads((build/'result.json').read_bytes())
    assert launch_result['rawChildExitCode'] == launch_result['launcherExitCode'] == 0
    assert launch_result['lifecycleComplete'] is True and launch_result['evidenceComplete'] is True
    assert launch_result['ownedGroupCleanup']['complete'] is True
    for filename in ['launch.json','result.json','build.log']:
        capture(build/filename,'launchers/'+variant+'/'+filename,'completed-launcher-build-evidence',
                launch_result['logSha256'] if filename == 'build.log' else None)
    for suffix in ['launch.stdout.json','launch.stderr.txt','freeze.stdout.json','freeze.stderr.txt','driver32.stdout.log','driver32.stderr.log']:
        capture(EXTERNAL/('link1-'+raw+'-'+suffix),'raw/'+variant+'/'+suffix,'exact-external-launch-freeze-or-component-output')
    report_path = RUN/driver/'results.json'
    report = json.loads(report_path.read_bytes())
    assert report['state'] == 'private-diagnostic-link1-ordinary-components-passed'
    assert report['driverSourceVersion'] == 'sm-private-ticks-link1-driver-v2'
    assert report['consumedInputCount'] == 32 and report['liveAdapterSealedBeforeAfter'] is True
    assert report['sourceInputsCheckedBeforeAfter'] is True
    assert len(report['artifacts']) == 10 and len(report['initializationFailures']) == 5
    assert len(report['runtimeFailures']) == len(report['pairedControls']) == 3
    metadata = json.loads((FREEZE/(label+'.engine.wasm.build.json')).read_bytes())
    assert metadata['diagnosticOnly'] is True and metadata['gcStress'] == (variant == 'gc')
    assert metadata['engineSha256'] == report['engineSha256']
    assert metadata['oomTesting'] is False
    assert len(metadata['sourceManifest']) == 306
    assert len(metadata['internalTickDiagnosticPolicy']['sourceManifest']) == 2
    engine = binary_reference(FREEZE/(label+'.engine.wasm'),metadata['engineSha256'],'diagnostic-only-frozen-engine')
    assert engine['bytes'] == metadata['engineBytes']
    assert digest(FREEZE/(label+'.engine.wasm.build.json')) == report['engineReceiptSha256']
    capture(report_path,'components/'+variant+'/results.json','complete-driver32-component-report')
    for source in sorted((RUN/driver).iterdir()):
        if source.is_file() and (source.name.endswith('.source.mjs') or '.initializer.' in source.name):
            capture(source,'components/'+variant+'/generated-source/'+source.name,'actual-application-or-recorded-initializer-source')
    for artifact in report['artifacts']:
        assert artifact['interfaceAudit']['emittedImports'] == []
        binary_reference(Path(artifact['componentPath']),artifact['componentSha256'],'actual-diagnostic-application-component')
    receipt_path = FREEZE/(label+'-freeze-receipt.json')
    assert digest(receipt_path) == report['frozenConfiguration']['receiptSha256']
    variants.append({'variant':variant,'gcStress':metadata['gcStress'],'engine':engine,
                     'metadataPath':str(FREEZE/(label+'.engine.wasm.build.json')),
                     'metadataSha256':digest(FREEZE/(label+'.engine.wasm.build.json')),
                     'freezeReceiptPath':str(receipt_path),'freezeReceiptSha256':digest(receipt_path),
                     'componentReportPath':str(report_path),'componentReportSha256':digest(report_path),
                     'components':10,'emittedImports':[],'initializationFailures':5,'pairedControls':3,
                     'freshFatalDiscardObservations':3,'retainedMainCalls':3,'mainFreshWasmtime':True,
                     'launcherExitCode':0,'rootOutputPrefix':raw})

# Preserve all root-level textual configuration/link/Rust/OpenSSL evidence.
# Source directories and binary engines stay external; receipt inventories bind them.
for source in sorted(FREEZE.iterdir()):
    if source.is_file():
        if source.suffix == '.wasm':
            continue
        capture(source,'native-freeze-text/'+source.name,'full-frozen-metadata-config-link-and-tooling-text')

for row in existing:
    assert digest(HERE/row['path']) == row['sha256']
for row in copied:
    assert digest(HERE/row['path']) == row['sha256'] and digest(Path(row['source'])) == row['sha256']
inventory = {'schemaVersion':1,'state':'COMPLETED_LINK1_TEXT_EVIDENCE_CAPTURED_NO_EXECUTION',
             'preexistingRootRecords':existing,'copiedTextFiles':copied,'externalBinaryReferences':list(binary_refs.values()),
             'independentVerificationReferences':independent_refs,'variants':variants,
             'binaryBytesCopied':False,'sourceOrArtifactModified':False,'buildGuestHostOrVerifierReexecuted':False}
with (HERE/'capture-inventory.json').open('x') as stream:
    json.dump(inventory,stream,indent=2);stream.write('\n')
print(json.dumps({'copiedTextFiles':len(copied),'preservedRootRecords':len(existing),
                  'externalBinaryReferences':len(binary_refs),'variants':len(variants),'binaryBytesCopied':False}))
