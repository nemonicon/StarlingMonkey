"""Prepare source afterimages only. Never apply, configure, compile or run guests."""
from pathlib import Path
import copy
import difflib
import hashlib
import json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PARENT=HERE.parent/'integration-candidate-v1'
FIX=HERE.parent/'trace-semantics-candidate-v1'
OLD_POLICY='137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f'
OLD_HELPER='f4a303250ac979206f0c2b358f4dd16d2a5e3a3e3007200901dedba8576b9a1e'
OLD_RECIPE='71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
FIX_INDEX='59c9233c5dd1c9f07c4da16a79abdb58abc9775b37c714f6af179e85f23f0631'
PEER_INDEX='b00a6097c266d110a60ab7fcbe2ab72ed6cf4736192c19ebdc342660c964938f'
REL='tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1'
FROZEN='/tmp/starling-node-compat/production-classic-trace-v1/native-freeze'

def sha(data):return hashlib.sha256(data).hexdigest()
def enc(value):return (json.dumps(value,indent=2)+'\n').encode()
def put(name,data):
    data=data.encode()if isinstance(data,str)else data
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==data,name
    else:path.write_bytes(data)
def canonical(rows):return sha(json.dumps(sorted(rows,key=lambda row:row['path']),separators=(',',':')).encode())
PROOFS=[]
def transformed(origin,edits,name):
    before=origin.read_text();text=before;proof=[]
    for old,new,count,reason in edits:
        assert old and text.count(old)==count,(name,reason,text.count(old),count)
        offsets=[];at=0
        while True:
            at=text.find(old,at)
            if at<0:break
            offsets.append(at);at+=len(old)
        after_offsets=[at+i*(len(new)-len(old))for i,at in enumerate(offsets)]
        text=text.replace(old,new);proof.append({'old':old,'new':new,'count':count,'offsets':after_offsets,'beforeOffsets':offsets,'reason':reason})
    restored=text
    for edit in reversed(proof):
        for at in reversed(edit['offsets']):
            assert restored[at:at+len(edit['new'])]==edit['new']
            restored=restored[:at]+edit['old']+restored[at+len(edit['new']):]
    assert restored==before,name
    put(name,text)
    patch=''.join(difflib.unified_diff(before.splitlines(True),text.splitlines(True),fromfile='a/'+str(origin.relative_to(REPO)),tofile='b/'+name))
    patchname='proofs/'+name.replace('/','__')+'.patch';put(patchname,patch)
    PROOFS.append({'origin':str(origin.relative_to(REPO)),'beforeSha256':sha(before.encode()),'afterimage':name,'afterSha256':sha(text.encode()),'edits':proof,'exactReverseProved':True,'patch':patchname,'patchSha256':sha(patch.encode())})
    return text

