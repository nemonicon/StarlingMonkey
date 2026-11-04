"""Read-only source/index/witness verification. No native or guest execution."""
from pathlib import Path
import hashlib
import json

def main():
    if not __debug__:raise RuntimeError('Source checks require assertions')
    here=Path(__file__).resolve().parent
    repo=here.parents[3]
    digest=lambda data:hashlib.sha256(data).hexdigest()
    receipt=json.loads((here/'source-receipt.json').read_bytes())
    input_bytes=(here/'input-freeze.json').read_bytes()
    assert digest(input_bytes)==receipt['inputFreezeSha256']
    inputs=json.loads(input_bytes)
    for row in inputs['files']:
        path=Path(row['path']);path=path if path.is_absolute() else repo/path
        assert path.is_file() and not path.is_symlink(),path
        data=path.read_bytes();assert digest(data)==row['sha256'] and len(data)==row['bytes'],path
    index=json.loads((here/'index.json').read_bytes())
    for row in index['files']:
        path=here/row['path'];assert path.is_file() and not path.is_symlink()
        data=path.read_bytes();assert digest(data)==row['sha256'] and len(data)==row['bytes'],path
    report=json.loads((here/'node-final-acceptance-results.json').read_bytes())
    assert report['groups']==19 and report['hostDependencies']==report['expected']==report['productionFacadesReferenceKernel']
    assert len(report['unsupportedChecks'])==48 and len(report['unsupportedOverloadChecks'])==17 and len(report['customPromisifyDefaultMutation'])==4
    assert report['nativeKernelExecuted'] is False and report['privateGuestSchedulerExecuted'] is False
    assert report['componentOrHostRuntimeExecuted'] is False
    changes=json.loads((here/'transformation-receipt.json').read_bytes())
    assert len(changes['rawSources'])==len(changes['transformations'])==24
    for row in changes['rawSources']:assert digest((here/'vendor'/row['path']).read_bytes())==row['sha256']
    for row in changes['transformations']:assert digest((here/'source'/row['path']).read_bytes())==row['afterSha256']
    pins=json.loads((here/'native-integration-pins.json').read_bytes())
    for name,expected in pins['before'].items():assert digest((repo/name).read_bytes())==expected
    for name,expected in pins['after'].items():assert digest((here/'integration'/name).read_bytes())==expected
    assert digest((here/'native-integration.UNAPPLIED.patch').read_bytes())==pins['patchSha256']
    mapping=json.loads((here/'integration/new-files.json').read_bytes())
    for row in mapping['files']:assert digest((here/row['candidatePath']).read_bytes())==row['sha256']
    print(json.dumps({'state':'UNAPPLIED_CLASSIC_SOURCE_PACKET_REHASHED','files':len(index['files']),
                     'inputs':len(inputs['files']),'vendorFiles':24,'groups':19,'nativeOrGuestExecuted':False}))

if __name__=='__main__':main()
