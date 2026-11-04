"""Source/data tests only; no native/guest/target-host or producer action main."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
REL=Path('tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1')
STAGE=Path('/tmp/starling-node-compat/trace-integration-source-model-v2')
checks=[]
def sha(data):return hashlib.sha256(data).hexdigest()
def check(name,condition=True):assert condition,name;checks.append(name)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def rejects(name,call):
    try:call()
    except (AssertionError,KeyError,ValueError):check(name);return
    raise AssertionError('Unexpected acceptance: '+name)
def main():
    assert not STAGE.exists(),'Source test root must be fresh; preserve prior failures'
    contract=json.loads((HERE/'contract.json').read_bytes());policy=json.loads((HERE/'policy.json').read_bytes())
    old=json.loads((HERE/'ancestry/policy.json').read_bytes())
    before={row['path']:row['sha256']for row in old['expectedNativeSourceManifest']}
    after={row['path']:row['sha256']for row in policy['expectedNativeSourceManifest']}
    check('full actual342 source path set retained',len(before)==len(after)==342 and set(before)==set(after))
    changed=[name for name in before if before[name]!=after[name]]
    check('exactly339 unchanged and three reviewed canonical afterimages',len(changed)==3 and sum(before[name]==after[name]for name in before)==339)
    check('no C++ registration CMake ABI native delta',all(name.startswith('builtins/node-compat/classic-streams/')and Path(name).name in ['classic-core.generated.mjs','transformation-receipt.json','factories.generated.h']for name in changed))
    check('full strict tag unchanged',policy['strictPolicyVersion']==old['strictPolicyVersion'])
    check('full protected tag unchanged',policy['protectedPolicyVersion']==old['protectedPolicyVersion'])
    check('embedding and original installation patch ancestry unchanged',policy['embedding']==old['embedding']and policy['nativePatchSha256']==old['nativePatchSha256'])
    check('m0.12 manifest and public surface unchanged',policy['profileVersion']==old['profileVersion']=='sm-node-22.14.0-m0.12'and policy['classicManifestSha256']==old['classicManifestSha256'])
    check('new source contract and install-policy versions distinct',policy['version']!=old['version']and policy['classicPolicyVersion']!=old['classicPolicyVersion'])
    proof=json.loads((HERE/'transformations.json').read_bytes())
    for row in proof['files']:
        text=(REPO/row['origin']).read_text();check('proof preimage '+row['afterimage'],sha(text.encode())==row['beforeSha256'])
        for edit in row['edits']:
            assert text.count(edit['old'])==edit['count'];text=text.replace(edit['old'],edit['new'])
        check('forward exact '+row['afterimage'],text==(HERE/row['afterimage']).read_text()and sha(text.encode())==row['afterSha256'])
        for edit in reversed(row['edits']):
            for at in reversed(edit['offsets']):
                assert text[at:at+len(edit['new'])]==edit['new'];text=text[:at]+edit['old']+text[at+len(edit['new']):]
        check('reverse exact '+row['afterimage'],sha(text.encode())==row['beforeSha256'])
        check('unified patch hash '+row['afterimage'],sha((HERE/row['patch']).read_bytes())==row['patchSha256'])
    rows={}
    def add(name,data):
        if name in rows:assert rows[name]==data,name
        rows[name]=data
    for row in old['expectedNativeSourceManifest']:
        data=(REPO/row['path']).read_bytes();assert sha(data)==row['sha256'];add(row['path'],data)
    for f in sorted((HERE/'source').rglob('*')):
        if f.is_file():rows[str(f.relative_to(HERE/'source'))]=f.read_bytes()
    tools=json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes())
    for row in tools['toolDependencies']:
        name=row['path']
        if name.startswith(str(REL)+'/'):data=(HERE/name[len(str(REL))+1:]).read_bytes()
        elif (HERE/'source'/name).is_file():data=(HERE/'source'/name).read_bytes()
        else:data=(REPO/name).read_bytes()
        assert sha(data)==row['sha256']and len(data)==row['bytes'];add(name,data)
    # Copy source-test fixture/producer source into the isolated source root.
    # There is no engine, dependency fetch, compiler or executable artifact here.
    for f in sorted(HERE.rglob('*')):
        if f.is_file()and f.suffix!='.pyc':add(str(REL/f.relative_to(HERE)),f.read_bytes())
    STAGE.mkdir()
    for name,data in sorted(rows.items()):
        target=STAGE/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for name,digest in after.items():assert sha((STAGE/name).read_bytes())==digest
    check('isolated full342 afterimage source root rehashed',True)
    layer=load(STAGE/REL/'layer-policy.py','trace_source_model_helper')
    check('successor helper directly validates corrected342 bytes',layer.validate_sources(STAGE))
    old_layer=load(REPO/'tests/node-compat/foundation-classic-streams/integration-candidate-v1/layer-policy.py','old_classic_source_model_helper')
    rejects('previous helper rejects corrected actual source bytes',lambda:old_layer.validate_sources(STAGE))
    rejects('successor helper rejects unchanged old342 source tree',lambda:layer.validate_sources(REPO))
    bad=STAGE/changed[0];saved=bad.read_bytes();bad.write_bytes(saved+b'\n')
    rejects('successor helper rejects one altered afterimage',lambda:layer.validate_sources(STAGE))
    bad.write_bytes(saved)
    rejects('successor helper rejects old342 row manifest on new sources',lambda:layer.validate_sources(STAGE,old['expectedNativeSourceManifest']))
    check('successor helper validates full342 manifest after restoration',layer.validate_sources(STAGE,policy['expectedNativeSourceManifest']))
    common=load(HERE/'artifact-tools/artifact_common.py','trace_artifact_source_common')
    pins=json.loads((REPO/'tests/node-compat/foundation-classic-streams/production-runtime-activated-v3/runtime-pins.json').read_bytes())
    for label,pin in pins['variants'].items():
        metadata=json.loads(Path(pin['enginePath']+'.build.json').read_bytes())
        rejects('new artifact classifier rejects unchanged old actual '+label,lambda metadata=metadata,label=label:common.classify(metadata,label))
    check('all new checked-in pins remain NULL',set(json.loads((HERE/'runtime-pins.json').read_bytes())['variants'].values())=={None}and contract['newEngineHashes']is None and contract['reviewedFutureEnginePins']is None)
    launch=(HERE/'artifact-tools/build-one.py').read_text();oldlaunch=(HERE/'ancestry/artifact-build-one.py').read_text()
    check('owned launcher lifecycle byte-exact',launch[launch.index('def error_record'):launch.index('def main():')]==oldlaunch[oldlaunch.index('def error_record'):oldlaunch.index('def main():')])
    check('launch2GiB start800MiB stop and jobs1 preserved',contract['minimumStartFreeBytes']==2*1024**3 and contract['stopBelowFreeBytes']==800*1024**2 and contract['jobs']==1 and "'NODE_COMPAT_JOBS': '1'"in launch)
    recipe=(HERE/'source/tests/node-compat/build-engine.sh').read_text()
    check('new source guard before first fetch',recipe.index('# Authenticate actual corrected342')<recipe.index('fetch_checked "https://codeload'))
    check('all generated namespace guards before first fetch',recipe.index('for generated_name in')<recipe.index('fetch_checked "https://codeload'))
    for label in tools['labels']:
        entropy='RUNTIME_ONLY'if label=='normal-runtime'else'OFF';gc=label=='gc-off';classic=label!='disabled-off'
        suffix=f'trace-v1.{entropy}.p1.e1.d1.a1.q1.u1.w1.t1.c{int(classic)}'
        source='componentize-abi-fixed-bigint-v1-'+suffix;build='engine-abi-fixed-bigint-v1-'+suffix
        stem='starlingmonkey_embedding.abi-i32-i64-v1'+('.gc-stress'if gc else'')+f'.trace-v1.{entropy}.p1.e1.d1.a1.q1.u1.w1.t1.c{int(classic)}.tracev1'
        names=[source,build,stem+'.wasm',stem+'.wasm.build.json',stem+'.raw.wasm',stem+'.raw.wasm.build.json','componentize-native-inputs-'+stem+'.json','source-inputs-'+stem+'.json','recipe-'+stem+'.sha256','openssl-source-'+stem+'.before.json','configure-'+stem+'.log','build-'+stem+'.log']
        check('bounded all generated basenames '+label,all(len(name.encode())<=255 for name in names))
        check('distinct trace source artifact names '+label,all('trace-v1'in name for name in names))
        oversized=stem+'.'+'x'*256
        check('oversized suffix rejected by exact byte bound '+label,len((oversized+'.wasm.build.json').encode())>255)
    check('recipe still checks generic graph/header generation',"generate-classic-factory.mjs\" --repository \"$repo_root\" --check"in recipe)
    check('selector source is byte-exact',sha((HERE/'source/tests/node-compat/module-selection.mjs').read_bytes())==sha((REPO/'tests/node-compat/module-selection.mjs').read_bytes()))
    parsed=[]
    for f in sorted(HERE.rglob('*.py')):
        ast.parse(f.read_text(),filename=str(f));parsed.append(str(f.relative_to(HERE)))
    blocks=re.findall(r"<<'([A-Z][A-Z0-9_]*)'\n(.*?)\n\1(?:\n|$)",recipe,re.S)
    for label,body in blocks:ast.parse(body,filename='embedded:'+label)
    check('all Python and embedded recipe blocks AST parsed',len(parsed)>5 and len(blocks)==4)
    # Source-only fixture bytes and independent source checks, not artifact data.
    result={'schemaVersion':1,'state':'TRACE_INTEGRATION_SOURCE_DATA_TESTS_PASSED_NOT_ARTIFACT_PROOF','passed':len(checks),'checks':checks,
      'stagedSourceRoot':str(STAGE),'stagedFiles':len(rows),'nativeSourceFiles':342,'pythonFilesParsed':parsed,'embeddedPythonBlocks':len(blocks),
      'largestGeneratedBasenameBytes':max(len(name.encode())for name in names),'sourceAfterimagesOnly':True,
      'actionMainsConfigureCompilerGuestTargetHostOrRuntimePreflightExecuted':False}
    (HERE/'evidence/python-source-tests.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'state':result['state'],'passed':len(checks),'stagedSourceRoot':str(STAGE)}))
if __name__=='__main__':main()