def main():
    assert sha((PARENT/'policy.json').read_bytes())==OLD_POLICY
    assert sha((PARENT/'layer-policy.py').read_bytes())==OLD_HELPER
    assert sha((REPO/'tests/node-compat/build-engine.sh').read_bytes())==OLD_RECIPE
    assert sha((FIX/'index.json').read_bytes())==FIX_INDEX
    peer=HERE.parent/'independent-trace-semantics-source-review-v1/index.json'
    assert sha(peer.read_bytes())==PEER_INDEX
    for packet in [FIX,peer.parent]:
        for row in json.loads((packet/'index.json').read_bytes())['files']:
            raw=(packet/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
    old=json.loads((PARENT/'policy.json').read_bytes())
    fix=json.loads((FIX/'source-receipt.json').read_bytes())
    delta=fix['intendedNativeSourceChanges'];assert len(delta)==3
    policy=copy.deepcopy(old)
    policy['version']='sm-private-ticks-classic-streams-trace-source-v1'
    policy['classicPolicyVersion']='sm-classic-streams-trace-install-v1'
    trace={'version':'sm-classic-trace-source-v1','previousPolicySha256':OLD_POLICY,'previousHelperSha256':OLD_HELPER,
      'previousRecipeSha256':OLD_RECIPE,'previousNativeManifestCanonicalSha256':canonical(old['expectedNativeSourceManifest']),
      'fixSourceIndexSha256':FIX_INDEX,'independentFixSourceReviewIndexSha256':PEER_INDEX,
      'sourceDeltaPatchSha256':sha((FIX/'canonical-3file.UNAPPLIED.patch').read_bytes()),
      'transformationProofSha256':sha((FIX/'transformation-proof.json').read_bytes()),
      'changes':delta,'unchangedNativePaths':339,'changedNativePaths':3,'nativeSourcePaths':342,
      'profileVersion':old['profileVersion'],'moduleSurfaceChanged':False,'nativeBoundaryAbiChanged':False,
      'strictPolicyVersionUnchanged':old['strictPolicyVersion'],'protectedPolicyVersionUnchanged':old['protectedPolicyVersion'],
      'rawVendorFilesChanged':0,'schedulerChanged':False,'newHostInterfaces':[],
      'nativePatchFieldMeaning':'The unchanged nativePatchSha256 identifies the original classic installation patch; sourceDeltaPatchSha256 is the reviewed three-file successor delta. Both are required ancestry, never one relabelled patch.'}
    policy['classicTraceSourcePolicy']=trace
    before={row['path']:row['sha256']for row in old['expectedNativeSourceManifest']}
    for row in delta:
        assert before[row['path']]==row['beforeSha256']
        assert policy['sourceLayer'][row['path']]['afterSha256']==row['beforeSha256']
        policy['sourceLayer'][row['path']]['afterSha256']=row['afterSha256']
        item=next(item for item in policy['expectedNativeSourceManifest']if item['path']==row['path']);item['sha256']=row['afterSha256']
        raw=(FIX/'proposed'/Path(row['path']).name).read_bytes();assert sha(raw)==row['afterSha256']and len(raw)==row['afterBytes']
        put('source/'+row['path'],raw)
    assert sum(row['sha256']==before[row['path']]for row in policy['expectedNativeSourceManifest'])==339
    put('policy.json',enc(policy));p_sha=sha(enc(policy))
    ancestry='''\n# Exact previous342 source ancestry is data, never an engine metadata adapter.\ndef verify_trace_ancestry():\n    previous=HERE.parent/'integration-candidate-v1'\n    assert digest(previous/'policy.json')==POLICY['classicTraceSourcePolicy']['previousPolicySha256']\n    assert digest(previous/'layer-policy.py')==POLICY['classicTraceSourcePolicy']['previousHelperSha256']\n    assert digest(previous/'source/tests/node-compat/build-engine.sh')==POLICY['classicTraceSourcePolicy']['previousRecipeSha256']\n    old=json.loads((previous/'policy.json').read_bytes())\n    before={row['path']:row['sha256']for row in old['expectedNativeSourceManifest']}\n    after={row['path']:row['sha256']for row in POLICY['expectedNativeSourceManifest']}\n    changes={row['path']:row for row in POLICY['classicTraceSourcePolicy']['changes']}\n    assert len(before)==len(after)==342 and set(before)==set(after)\n    assert len(changes)==3 and sum(before[path]==after[path]for path in before)==339\n    for path,row in changes.items():assert before[path]==row['beforeSha256']and after[path]==row['afterSha256']\n    assert POLICY['strictPolicyVersion']==old['strictPolicyVersion']\n    assert POLICY['protectedPolicyVersion']==old['protectedPolicyVersion']\n    assert POLICY['embedding']==old['embedding']and POLICY['nativePatchSha256']==old['nativePatchSha256']\n    fix=HERE.parent/'trace-semantics-candidate-v1'\n    assert digest(fix/'index.json')==POLICY['classicTraceSourcePolicy']['fixSourceIndexSha256']\n    for row in json.loads((fix/'index.json').read_bytes())['files']:\n        target=fix/row['path'];assert not target.is_symlink()and target.stat().st_size==row['bytes']and digest(target)==row['sha256']\n    assert digest(fix/'canonical-3file.UNAPPLIED.patch')==POLICY['classicTraceSourcePolicy']['sourceDeltaPatchSha256']\n    assert digest(fix/'transformation-proof.json')==POLICY['classicTraceSourcePolicy']['transformationProofSha256']\n    return True\nverify_trace_ancestry()\n'''
    release_check="""def _release(words):
    assert [word for word in words if word.startswith('-O')]==['-O3'],'Exactly one Release optimization flag required'
    assert [word for word in words if word=='-DNDEBUG'or word.startswith('-DNDEBUG=')]==['-DNDEBUG'],'Exact NDEBUG definition required'
    assert '-UNDEBUG'not in words and '-UDEBUG'not in words and not any(word.startswith('-DDEBUG')for word in words)
    assert not any(word=='-DNODE_COMPAT_OOM_TESTING'or word.startswith('-DNODE_COMPAT_OOM_TESTING=')for word in words)
    assert '-UNODE_COMPAT_OOM_TESTING'not in words
"""
    helper=transformed(PARENT/'layer-policy.py',[
      ("POLICY_SHA256='"+OLD_POLICY+"'","POLICY_SHA256='"+p_sha+"'",1,'Require corrected exact342 policy'),
      ("PARENT_ROOT=HERE.parents[1]",ancestry+"PARENT_ROOT=HERE.parents[1]",1,'Authenticate339+3 source ancestry without old metadata projection'),
      ("    metadata['classicStreamsPolicy']={","    metadata['classicTraceSourcePolicy']=copy.deepcopy(POLICY['classicTraceSourcePolicy'])\n    metadata['classicStreamsPolicy']={",1,'Write explicit source provenance from the new actual build'),
      ('def validate_classic_compilation(',release_check+'def validate_classic_compilation(',1,'Reject conflicting Release/DEBUG/OOM compiler definitions'),
      ("assert '-O3'in words and '-DNDEBUG'in words and '-UNDEBUG'not in words and not any(word.startswith('-DDEBUG')for word in words),'Need actual Release compile flags'","_release(words)\n        _macro(words,'NODE_COMPAT_STRICT_INITIALIZATION',True)\n        _macro(words,'NODE_COMPAT_INTERNAL_TICKS',ticks)",1,'Exact compile evidence on all native translation units'),
      ("assert '-O3'in words and '-DNDEBUG'in words and '-UNDEBUG'not in words and not any(word.startswith('-DDEBUG')for word in words),'Need actual Release embedding flags'","_release(words)\n        _macro(words,'NODE_COMPAT_STRICT_INITIALIZATION',True)\n        _macro(words,'NODE_COMPAT_INTERNAL_TICKS',ticks)",1,'Exact Release and layout macro evidence on parent embedding'),
    ],'layer-policy.py');h_sha=sha(helper.encode())
    recipe=transformed(REPO/'tests/node-compat/build-engine.sh',[
      ('/tmp/starling-node-compat/improved-build','/tmp/starling-node-compat/classic-trace-v1-build',1,'Distinct production work root'),
      ('build_jobs="${NODE_COMPAT_JOBS:-8}"','build_jobs="${NODE_COMPAT_JOBS:-1}"',1,'One-job default'),
      ('foundation-classic-streams/integration-candidate-v1','foundation-classic-streams/trace-integration-candidate-v1',3,'New source helper at every capture/import'),
      (OLD_HELPER,h_sha,4,'Exact corrected helper before and after build at every capture/decorate guard'),
      (OLD_POLICY,p_sha,1,'Exact corrected source policy'),
      ('policy_suffix="entropy-entry-v1-strict-callback-v3-protected-abort-v2.$entropy_mode.path-$path_enabled.events-$events_enabled.string-decoder-$string_decoder_enabled.assert-$assert_enabled.querystring-$querystring_enabled.util-$util_enabled.stream-web-$stream_web_enabled"\npolicy_suffix="$policy_suffix.private-ticks-v1-$ticks_enabled.classic-v1-$classic_enabled"',
       'policy_suffix="trace-v1.$entropy_mode.p$path_enabled.e$events_enabled.d$string_decoder_enabled.a$assert_enabled.q$querystring_enabled.u$util_enabled.w$stream_web_enabled.t$ticks_enabled.c$classic_enabled"',1,'Bounded distinct source/build namespace; semantic boundary tags remain exact'),
      ('artifact_name="$artifact_name.classic-v1.','artifact_name="$artifact_name.trace-v1.',1,'Distinct actual artifact namespace'),
      ('for generated_name in "$artifact_name.wasm.build.json" "componentize-native-inputs-$artifact_name.json" "source-inputs-$artifact_name.json" "openssl-source-$artifact_name.before.json" "configure-$artifact_name.log" "build-$artifact_name.log"; do',
       'for generated_name in "${source_dir##*/}" "${build_dir##*/}" "$artifact_name.wasm" "$artifact_name.wasm.build.json" "$artifact_name.raw.wasm" "$artifact_name.raw.wasm.build.json" "componentize-native-inputs-$artifact_name.json" "source-inputs-$artifact_name.json" "recipe-$artifact_name.sha256" "openssl-source-$artifact_name.before.json" "configure-$artifact_name.log" "build-$artifact_name.log"; do',1,'Check every parameterized basename including recipe sidecar before fetch'),
      ('fetch_checked "https://codeload.github.com/bytecodealliance/ComponentizeJS/tar.gz/$componentize_revision"',
       '# Authenticate actual corrected342 sources before any archive fetch.\n[[ "$(sha256_file "$layer_root/layer-policy.py")" == '+h_sha+' ]] || exit 1\n[[ "$(sha256_file "$layer_root/policy.json")" == '+p_sha+' ]] || exit 1\npython3 "$layer_root/layer-policy.py" "$repo_root"\nfetch_checked "https://codeload.github.com/bytecodealliance/ComponentizeJS/tar.gz/$componentize_revision"',1,'New source bytes must never be accepted under the previous helper'),
      ("json.dump([{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],open(sys.argv[2],'w'),indent=2)",
       "rows=[{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]\nexpected=[{'path':'embedding/embedding.cpp','sha256':'9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205'},{'path':'embedding/embedding.h','sha256':'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e'},{'path':'CMakeLists.txt','sha256':'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}]\nassert rows==expected,'Exact unchanged external3 sources required before configure'\njson.dump(rows,open(sys.argv[2],'w'),indent=2)",1,'Authenticate unchanged external cpp/header/CMake inputs before configure, and retain original post-build comparison'),
    ],'source/tests/node-compat/build-engine.sh');r_sha=sha(recipe.encode())
    pins=json.loads((PARENT/'admission-pins.json').read_bytes())
    pins.update(state='UNAPPLIED_CLASSIC_TRACE_SOURCE_ADMISSION_CONTRACT',productionRecipeSha256=r_sha,policySha256=p_sha,helperSha256=h_sha,
      sourceContractVersion=trace['version'],previousClassicPolicySha256=OLD_POLICY,previousClassicHelperSha256=OLD_HELPER,
      previousClassicRecipeSha256=OLD_RECIPE,fixSourceIndexSha256=FIX_INDEX,nativeSourceInputs=342,reviewedFutureEnginePins=None)
    put('admission-pins.json',enc(pins));pins_sha=sha(enc(pins))
    old_admission=REPO/'tests/node-compat/classic-streams-admission.mjs'
    old_pins_sha=sha((PARENT/'admission-pins.json').read_bytes())
    admission=transformed(old_admission,[
      (old_pins_sha,pins_sha,1,'Fixed successor source contract'),(OLD_RECIPE,r_sha,1,'Refuse previous recipe identity'),
      ('foundation-classic-streams/integration-candidate-v1/','foundation-classic-streams/trace-integration-candidate-v1/',3,'Load exact successor policy/helper contract'),
      (" const current=entries(metadata.sourceManifest);", " assert.deepEqual(metadata.classicTraceSourcePolicy,policy.classicTraceSourcePolicy,'Exact corrected source provenance required');\n const current=entries(metadata.sourceManifest);",1,'Require explicit actual trace source provenance'),
      ('function compiled(command,',"function release(tokens) {\n  assert.deepEqual(tokens.filter(word=>word.startsWith('-O')),['-O3']);\n  assert.deepEqual(tokens.filter(word=>word==='-DNDEBUG'||word.startsWith('-DNDEBUG=')),['-DNDEBUG']);\n  assert(!tokens.includes('-UNDEBUG')&&!tokens.includes('-UDEBUG')&&!tokens.some(word=>word.startsWith('-DDEBUG')));\n  assert(!tokens.some(word=>word==='-DNODE_COMPAT_OOM_TESTING'||word.startsWith('-DNODE_COMPAT_OOM_TESTING=')));\n  assert(!tokens.includes('-UNODE_COMPAT_OOM_TESTING'));\n}\nfunction compiled(command,",1,'Match exact Release/OOM checks in finite metadata parser'),
      ("assert(tokens.includes('-O3')&&tokens.includes('-DNDEBUG')&&!tokens.includes('-UNDEBUG')&&!tokens.some(x=>x.startsWith('-DDEBUG')));",'release(tokens);',1,'Reject conflicting captured compile flags'),
    ],'source/tests/node-compat/classic-streams-admission.mjs')
    # The existing selector already calls the classic validator, so its code and
    # compatibility/legacy branches need no edits. It is included as an exact witness.
    put('source/tests/node-compat/module-selection.mjs',(REPO/'tests/node-compat/module-selection.mjs').read_bytes())
    fixture=transformed(PARENT/'source-model-fixture.mjs',[
      ('    sourceManifest:copy(policy.expectedNativeSourceManifest),','    classicTraceSourcePolicy:copy(policy.classicTraceSourcePolicy),\n    sourceManifest:copy(policy.expectedNativeSourceManifest),',1,'Explicit synthetic successor parser fixture; never an engine receipt'),
    ],'source-model-fixture.mjs')
    tools=json.loads((PARENT/'artifact-tools/tool-pins.json').read_bytes())
    tools.update(state='SOURCE_ONLY_CLASSIC_TRACE342_ARTIFACT_TOOL_CONTRACT',recipeSha256=r_sha,sourcePolicySha256=p_sha,sourceHelperSha256=h_sha,
      freezeRoot=FROZEN,sourceContractVersion=trace['version'],reviewedEnginePins=None,actualArtifactFreezeExecuted=False)
    deps={}
    for row in tools['toolDependencies']:
        name=row['path'].replace('foundation-classic-streams/integration-candidate-v1/','foundation-classic-streams/trace-integration-candidate-v1/')
        if name=='tests/node-compat/build-engine.sh':data=recipe.encode()
        elif name=='tests/node-compat/classic-streams-admission.mjs':data=admission.encode()
        elif name.startswith(REL+'/'):data=(HERE/name[len(REL)+1:]).read_bytes()
        else:data=(REPO/name).read_bytes()
        deps[name]={'path':name,'sha256':sha(data),'bytes':len(data)}
    # The helper's exact previous342/fix ancestry must be in the consumed tool closure.
    extra=[PARENT/'policy.json',PARENT/'layer-policy.py',PARENT/'source/tests/node-compat/build-engine.sh',FIX/'index.json']
    extra += [FIX/row['path']for row in json.loads((FIX/'index.json').read_bytes())['files']]
    for f in extra:
        name=str(f.relative_to(REPO));data=f.read_bytes();deps[name]={'path':name,'sha256':sha(data),'bytes':len(data)}
    tools['toolDependencies']=sorted(deps.values(),key=lambda row:row['path'])
    put('artifact-tools/tool-pins.json',enc(tools));t_sha=sha(enc(tools))
    for name in ['build-one.py','freeze-engine.py','artifact_common.py','metadata-admission.mjs','export-pin-candidate.py']:
        origin=PARENT/'artifact-tools'/name;text=origin.read_text();edits=[]
        def add(old,new,why):
            n=text.count(old)
            if n:edits.append((old,new,n,why))
        add('/tmp/starling-node-compat/production-classic-artifacts-v1','/tmp/starling-node-compat/production-classic-trace-v1','Exclusive new build/freeze namespace')
        add('/tmp/starling-node-compat/improved-build','/tmp/starling-node-compat/classic-trace-v1-build','Distinct source/build cache root')
        add("'p342v1'","'tracev1'",'Distinct fresh launcher artifact tag')
        add('immutable-release-engine-frozen','immutable-trace-release-engine-frozen','Distinct corrected-source freeze schema state')
        add('unreviewed-classic-production-freeze-pin-candidate','unreviewed-classic-trace-production-freeze-pin-candidate','Never relabel previous pins')
        add('UNREVIEWED_CLASSIC_PRODUCTION_PIN_CANDIDATES_V1','UNREVIEWED_CLASSIC_TRACE_PRODUCTION_PIN_CANDIDATES_V1','Unreviewed corrected-source pin data only')
        add("free = lambda: os.statvfs(work).f_bavail * os.statvfs(work).f_frsize","free = lambda: os.statvfs(work if work.exists() else work.parent).f_bavail * os.statvfs(work if work.exists() else work.parent).f_frsize",'Check2GiB before new work root exists; preserve lifecycle')
        if name=='artifact_common.py':
            add("    return gc, entropy","    assert metadata.get('classicTraceSourcePolicy') == json.loads((HERE.parent / 'policy.json').read_bytes())['classicTraceSourcePolicy'], 'Corrected source provenance required before engine use'\n    return gc, entropy",'Reject previous or projected provenance before engine bytes')
            add('def compile_command(',release_check.replace('def _release(words):','def exact_release(words):')+'\ndef compile_command(','Exact Release/OOM rules in freezer command observations')
            add("    assert '-O3' in args and '-DNDEBUG' in args and '-UNDEBUG' not in args and not any(x.startswith('-DDEBUG') for x in args)","    exact_release(args)",'Do not accept shadowing optimization/debug flags in freezer')
            add('    checked(receipt_path, receipt_digest)',"    semantic = receipt['semanticSourceProvenance']\n    assert semantic['fixSourceIndexSha256'] == metadata['classicTraceSourcePolicy']['fixSourceIndexSha256']\n    base = output / 'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1'\n    assert semantic['correctedReceiptAnnotationBase'] == str(base)\n    assert semantic['primaryPinsPath'] == str(base / 'primary-source-pins.json')\n    assert semantic['nodeMitNoticePath'] == str(base / 'LICENSE.node')\n    assert inventory[semantic['primaryPinsPath']]['sha256'] == semantic['primaryPinsSha256']\n    assert inventory[semantic['nodeMitNoticePath']]['sha256'] == semantic['nodeMitNoticeSha256']\n    primary = json.loads(Path(semantic['primaryPinsPath']).read_bytes())\n    for row in primary['sources']:\n        path = base / row['path']; assert inventory[str(path)]['sha256'] == row['sha256'] and inventory[str(path)]['bytes'] == row['bytes']\n    checked(receipt_path, receipt_digest)",'Retain and validate the proposal-relative Node primary/MIT annotation in the frozen tool subtree')
        if name=='metadata-admission.mjs':
            add("export const RECIPE=contract.productionRecipeSha256;","export const RECIPE=contract.productionRecipeSha256;\nconst sourcePolicy=JSON.parse(await readFile(join(here,'../policy.json')));\nassert.equal(hash(await readFile(join(here,'../policy.json'))),contract.policySha256);",'Bind source policy before diagnostic/previous metadata classification')
            add(' return Object.freeze(options);'," assert.deepEqual(metadata.classicTraceSourcePolicy,sourcePolicy.classicTraceSourcePolicy,'Corrected source provenance required before engine use');\n return Object.freeze(options);",'No previous metadata source relabelling')
        if name=='export-pin-candidate.py':
            add("        'sourceFiles': 342, 'recipeSha256': RECIPE,","        'sourceContractVersion': 'sm-classic-trace-source-v1', 'classicTraceSourcePolicy': metadata['classicTraceSourcePolicy'],\n        'sourceFiles': 342, 'recipeSha256': RECIPE,",'Export source-version evidence without activating pins')
        if name=='freeze-engine.py':
            add("        'nativeInputsVerified': 342,", "        'classicTraceSourcePolicy': metadata['classicTraceSourcePolicy'],\n        'nativeInputsVerified': 342,",'Preserve actual source provenance in frozen receipt')
            add("        'copies': [{'path': str(row['target'])", "        'semanticSourceProvenance': {\n            'fixSourceIndexSha256': metadata['classicTraceSourcePolicy']['fixSourceIndexSha256'],\n            'correctedReceiptAnnotationBase': str(OUTPUT / 'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1'),\n            'primaryPinsPath': str(OUTPUT / 'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/primary-source-pins.json'),\n            'primaryPinsSha256': next(row['sha256'] for row in dependency_rows if row['path'] == 'tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/primary-source-pins.json'),\n            'nodeMitNoticePath': str(OUTPUT / 'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/LICENSE.node'),\n            'nodeMitNoticeSha256': next(row['sha256'] for row in dependency_rows if row['path'] == 'tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/LICENSE.node'),\n            'annotationInterpretation': 'primaryPins in the unchanged corrected receipt is relative to the reviewed fix proposal, preserved at correctedReceiptAnnotationBase; not relative to the native canonical source directory.'},\n        'copies': [{'path': str(row['target'])",'Preserve an explicit interpretable Node primary pin and MIT notice mapping without editing the three native afterimages')
        if name in ['artifact_common.py','metadata-admission.mjs']:
            add('f68267eff5126af83c099346d07e5befbf6261ed4ca245e14a68f292f32087e3',t_sha,'Fixed successor tool dependency graph')
        transformed(origin,edits,'artifact-tools/'+name)
    # Keep immutable original artifact ancestry files required by the existing freezer.
    for f in (PARENT/'artifact-tools/ancestry/production-artifacts-v1').iterdir():
        put('artifact-tools/ancestry/production-artifacts-v1/'+f.name,f.read_bytes())
    put('artifact-tools/parent-inputs.json',(PARENT/'artifact-tools/parent-inputs.json').read_bytes())
    runtime=transformed(HERE.parent/'production-runtime-activated-v3/runtime-contract.mjs',[
      ('REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1','REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1',1,'Distinct reviewed source-version artifact document'),
      ('reviewed-real-classic-production-freeze','reviewed-real-classic-trace-production-freeze',1,'Previous artifact pin states never enter corrected source admission'),
      ("  assert.equal(pin.gcStress", "  assert.equal(pin.sourceContractVersion,'sm-classic-trace-source-v1');\n  assert.equal(pin.classicTraceSourcePolicy?.fixSourceIndexSha256,'"+FIX_INDEX+"');\n  assert.equal(pin.gcStress",1,'Require explicit corrected source version and fix ancestry'),
    ],'runtime-contract.mjs')
    put('runtime-pins.json',enc({'schemaVersion':1,'state':'UNCONFIGURED_CLASSIC_TRACE_PRODUCTION_ARTIFACT_PINS_SOURCE_ONLY','sourceContractVersion':trace['version'],
      'variants':{label:None for label in tools['labels']},'reviewedFutureEnginePins':None,'runtimeAcceptanceClaim':False}))
    put('contract.json',enc({'schemaVersion':1,'state':'UNAPPLIED_TRACE_INTEGRATION_SOURCE_PROPOSAL_ACTIONS_HELD','sourceContractVersion':trace['version'],
      'sourcePolicySha256':p_sha,'sourceHelperSha256':h_sha,'productionRecipeSha256':r_sha,'admissionPinsSha256':pins_sha,
      'productionAdmissionSha256':sha(admission.encode()),'productionSelectorSha256':sha((REPO/'tests/node-compat/module-selection.mjs').read_bytes()),
      'selectorChanged':False,'toolPinsSha256':t_sha,'fixSourceIndexSha256':FIX_INDEX,'independentFixSourceReviewIndexSha256':PEER_INDEX,
      'previousPolicySha256':OLD_POLICY,'previousHelperSha256':OLD_HELPER,'previousRecipeSha256':OLD_RECIPE,
      'nativeSourceFiles':342,'unchangedNativeSourcePaths':339,'changedNativeSourcePaths':3,'moduleProfileVersion':old['profileVersion'],
      'strictPolicyVersion':old['strictPolicyVersion'],'protectedPolicyVersion':old['protectedPolicyVersion'],'strictAndProtectedTagsUnchanged':True,
      'buildRoot':'/tmp/starling-node-compat/classic-trace-v1-build','artifactRoot':'/tmp/starling-node-compat/production-classic-trace-v1',
      'freezeRoot':FROZEN,'minimumStartFreeBytes':2*1024**3,'stopBelowFreeBytes':800*1024**2,'jobs':1,
      'newEngineHashes':None,'reviewedFutureEnginePins':None,'nativeBuildApproved':False,'liveApplicationApproved':False,
      'diagnosticMeasurementProducerRequiresSuccessor':True,'oldMeasurementProducerIndexSha256':'35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc'}))
    put('transformations.json',enc({'schemaVersion':1,'state':'EXACT_SOURCE_TOOL_AFTERIMAGE_DERIVATIONS','files':PROOFS,'nativeChanges':delta,'compiledOrGuestExecuted':False}))
    print(json.dumps({'state':'SOURCE_AFTERIMAGES_PREPARED_ACTIONS_HELD','policySha256':p_sha,'helperSha256':h_sha,'recipeSha256':r_sha,'toolPinsSha256':t_sha,'toolDependencies':len(deps),'proofs':len(PROOFS)}))

if __name__=='__main__':main()
