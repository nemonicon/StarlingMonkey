"""Seal this owned source packet and explicit data references; no action imports."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
BASE=Path('/tmp/starling-node-compat/zlib-source-v4')
def describe(path):
    path=Path(path).absolute();before=path.lstat()
    assert path.is_file()and not path.is_symlink(),path
    digest=hashlib.sha256()
    with path.open('rb')as f:
        for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    after=path.lstat()
    assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    return{'path':str(path),'realpath':str(path.resolve()),'sha256':digest.hexdigest(),'bytes':after.st_size}
def put(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def main():
    assert not(HERE/'index.json').exists()
    ast.parse(Path(__file__).read_bytes())
    references={}
    def add(path,role):
        row=describe(path);key=row['path']
        if key not in references:references[key]={**row,'roles':[role]}
        else:
            assert all(references[key][k]==row[k]for k in row)
            if role not in references[key]['roles']:references[key]['roles'].append(role)
        return references[key]
    parent=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
    manifest=json.loads((parent/'policy.json').read_bytes())['expectedNativeSourceManifest']
    for row in manifest:assert add(BASE/row['path'],'actual-parent350-native-input')['sha256']==row['sha256']
    parent_index=json.loads((parent/'index.json').read_bytes());add(parent/'index.json','parent350-authority')
    for row in parent_index['files']:
        record=add(parent/row['path'],'parent350-sealed-input');assert record['sha256']==row['sha256']and record['bytes']==row['bytes']
    original=HERE.with_name('production-text-json-candidate-v1')
    hold=HERE.with_name('independent-production-text-json-source-review-v1')
    for root,expected,role in[(original,'d768d71244695d18914844c860f1053e0c09d67cf2b321bffedfeb2e911ebba1','immutable-v1-beforeimage'),(hold,'b58cf2dc101686c63dce246e52702794ca08b76a8f68168b44162be6cfadc202','immutable-CONS355-M1-HOLD')]:
        assert add(root/'index.json',role)['sha256']==expected
        for row in json.loads((root/'index.json').read_bytes())['files']:
            record=add(root/row['path'],role)
            assert record['sha256']==row['sha256']and record['bytes']==row['bytes']
    names=[
      'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json',
      'tests/node-compat/foundation-scheduler/integration-candidate-v1/layer-policy.py',
      'tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json',
      'tests/node-compat/profile-bundler.mjs',
      'tests/node-compat/foundation-stream-consumers/LICENSE.node',
      'tests/node-compat/foundation-stream-consumers/source-audit.json',
      'tests/node-compat/foundation-stream-consumers/export-contract.node-v22.14.0.json',
      'tests/node-compat/foundation-stream-consumers/node-results.json',
      'tests/node-compat/foundation-stream-consumers/node-checks.mjs',
      'tests/node-compat/foundation-stream-consumers/guest-oracle.mjs',
      'tests/node-compat/foundation-stream-consumers/metadata-v2/create-module.mjs',
      'tests/node-compat/foundation-stream-consumers/metadata-v2/component.mjs',
      'tests/node-compat/foundation-stream-consumers/metadata-v2/component-checks.mjs',
      'tests/node-compat/foundation-stream-consumers/metadata-v2/component-results.json',
      'tests/node-compat/foundation-stream-consumers/metadata-v2/source-receipt.json',
      'tests/node-compat/foundation-stream-consumers/metadata-v2/reflection-results.json',
      'builtins/node-compat/validate-manifest.mjs',
      'builtins/node-compat/manifest.schema.json',
      'builtins/node-compat/stream-web-readable-iteration.mjs',
    ]
    for name in names:add(REPO/name,'explicit-source-reuse-or-tooling-reference')
    for name in['cli','clocks','filesystem','http','io','random','sockets']:
        add(REPO/f'host-apis/wasi-0.2.10/wit/deps/wasi-{name}-0.2.10/package.wit','future-live-http-copy-input-reference')
    add(REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm','future-live-packaging-input-reference')
    add('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node','source-test-node-executable')
    put('source-inputs.json',{'schemaVersion':1,'state':'SOURCE_INPUT_REFERENCES_NOT_ENGINE_ADMISSION','files':sorted(references.values(),key=lambda r:r['path']),'nativeParentCount':350,'parentIndexFileCount':len(parent_index['files']),'nativeAndHarnessRootsSeparate':True,'futurePackagingClosureComplete':False,'noEngineOrSDKArchiveCopied':True,'actualFutureEnginePins':None})
    policy=json.loads((HERE/'policy.json').read_bytes());derivation=json.loads((HERE/'native-derivations.json').read_bytes())
    own=lambda name:{k:v for k,v in describe(HERE/name).items()if k in['sha256','bytes']}
    put('source-receipt.json',{'schemaVersion':1,'state':'UNAPPLIED_BOUNDED_STREAM_CONSUMERS355_SOURCE_CANDIDATE_V2','installed':False,'profileVersion':policy['profileVersion'],'parent350Index':describe(parent/'index.json'),'parent350NativeSourceRoot':str(BASE),'nativeSources':355,'unchangedParentSources':348,'nativeReplacements':2,'nativeAdditions':5,'newCppTranslationUnits':0,'changedPaths':[row['path']for row in derivation['changes']],'addedPaths':derivation['addedSources'],'nativePatch':own('native.UNAPPLIED.patch'),'hostPatch':own('host.UNAPPLIED.patch'),'policy':own('policy.json'),'helper':own('layer-policy.py'),'recipe':own('proposed/tests/node-compat/build-engine.sh'),'admissionPins':own('admission-pins.json'),'sourceInputs':own('source-inputs.json'),'checks':own('checks.json'),'v1Candidate':describe(original/'index.json'),'v1Hold':describe(hold/'index.json'),'successorDerivations':own('successor-derivations.json'),'correctedSourceBlocker':'CONS355-M1','nativePayloadChangesFromV1':0,'futureEnginePins':None,'operationalAdmission':'CLOSED','nativeSdkSyntaxBuildFactoryCodecBundlerGuestHostOrTimingExecuted':False,'historicalEvidenceIsRuntimeProofFor355':False,'artifactFrameworkDeferred':True})
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and path.name!='index.json':
            row=describe(path);files.append({'path':str(path.relative_to(HERE)),'sha256':row['sha256'],'bytes':row['bytes']})
    put('index.json',{'schemaVersion':1,'state':'UNAPPLIED_STREAM_CONSUMERS_SOURCE_PACKET_SEALED','files':files,'sourceInputFiles':len(references),'nativeSourceFiles':355,'actualFutureEnginePins':None,'runtimeOrReleaseAcceptance':False})
    print(json.dumps({'files':len(files),'inputReferences':len(references),'indexSha256':describe(HERE/'index.json')['sha256'],'sourceReceiptSha256':describe(HERE/'source-receipt.json')['sha256'],'operationalAdmission':'CLOSED'}))
if __name__=='__main__':main()
