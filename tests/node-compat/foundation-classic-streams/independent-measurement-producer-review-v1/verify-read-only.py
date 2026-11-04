#!/usr/bin/env python3
"""Independent sealed producer source/data reader. Executes no reviewed code."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import os
import re
import stat
HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
REPO=HERE.parents[3]
BASE=FAMILY/'measurement-producer-candidate-v1'
EXTENSION=FAMILY/'measurement-extension-candidate-v1'
INDEX='35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc'
RECIPE='2dc10045f511ac0c76bfa401f7120c843adbed3289b4477d3e01f2be5ca0fbef'
PARENT='71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
EXTENSION_INDEX='69d61ebd61a93d5c34f56b4c4d2fd5d0988b07495ce5636df102a543a036d0aa'
EXTENSION_REVIEW='190a9e291f6ad28cfcbb55325a031b3981fe228c9f5958e9fe29580194236bc2'
PINS='c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
checks={}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def absolute(path):
    return Path(os.path.abspath(path))


def regular(path, expected=None, size=None):
    path = absolute(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), str(path)
    if size is not None:
        assert before.st_size == size, str(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), str(path)
    row = {'path': str(path), 'sha256': h.hexdigest(), 'bytes': before.st_size}
    assert expected is None or expected == row['sha256'], str(path)
    if str(path) in checks:
        assert checks[str(path)] == row
    checks[str(path)] = row
    return row


def document(path, expected=None, size=None):
    row = regular(path, expected, size)
    data = Path(path).read_bytes()
    assert digest(data) == row['sha256']
    return json.loads(data)


def below(root, path):
    root, path = absolute(root), absolute(path)
    assert path != root and path.is_relative_to(root), (str(root), str(path))
    assert root.is_dir() and not root.is_symlink(), str(root)
    cursor = path
    while cursor != root:
        assert not cursor.is_symlink(), str(cursor)
        cursor = cursor.parent


def membership(root):
    assert root.is_dir() and not root.is_symlink(), str(root)
    rows = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(directory) / name
            mode = path.lstat().st_mode
            kind = ('symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None)
            assert kind, str(path)
            rows.append({'path': str(path.relative_to(root)), 'kind': kind})
        dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
    return sorted(rows, key=lambda row: row['path'])



def transform(before, edits):
    after = before
    applications = []
    for edit in edits:
        assert edit['old'], 'No ambiguous empty source match'
        assert after.count(edit['old']) == edit.get('occurrences',1), edit['old']
        positions = [match.start() for match in re.finditer(re.escape(edit['old']),after)]
        delta = len(edit['new'])-len(edit['old'])
        applications.append((edit,[position+number*delta for number,position in enumerate(positions)],after))
        after = after.replace(edit['old'],edit['new'])
    reverse = after
    for edit,positions,previous in reversed(applications):
        for position in reversed(positions):
            assert reverse[position:position+len(edit['new'])] == edit['new']
            reverse = reverse[:position]+edit['old']+reverse[position+len(edit['new']):]
        assert reverse == previous
    assert reverse == before
    return after


def unified(text):
    lines = text.splitlines(keepends=True)
    result = {}
    cursor = 0
    while cursor < len(lines):
        assert lines[cursor].startswith('--- ')
        old_name = lines[cursor][4:].strip()
        cursor += 1
        assert lines[cursor].startswith('+++ ')
        new_name = lines[cursor][4:].strip()
        cursor += 1
        name = new_name[2:] if new_name.startswith('b/') else new_name
        hunks = []
        while cursor < len(lines) and not lines[cursor].startswith('--- '):
            match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[cursor])
            assert match, lines[cursor]
            old_start,old_count,new_start,new_count = [int(value) if value is not None else 1 for value in match.groups()]
            cursor += 1
            body = []
            while cursor < len(lines) and not lines[cursor].startswith(('@@ ','--- ')):
                assert lines[cursor][0] in ' +-'
                body.append(lines[cursor])
                cursor += 1
            assert sum(line[0] in ' -' for line in body) == old_count
            assert sum(line[0] in ' +' for line in body) == new_count
            hunks.append((old_start,old_count,new_start,new_count,body))
        assert name not in result
        result[name] = {'old':old_name,'new':new_name,'hunks':hunks}
    return result


def patched(data, patch, reverse=False):
    source = data.decode().splitlines(keepends=True)
    result, cursor = [],0
    for old_start,old_count,new_start,new_count,body in patch['hunks']:
        start,count = (new_start,new_count) if reverse else (old_start,old_count)
        offset = start - 1 if count else start
        assert cursor <= offset <= len(source)
        result += source[cursor:offset]
        expected = [line[1:] for line in body if line[0] in (' +' if reverse else ' -')]
        replacement = [line[1:] for line in body if line[0] in (' -' if reverse else ' +')]
        assert source[offset:offset+count] == expected
        result += replacement
        cursor = offset+count
    result += source[cursor:]
    return ''.join(result).encode()



def indexed(root,expected,count):
    value=document(root/'index.json',expected);rows={r['path']:r for r in value['files']}
    assert len(rows)==len(value['files'])==count
    for name,row in rows.items():
        assert not Path(name).is_absolute()and '..'not in Path(name).parts
        below(root,root/name);regular(root/name,row['sha256'],row['bytes'])
    observed=membership(root)
    assert not any(row['kind']=='symlink'for row in observed)
    assert {row['path']for row in observed if row['kind']=='file'}==set(rows)|{'index.json'}
    return value


def main():
    index=indexed(BASE,INDEX,43)
    receipt=document(BASE/'source-receipt.json')
    assert receipt['state']=='EXECUTABLE_SOURCE_READY_NO_BUILD_OR_RUNTIME_ACCEPTANCE'
    assert receipt['recipeSha256']==RECIPE and receipt['parentRecipeSha256']==PARENT
    assert receipt['configureCompilerLauncherVerifierGuestOrTargetHostActionInvoked']is receipt['runtimeAcceptanceClaim']is receipt['measurementClaim']is False
    seal=document(BASE/'input-freeze.json',receipt['inputFreezeSha256']);consumed={}
    for row in seal['inputs']:
        path=Path(row['path']);assert path.is_absolute()and path not in consumed
        regular(path,row['sha256'],row['bytes']);consumed[path]=row
    assert len(consumed)==receipt['inputFiles']==666
    indexed(EXTENSION,EXTENSION_INDEX,13)
    indexed(FAMILY/'independent-measurement-extension-review-v1',EXTENSION_REVIEW,12)
    extension_receipt=document(EXTENSION/'source-review.json')
    extension_inputs=document(EXTENSION/'input-freeze.json',extension_receipt['inputFreezeSha256'])
    assert len(extension_inputs['inputs'])==401
    for row in extension_inputs['inputs']:regular(row['path'],row['sha256'],row['bytes'])
    contract=document(BASE/'contract.json');assert contract['recipeSha256']==RECIPE and contract['parentRecipeSha256']==PARENT
    assert contract['extensionIndexSha256']==EXTENSION_INDEX
    assert contract['nativeSources']==342 and contract['declaredNativeAndBuildInputs']==344 and contract['externalEmbeddingInputs']==3
    assert len(contract['addonSources'])==2 and contract['exports']==['default','nextTick']
    assert contract['moduleId']=='starling:test-classic-benchmark'and contract['namespace']=='diagnostics::classic_benchmark'
    assert contract['target']=='builtin_diagnostics_classic_benchmark'and contract['linkerFlags']==''
    assert contract['freezeRoot']=='/tmp/starling-node-compat/classic-benchmark-artifacts-v1/native-freeze'
    assert contract['labels']==['benchmark-classic-on','benchmark-classic-off']and contract['reviewedEnginePins']is None
    for row in contract['addonSources']:regular(REPO/row['path'],row['sha256'])
    policy=document(FAMILY/'integration-candidate-v1/policy.json',contract['sourcePolicySha256'])
    assert len(policy['expectedNativeSourceManifest'])==342
    for row in policy['expectedNativeSourceManifest']:
        path=REPO/row['path'];regular(path,row['sha256']);assert consumed[path]['sha256']==row['sha256']
    regular(FAMILY/'integration-candidate-v1/layer-policy.py',contract['sourceHelperSha256'])
    before=(BASE/'before/build-engine.sh').read_text();after=(BASE/'build-classic-benchmark-engine.sh').read_text()
    regular(BASE/'before/build-engine.sh',PARENT);regular(REPO/'tests/node-compat/build-engine.sh',PARENT)
    regular(BASE/'build-classic-benchmark-engine.sh',RECIPE)
    proof=document(BASE/'producer-transformations.json');assert proof['parentRecipeSha256']==PARENT and proof['afterRecipeSha256']==RECIPE
    assert len(proof['edits'])==receipt['producerReverseEdits']==15
    edits=[{'old':r['old'],'new':r['new'],'occurrences':r['count']}for r in proof['edits']]
    assert transform(before,edits)==after
    patches=unified((BASE/'producer.UNAPPLIED.patch').read_text());assert len(patches)==1
    patch=next(iter(patches.values()));assert patched(before.encode(),patch)==after.encode()and patched(after.encode(),patch,True)==before.encode()
    inherited={}
    for name in ['build-one.py','artifact_common.py','tool-pins.json']:
        parent=FAMILY/'integration-candidate-v1/artifact-tools'/name
        assert (BASE/'ancestry'/name).read_bytes()==parent.read_bytes()
        inherited[name]=regular(parent)
    tool_pins=document(BASE/'ancestry/tool-pins.json','f68267eff5126af83c099346d07e5befbf6261ed4ca245e14a68f292f32087e3')
    for row in tool_pins['toolDependencies']:regular(REPO/row['path'],row['sha256'],row['bytes'])
    assert tool_pins['recipeSha256']==PARENT and tool_pins['reviewedEnginePins']is None
    pins=document(FAMILY/'production-adoption-v1/reviewed-runtime-pins-v1.json',PINS)
    metadata=document(pins['variants']['normal-off']['enginePath']+'.build.json',pins['variants']['normal-off']['receiptSha256'])
    assert contract['externalSources']==metadata['componentizeSourceManifest']
    assert {r['path']for r in contract['externalSources']}=={'embedding/embedding.cpp','embedding/embedding.h','CMakeLists.txt'}
    external_root=Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/componentize-source')
    for row in contract['externalSources']:regular(external_root/row['path'],row['sha256'])
    adapter=REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
    regular(adapter,'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0',53512)
    static=document(BASE/'parent-policy-values.json',contract['parentPolicyValuesSha256'])
    for field,values in static.items():
        for key,value in values.items():assert metadata[field][key]==value
    common=(BASE/'benchmark_common.py').read_text();build_policy=(BASE/'benchmark-policy.py').read_text()
    launcher=(BASE/'build-one.py').read_text();freezer=(BASE/'freeze-engine.py').read_text()
    frozen=(BASE/'verify-frozen.py').read_text();exporter=(BASE/'export-pin-candidate.py').read_text()
    preflight=(BASE/'runtime-preflight.mjs').read_text();admission=(BASE/'metadata-admission.mjs').read_text()
    assert after.count('python3 "$packet_root/verify-packet.py" "$1"')==2
    assert after.index('verify-packet.py')<after.index('mkdir -p "$work_root/cache"')<after.index('fetch_checked "https://')
    assert after.index('exceeds255bytes')<after.index('fetch_checked "https://')
    assert after.index('benchmark-policy.py" external "$source_dir"')<after.index('cmake -S "$source_dir"')
    assert after.index('benchmark-policy.py" before')<after.index('cmake --build')<after.rindex('verify-packet.py')<after.index("<<'PY'\nimport datetime")
    assert '-DCMAKE_EXE_LINKER_FLAGS=""'in after and '-DENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK=ON'in after
    assert 'classic-bench-v1'in after and 'artifact_name="sm-classic-bench-v1.c$classic_enabled"'in after
    assert '"$build_jobs" == 1'in after and '"$stress" == 0'in after and '"$oom" == 0'in after and '"$entropy_mode" == OFF'in after
    assert "'NODE_COMPAT_JOBS':'1'"in launcher and "'BINARYEN_CORES':'1'"in launcher and "'CARGO_BUILD_JOBS':'1'"in launcher
    assert "'requiredStartFreeBytes':2147483648"in launcher and "'stopBelowFreeBytes':838860800"in launcher
    assert launcher.index('module.verify(index_sha)')<launcher.index('prepare_output(output,free)')<launcher.index('monitor_owned_command(')
    lifecycle=(BASE/'ancestry/build-one.py').read_text()
    for token in ['start_new_session=True','os.killpg(self.pgid','signal.SIGTERM','signal.SIGKILL','process.wait(timeout=','rawChildExitCode','resultFileWriteError']:
        assert token in lifecycle
    assert 'for command in native+embedding+diagnostic:exact_release_command(command)'in common
    assert "==['-O3']"in common and "==['-DNDEBUG']"in common
    assert "('DEBUG','NDEBUG','NODE_COMPAT_OOM_TESTING')"in common
    assert "('NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER','NODE_COMPAT_ENTROPY_POLICY')"in common
    assert "assert definitions == (['-D' + flag + '=1'] if enabled else [])"in (BASE/'ancestry/artifact_common.py').read_text()
    assert "assert len(native)==61 and len(queue)==1 and len(private)==5"in common
    assert "assert len(strict)==4"in common
    assert "text.index(line)>text.index('NS_DEF(builtins::node_compat)')"in common
    assert "'builtin_componentize_embedding',CONTRACT['target']"in build_policy
    assert "'starling-raw.wasm/starling-raw.wasm'"in build_policy
    assert "'collectionCommands':commands"in build_policy and "assert commands==previous['collectionCommands']"in build_policy
    assert "assert digest(data)==row['sha256']and len(data)==row['bytes']"in build_policy
    assert "validate_external_sources(metadata['componentizeSourceManifest'],Path(cache['CMAKE_HOME_DIRECTORY']))"in build_policy
    assert "assert len(ev['before'])==len(ev['after'])==8"in common
    assert "'tool-witnesses.json'"in common and "'toolWitnesses'"in common
    assert "add(adapter(),'tooling/wasi_snapshot_preview1.wasm',ADAPTER,True)"in freezer
    assert "len(own('tooling/wasi_snapshot_preview1.wasm',ADAPTER))==53512"in common
    assert "assert path.stat().st_size==53512"in common
    assert common.count('adapter()')>=2
    assert "sorted(CONTRACT['externalSources']"in common
    assert "classify(metadata,label) # Must precede any original engine stat/read."in freezer
    assert freezer.index('classify(metadata,label)')<freezer.index('engine=checked(original_engine,')
    assert freezer.index('validate_plan(plan,receipt_path,OUTPUT)')<freezer.index('execute_plan(plan,OUTPUT)')<freezer.index("with receipt_path.open('x')")
    assert "'reviewedPinsCreated':False"in freezer and "'runtimeAcceptanceClaim':False"in freezer
    assert 'productionSelectorRefused' in freezer and 'metadata-admission.mjs'in freezer
    for token in ['Cargo.toml','Cargo.lock','openssl-before.json','openssl-receipt.txt','openssl-configure.txt','openssl-configdata.pm','libcrypto.a','licenses/openssl-LICENSE.txt']:
        assert token in freezer
    assert "audit['sourceFilesVerified']==4650"in freezer and "audit['beforeAndAfterBuild']is True"in freezer
    assert "UNREVIEWED_CLASSIC_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V1"in exporter
    assert "with target.open('x')"in exporter and 'reviewed-pins.json'not in exporter
    null_pins=document(BASE/'reviewed-pins.json');assert null_pins['state']=='UNCONFIGURED_CLASSIC_BENCHMARK_DIAGNOSTIC_FREEZES'
    assert all(value is None for value in null_pins['variants'].values())
    assert 'ROOT_REVIEWED_CLASSIC_BENCHMARK_DIAGNOSTIC_FREEZES_V1'in preflight and "'reviewed-classic-benchmark-diagnostic-freeze'"in preflight
    assert preflight.index('selectPin(JSON.parse(raw)')<preflight.index('async function verify()')<preflight.index('spawnSync(')
    assert "await regular(join(here,'index.json'),indexSha)"in preflight
    assert "diagnosticExternalIds:Object.freeze(['starling:test-classic-benchmark'])"in preflight
    assert "assert.equal(metadata.diagnosticOnly,true"in admission and 'Diagnostic engines are never classic production'in admission
    assert "...(choice.classicStreamsEnabled?['classic-streams/export-manifest.classic-streams.node-v22.14.0.json']:[])"in admission
    assert 'metadataProjected:false'in admission and 'engineBytesRead:false'in admission
    assert "assert.equal(hash(await readFile(validatorPath)),validator.sha256)"in admission
    # Independently parse Python/embedded Python without importing the modules.
    parsed=[]
    for path in sorted(BASE.rglob('*.py')):
        ast.parse(path.read_text());parsed.append(str(path.relative_to(BASE)))
    blocks=re.findall(r"<<'(PY[A-Z]*)'\n(.*?)\n\1",after,re.S);assert len(blocks)==4
    for marker,code in blocks:ast.parse(code)
    owner_python=document(BASE/'python-test-results.json');owner_node=document(BASE/'host-test-results.json');syntax=document(BASE/'syntax-results.json')
    assert owner_python['passed']==len(owner_python['cases'])==72 and owner_python['syntheticPositiveModelsAreNotArtifactProof']is True
    assert owner_python['configureCompilerLauncherGuestOrTargetHostInvoked']is False
    assert owner_node['passed']==len(owner_node['cases'])==19 and owner_node['positiveDeclarationModelsAreNotArtifactAdmission']is True
    assert owner_node['engineBytesRead']is owner_node['pythonVerifierInvoked']is owner_node['toolchainOrPackagerLoaded']is False
    assert syntax['bashStatus']==0 and len(syntax['javascript'])==3 and syntax['embeddedPythonBlocks']==4
    for row in syntax['javascript']:
        regular(BASE/row['path'],row['sha256']);assert row['status']==0
    for row in syntax['pythonAST']:regular(BASE/row['path'],row['sha256'])
    corrections=document(BASE/'preparation-history/peer-corrections.json');assert len(corrections['findings'])==3 and corrections['actualBuildConfigureGuestOrHostActions']is False
    # Recheck sealed boundaries after all source and AST reads.
    regular(BASE/'index.json',INDEX);regular(BASE/'build-classic-benchmark-engine.sh',RECIPE)
    regular(REPO/'tests/node-compat/build-engine.sh',PARENT);regular(EXTENSION/'index.json',EXTENSION_INDEX)
    result={'schemaVersion':1,'state':'INDEPENDENT_MEASUREMENT_PRODUCER_SOURCE_REVIEW_PASSED_NOT_BUILD_APPROVAL',
        'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidateIndex':regular(BASE/'index.json',INDEX),
        'indexedFilesRehashed':43,'consumedInputRowsRehashed':666,'parentExtensionIndexedFilesRehashed':13,'parentExtensionConsumedRowsRehashed':401,
        'recipeSha256':RECIPE,'parentRecipeSha256':PARENT,'reversibleRecipeEditsReconstructed':15,'unifiedPatchForwardReverseExact':True,
        'nativeSourceRowsRehashed':342,'addonSourceBuildRows':2,'declaredNativeBuildInputs':344,'externalEmbeddingRowsPinnedAndRehashed':3,
        'explicitRepositoryAdapter':regular(adapter),'inheritedLifecycleAndArtifactHelpersByteExact':inherited,
        'inheritedToolDependenciesRehashed':len(tool_pins['toolDependencies']),'pythonFilesParsed':parsed,'embeddedPythonBlocksParsed':4,
        'ownerSourceTestEvidence':{'python':72,'node':19,'bashSyntax':0,'javascriptSyntaxFiles':3,'newSubprocessesRunByThisReader':False},
        'draftCorrectionsClosed':['Explicit release53512 adapter copy and frozen/live authentication','Exact63 compile commands with Release/OOM/public macro conflict rejection','All3 fixed external source hashes before configure and in frozen validation'],
        'findings':['Actual CMake hook/install timing and rooted extension APIs remain the exact previously reviewed13/401 proposal.',
          '342 native plus2 benchmark inputs remain distinct from external embedding3; authentic current source policies and all15 standalone recipe edits preserve parent build ancestry.',
          'Both ordinary Release/OFF labels have the same finite prerequisites, extension, empty linker flags and one-job resource gates; CLASSIC alone differs. Diagnostic/private macro placement is validated on61native+embedding1+diagnostic1 actual command witnesses.',
          'Cache, compile database, installer, parent/final Ninja command text, stderr and tool witnesses have real pre/post capture paths and exact-byte checks. Unknown/duplicate native TUs and mismatched command operands are rejected.',
          'Exclusive new namespaces, whole source gates before fetch and after Ninja, original/copy rehashes, Rust/OpenSSL4650 audit/config/license evidence and release adapter boundaries remain explicit.',
          'Frozen diagnostic metadata must be refused by the unchanged production selector. Exporter creates only unreviewed tuples; NULL pins and unknown states stop raw admission before artifact/tool access.',
          'Future raw admission binds exact Root authority/source/receipt digests and exposes only8or9 selected native manifests plus the one diagnostic module ID. Component workload/tool-root/correctness activation is still separate.'],
        'limitations':['This reader performed current-byte hashing, exact source reconstruction, AST parsing and source inspection only; owner72Python/19Node reports are authenticated evidence, not reruns.',
          'No configure, compiler, launcher, native producer/freezer/exporter/verifier main, Node admission, componentizer, guest, target host or timing action ran in this review.',
          'No actual diagnostic engine/pin exists in this packet. Source approval does not establish compile/link/install/runtime correctness, a reviewed artifact, measurement eligibility or performance.',
          'Production pins cannot be reused or relabeled for this extension; builds/actions remain separately unapproved.'],
        'reviewedCodeExecuted':False,'nativeBuildOrActionApproved':False,'productionPinsReusableForDiagnostic':False,'runtimeAcceptanceClaim':False,'measurementClaim':False}
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'verified-files.json').write_text(json.dumps({'schemaVersion':1,'files':sorted(checks.values(),key=lambda row:row['path'])},indent=2)+'\n')
    print(json.dumps({key:result[key]for key in ['state','indexedFilesRehashed','consumedInputRowsRehashed','reversibleRecipeEditsReconstructed','nativeBuildOrActionApproved']}))


if __name__=='__main__':main()
