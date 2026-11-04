"""Hash/source review only. Do not import any JavaScript or invoke tool mains."""
from pathlib import Path
import datetime
import hashlib
import json

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
SOURCE=BASE/'classic-http-candidate-v1'
REPO=HERE.parents[3]
seen={}
def read(path,expected=None,size=None):
    path=Path(path);assert path.is_file() and not path.is_symlink(),path
    before=path.stat();data=path.read_bytes();after=path.stat()
    assert (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
    sha=hashlib.sha256(data).hexdigest();assert expected is None or sha==expected,path
    assert size is None or len(data)==size,path
    seen[str(path)]={'path':str(path),'sha256':sha,'bytes':len(data)}
    return data
def load(path,expected=None):return json.loads(read(path,expected))
def main():
    index=load(SOURCE/'index.json','ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982')
    assert len(index['files'])==63
    for row in index['files']:read(SOURCE/row['path'],row['sha256'],row['bytes'])
    receipt=load(SOURCE/'source-receipt.json')
    seal=load(SOURCE/'input-freeze.json','511723ec0ef2079d3fac2f6a6f78f2fa26c3be7d15cf55f7ec03a411e028193b')
    assert len(seal['inputs'])==7518
    mapped={}
    for row in seal['inputs']:
        path=(SOURCE/row['path']).absolute()
        read(path,row['sha256'],row['bytes']);mapped[str(path.resolve())]=row
    assert len(mapped)==7518
    for name in ['cli','clocks','filesystem','http','io','random','sockets']:
        assert str((REPO/('host-apis/wasi-0.2.10/wit/deps/wasi-'+name+'-0.2.10/package.wit')).resolve())in mapped
    assert str((REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm').resolve())in mapped
    transformations=load(SOURCE/'transformations.json')
    assert len(transformations['proofs'])==3
    for proof in transformations['proofs']:
        before=read(REPO/proof['original'],proof['beforeSha256'])
        after=read(SOURCE/proof['target'],proof['afterSha256']).decode()
        for edit in reversed(proof['edits']):
            assert edit['new']in after
            after=after.replace(edit['new'],edit['old'])
        assert after.encode()==before
    bundle=load(SOURCE/'evidence/bundle-final-results.json')
    first=load(SOURCE/'evidence/bundle-first-results.json')
    read(SOURCE/'evidence/http.bundle.mjs',bundle['bundleSha256'])
    assert bundle['bundleSha256']==first['bundleSha256']=='2fab5aabb3aa48dff806fff8e21b202f8883cffad5eb20578bed9ad50a9c029c'
    assert len(bundle['imports'])==len(set(bundle['imports']))==17
    assert set(bundle['imports'])=={'node:buffer','node:child_process','node:path','node:path/posix','node:path/win32','node:events','node:string_decoder','node:assert','node:assert/strict','node:querystring','node:util','node:util/types','node:sys','node:stream/web','wasi:http/types@0.2.10','node:stream','node:stream/promises'}
    for module in bundle['modules']:
        if module.startswith('\0'):continue
        path=module.removesuffix('.native-profile.mjs') if module.endswith('.cjs.native-profile.mjs')else module
        assert str(Path(path).resolve())in mapped,path
        assert '/builtins/node-compat/'not in path
    assert bundle['sourceInputsRecheckedAfterBundle'] is True
    assert bundle['componentizerOperationInvoked'] is bundle['bundleExecuted'] is bundle['guestExecuted'] is bundle['targetHostExecuted'] is False
    assert load(SOURCE/'capability/component-pins.json')['component'] is None
    template=read(SOURCE/'capability/preflight.template.mjs').decode()
    compiled=template.replace('@INPUTS_SHA@',receipt['sourceInputSha256'])
    assert read(SOURCE/'capability/preflight.mjs')==compiled.encode()
    result={'schemaVersion':1,'state':'INDEPENDENT_CLASSIC_HTTP_SOURCE_AND_BUNDLE_EVIDENCE_REVIEW_PASSED','reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'indexSha256':hashlib.sha256((SOURCE/'index.json').read_bytes()).hexdigest(),'indexedFilesRehashed':63,'consumedRowsRehashed':7518,'liveComputedInputs':8,'exactReverseHostBuilderProofs':3,'hostBundleExternalImports':17,
      'sourceReview':['Composer redirects only the sealed baseline handler-factory import, requires exactly one redirect, delegates original WASI resource handling and retains baseline failure handling.',
        'Ordinary19 uses actual selected native modules and the unchanged pinned public-wait Node checks. No fatal/initializer/limit/CJS/GC/Web-bridge workload enters HTTP.',
        'Exact runtime-v2 index is authenticated before dynamic import. Actual342 normal-runtime admission and private immutable rechecks are delegated; scalar-writer failure does not alter these source/native artifacts.',
        'The eight LIVE WIT/adapter inputs, actual bundle modules/oracles and compiled preflight are sealed. No JavaScript factory/adapter enters the bundle.',
        'HTTP remains exact six standard0.2.10 interfaces with duration-only clock types, incoming-handler export and no Preview1/callable-clock expansion.',
        'Local component pin is null. A separately Root-reviewed exact-SHA external phase must bind the original Entry/build paths plus engine/source/component/audit/bundle/input tuple before either host starts.',
        'Both stock hosts require the same component bytes, three successful responses, clean stop/exit0, original baseline validators and full combined bodies. No instance-reuse/request-isolation claim.',
        'Known getter/Symbol/combined-owner/reset/ALS limits remain explicit; no performance or full Node profile claim.'],
      'sourceTestsObservedInOwnerEvidence':26,'syntaxChecksObservedInOwnerEvidence':24,'independentOwnerTestsOrPreflightExecuted':False,
      'independentComponentizerGuestHostOrBuildExecuted':False,'runtimeAcceptanceClaim':False,'remainingConcreteSourceBlockers':[]}
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'verified-files.json').write_text(json.dumps({'schemaVersion':1,'files':sorted(seen.values(),key=lambda row:row['path'])},indent=2)+'\n')
    print(json.dumps({'state':result['state'],'indexed':63,'inputs':7518}))
if __name__=='__main__':main()
