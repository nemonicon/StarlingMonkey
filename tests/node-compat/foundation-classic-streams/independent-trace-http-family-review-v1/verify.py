"""Read/hash/data-only generated HTTP source review. No owner code imports."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
REPO = HERE.parents[3]
STAGE = Path('/private/tmp/starling-node-compat/classic-trace-source-v1')
OUT = STAGE / 'tests/node-compat/foundation-classic-streams/production-trace-http-activated-v1'
REPLAY = OUT.with_name('production-trace-regression-activated-v1')
PRODUCER = FAMILY / 'trace-replay-activation-candidate-v1'
PARENT = FAMILY / 'classic-http-candidate-v1'
RUNTIME = FAMILY / 'production-trace-runtime-activated-v1'
INDEX = 'bb37128336a8b3044e4c632f77827c3e9e1f93dc56ec52f2099399791d3f985a'
PRODUCER_SHA = '8851e255cb51ac3db02d25946854fef0c8d9e60fac5db7042e180c2b20b2af58'
PARENT_SHA = 'ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982'
REPLAY_SHA = 'a08aec2d8a28f6bb91251841b617be20820c23ab085e526d0dc107439b061c6e'
RUNTIME_SHA = 'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78'
PINS_SHA = '182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb'
REVIEW_SHA = 'ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0'
verified = {}
checks = []

def sha(raw): return hashlib.sha256(raw).hexdigest()
def regular(path, expected=None, size=None):
    path = Path(path); before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    key = str(path.resolve()); identity = (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
    old = verified.get(key)
    if old and old['identity'] == identity: digest = old['sha256']
    else:
        digest = hashlib.sha256()
        with path.open('rb') as source:
            for block in iter(lambda:source.read(1024*1024),b''): digest.update(block)
        digest = digest.hexdigest(); after = path.lstat()
        assert identity == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
        verified[key] = {'sha256':digest,'bytes':before.st_size,'identity':identity}
    if expected is not None: assert digest == expected, (str(path),digest,expected)
    if size is not None: assert before.st_size == size
    return digest
def doc(path, expected=None):
    regular(path,expected); raw=Path(path).read_bytes()
    if expected is not None: assert sha(raw)==expected
    return json.loads(raw)
def text(path): regular(path); return Path(path).read_text()
def note(name,**values):checks.append({'name':name,'passed':True,**values})
def indexed(root,expected,count):
    value=doc(root/'index.json',expected); assert len(value['files'])==count
    seen=set()
    for row in value['files']:
        path=Path(row['path']); assert not path.is_absolute() and all(p not in ('','.','..') for p in path.parts)
        assert row['path'] not in seen;seen.add(row['path']); cursor=root
        for part in path.parts:cursor/=part;assert not cursor.is_symlink()
        regular(cursor,row['sha256'],row['bytes'])
    return value
def manifest(path,count):
    value=doc(path);assert len(value['inputs'])==count;rows={}
    for row in value['inputs']:
        target=Path(os.path.abspath(path.parent/row['path']));assert str(target) not in rows
        regular(target,row['sha256'],row['bytes']);rows[str(target)]=row
    return value,rows

def main():
    indexed(OUT,INDEX,29);indexed(PRODUCER,PRODUCER_SHA,124);indexed(PARENT,PARENT_SHA,63)
    indexed(REPLAY,REPLAY_SHA,83);indexed(RUNTIME,RUNTIME_SHA,26)
    indexed(FAMILY/'independent-trace-replay-family-review-v1','85296020f2f792c01107e10d9602de5f586881c3cde3628e1c1b30226f6dbf1d',7)
    note('all generated, producer and delegated indices rehashed',generated=29,producer=124,parent=63,replay=83,runtime=26,priorIndependentReplayReview=7)
    receipt=doc(OUT/'source-receipt.json');seal,rows=manifest(OUT/'input-freeze.json',7496)
    assert receipt['inputFreezeSha256']==regular(OUT/'input-freeze.json')
    assert receipt['consumedFiles']==7496 and receipt['componentizerGuestHostExecuted'] is False
    assert receipt['runtimeAcceptanceClaim'] is False and seal['runtimeAcceptanceClaim'] is False
    assert receipt['producerIndexSha256']==PRODUCER_SHA and receipt['replayIndexSha256']==REPLAY_SHA
    binding=doc(OUT/'source-binding.json')
    assert binding['runtimeIndexSha256']==RUNTIME_SHA and binding['replayIndexSha256']==REPLAY_SHA
    assert binding['runtimeRoot']==str(RUNTIME) and binding['replayRoot']==str(REPLAY)
    assert binding['reviewedPinsSha256']==PINS_SHA and binding['rootReviewReceiptSha256']==REVIEW_SHA
    assert binding['nativeSourceMetadataRewritten'] is False and binding['hostBundleStillRequired'] is True
    for name,digest in [('runtime-pins.json',PINS_SHA),('root-review-receipt.json',REVIEW_SHA)]:
        regular(OUT/name,digest);assert (OUT/name).read_bytes()==(REPLAY/name).read_bytes()==(RUNTIME/name).read_bytes()
    note('full7496 consumed seal and actual Root/native bindings authenticate; no metadata projection',files=7496)

    payload=PRODUCER/'http-payload'
    for path in payload.rglob('*'):
        if path.is_file():assert path.read_bytes()==(OUT/path.relative_to(payload)).read_bytes()
    proof=doc(PRODUCER/'http-transformations.json');assert len(proof['files'])==21
    for row in proof['files']:
        original=Path(row['origin']).read_bytes();regular(row['origin'],row['beforeSha256'])
        value=original.decode()
        for edit in row['edits']:
            assert value.count(edit['old'])==edit['count'];value=value.replace(edit['old'],edit['new'])
        after=(OUT/row['path']).read_bytes();assert value.encode()==after and sha(after)==row['afterSha256']
        for edit in reversed(row['edits']):
            assert value.count(edit['new'])==edit['count'];value=value.replace(edit['new'],edit['old'])
        assert value.encode()==original
    note('entire generated payload exact and21 full source derivations reverse',derivations=21)

    policy=doc(FAMILY/'trace-integration-candidate-v1/policy.json')
    canonical={r['path']:r['sha256'] for r in policy['expectedNativeSourceManifest']}
    tools=doc(FAMILY/'trace-integration-candidate-v1/artifact-tools/tool-pins.json')
    canonical.update({r['path']:r['sha256'] for r in tools['toolDependencies']})
    mappings=doc(OUT/'source-mappings.json')['mappings'];assert len(mappings)==992
    for row in mappings:
        regular(row['original'],row['beforeSha256']);regular(row['actualNewSource'],row['afterSha256'])
        relative=Path(row['original']).relative_to(REPO)
        assert Path(row['actualNewSource'])==STAGE/relative
        assert row['afterSha256']==canonical.get(str(relative),row['beforeSha256'])
    old=doc(PARENT/'input-freeze.json','511723ec0ef2079d3fac2f6a6f78f2fa26c3be7d15cf55f7ec03a411e028193b')
    assert len(old['inputs'])==7518
    old_freeze=Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze')
    excluded_native=0;replaced_local=0;retained=0
    for row in old['inputs']:
        original=Path(os.path.abspath(PARENT/row['path']))
        if original.is_relative_to(PARENT):
            relative=original.relative_to(PARENT)
            if (payload/relative).is_file() or str(relative)=='capability/preflight.mjs':replaced_local+=1;continue
        if original.is_relative_to(old_freeze) or original.is_relative_to(old_freeze.resolve()):excluded_native+=1;continue
        if original.is_relative_to(REPO):
            relative=original.relative_to(REPO);target=STAGE/relative;digest=canonical.get(str(relative),row['sha256'])
        else:target=original;digest=row['sha256']
        assert str(target) in rows and rows[str(target)]['sha256']==digest,str(target);retained+=1
    replay_seal,replay_rows=manifest(REPLAY/'input-freeze.json',2293)
    for target,row in replay_rows.items():assert target in rows and rows[target]['sha256']==row['sha256']
    note('old7518 ancestry accounted for without admitting old freeze as corrected authority; actual replay rows all retained',ancestry=7518,mappings=992,replacedLocal=replaced_local,oldNativeReferencesExcluded=excluded_native,remainingInherited=retained,replayRows=2293)

    live=replay_seal['liveComputedInputs'];assert len(live)==8
    for name in live:
        target=str(STAGE/name);assert target in rows
        assert rows[target]['sha256']==replay_rows[target]['sha256']
    regular(STAGE/live[-1],'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0',53512)
    packages=STAGE/'host-apis/wasi-0.2.10/wit/deps'
    assert sorted(p.name for p in packages.iterdir())==sorted(Path(x).parent.name for x in live[:7])
    for package in packages.iterdir():assert package.is_dir() and not package.is_symlink() and [x.name for x in package.iterdir()]==['package.wit']
    note('LIVE8 canonical actual paths and exact seven WIT leaf directories authenticate',live=8)

    template=text(OUT/'capability/preflight.template.mjs')
    rendered=template.replace('@INPUTS_SHA@',regular(OUT/'input-freeze.json'))
    assert rendered==text(OUT/'capability/preflight.mjs')
    assert rendered.index("assert.equal(sha256,expectedSha256")<rendered.index('const document=JSON.parse(bytes)')
    assert rendered.index('await verifyRuntimeIndex();const {classicPreflight}=await import')<rendered.index("await classicPreflight({variant:'normal-runtime'})")
    assert "const nativeRecheck=actual.recheck" in rendered and 'expectedManifest=inputClosure.sha256' in rendered
    assert 'await nativeRecheck();await verifyRuntimeIndex();await verifyInputClosure({manifestPath,expectedSha256:expectedManifest});' in rendered
    assert 'requiresIndependentTerminalExitZero:true' in rendered
    note('compiled preflight exact; runtime index before import, seal before rows and privately captured rechecks retained')

    pin=doc(OUT/'capability/component-pins.json');assert pin['component'] is None
    contract=text(OUT/'capability/http-contract.mjs')
    assert 'ROOT_REVIEWED_CLASSIC_TRACE_COMBINED_HTTP_COMPONENT_V1' in contract
    assert "'reviewed-classic-trace-combined-http-component'" in contract
    assert contract.index("hash(raw),expectedPinSha")<contract.index('selectCombinedHTTPPin(JSON.parse(raw)')
    for statement in ["pin.engineSha256,productionPin.engineSha256","pin.engineReceiptSha256,productionPin.receiptSha256","pin.sourceInputSha256,sourceSha","pin.sourceEntryPath,join(here,'http-component.mjs')","const frozenChecks=checks.map(row=>[...row]),nativeRecheck=admission.recheck"]:assert statement in contract
    wt=text(OUT/'capability/run-http-wasmtime.mjs')
    assert wt.index("assert.notEqual(process.env.NODE_COMPAT_HTTP_REQUIRE_INTRINSICS,'1'")<wt.index('await verifyHTTPReady()')
    note('local phase remains null; new exact TRACE external phase binds entry/component/audit/bundle/inputs and actual runtime; early intrinsics misuse refused')

    bundle=text(OUT/'test-bundle.mjs');match=re.search(r"const imports=(\[.*?\])\.sort\(\);",bundle)
    assert match
    imports=re.findall(r"'([^']+)'",match.group(1));assert len(imports)==len(set(imports))==17
    expected=['node:stream','node:stream/promises','node:buffer','node:child_process','wasi:http/types@0.2.10','node:path','node:path/posix','node:path/win32','node:events','node:string_decoder','node:assert','node:assert/strict','node:querystring','node:util','node:util/types','node:sys','node:stream/web']
    assert sorted(imports)==sorted(expected)
    assert 'assert.deepEqual([...chunk.imports].sort(),imports)' in bundle
    assert 'modules.includes(BASELINE_ENTRY)' in bundle and 'modules.includes(COMPOSER_ID)' in bundle
    assert 'noFacadeOrAdapterBundled:true' in bundle and 'await actual.recheck()' in bundle
    note('unexecuted whole-entry bundle checker demands exact17 imports and actual baseline/checks/composer graph with no facade/adapter',imports=imports)

    composer=text(OUT/'capability/composer-plugin.mjs');ordinary=text(OUT/'capability/ordinary.mjs')
    assert "../../production-trace-regression-activated-v1/capability/http-component.mjs" in composer
    assert str(RUNTIME/'harness/checks.mjs') in composer and ('file://'+str(RUNTIME/'harness/checks.mjs')) in ordinary
    actual_checks=RUNTIME/'harness/checks.mjs';assert str(actual_checks) in rows
    oracle=STAGE/'tests/node-compat/foundation-classic-streams/implementation-candidate-v1/node-final-acceptance-results.json'
    regular(oracle,'88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce');assert len(doc(oracle)['expected'])==19
    baseline=REPLAY/'capability/http-component.mjs';assert str(baseline) in rows
    assert baseline.read_bytes()==(FAMILY/'production-regression-activated-v3/capability/http-component.mjs').read_bytes()
    host=text(OUT/'capability/validate-hosts.mjs');combined=text(OUT/'capability/validate-combined.mjs')
    for statement in ['report.responses.length,3','report.process.stopped,true','report.process.exitStatus,{code:0,signal:null}','wasmtime.componentSha256,audit.componentSha256','wash.component.sha256,audit.componentSha256','instanceReuseClaim:false,requestIsolationClaim:false']:assert statement in host
    assert 'assert.deepEqual(report.ordinary,expected)' in combined and 'checkFoundationsHTTPReport(baseline,audit)' in combined
    capabilities=text(OUT/'capability/capabilities.mjs')
    assert 'audit.clockDependency.typeOnly,true' in capabilities
    assert 'audit.clockDependency.callableImports,[]' in capabilities and 'audit.clockDependency.coreClockImports,[]' in capabilities
    assert "wasi:random/random@0.2.10" in capabilities
    note('unchanged baseline/protected29/ordinary19 full oracle and handler/host validators; same bytes three requests per stock host and type-only clock required')

    indexed(OUT,INDEX,29);indexed(REPLAY,REPLAY_SHA,83);indexed(RUNTIME,RUNTIME_SHA,26)
    result={'schemaVersion':1,'state':'INDEPENDENT_GENERATED_CORRECTED_HTTP_SOURCE_REVIEW_PASSED','reviewedIndexSha256':INDEX,
            'checks':checks,'uniqueRegularPathsRehashed':len(verified),'consumedFilesVerified':7496,
            'noConcreteSourceBlockerFound':True,'ownerActionsExecuted':False,'bundleExecuted':False,'nativePreflightExecuted':False,
            'componentOrGuestOrHostExecuted':False,'runtimeAcceptanceClaim':False,
            'scope':'Source/data/hash review only. Whole-entry bundle and later reviewed phase, packaging and both hosts are unexecuted and remain mandatory. No acceptance/performance/reuse/ALS/reset claim.'}
    with (HERE/'results.json').open('x') as output:json.dump(result,output,indent=2);output.write('\n')
    with (HERE/'verified-paths.json').open('x') as output:json.dump({'schemaVersion':1,'files':[{'path':p,'sha256':r['sha256'],'bytes':r['bytes']} for p,r in sorted(verified.items())]},output,indent=2);output.write('\n')
    print(json.dumps({'checks':len(checks),'uniquePaths':len(verified),'resultsSha256':regular(HERE/'results.json')}))

if __name__=='__main__':main()
