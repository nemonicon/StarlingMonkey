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
BASE=FAMILY/'measurement-producer-candidate-v2'
EXTENSION=FAMILY/'measurement-extension-candidate-v1'
INDEX='e2f8e7be30f32d28f278e39b6ec8ef0a0a6ca01ed2f3dec6aaf4a4374807819f'
RECIPE='baa0295a51fbc920363ec68d7c3a6f738d5828a8e62a0c0ea3ce2c664ff1df17'
PARENT='3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'
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


def contains(text,*values):
    for value in values:assert value in text,value


def main():
    index=indexed(BASE,INDEX,36)
    assert index['state']=='SEALED_UNEXECUTED_CORRECTED_TRACE_BENCHMARK_PRODUCER_SOURCE'
    receipt=document(BASE/'source-receipt.json')
    assert receipt['recipeSha256']==RECIPE and receipt['parentProductionRecipeSha256']==PARENT
    assert receipt['configureCompilerLauncherFreezerExporterGuestOrTargetHostActionInvoked']is receipt['runtimeAcceptanceClaim']is receipt['measurementClaim']is False
    seal=document(BASE/'input-freeze.json',receipt['inputFreezeSha256'])
    assert seal['preparationContext']['root']==str(REPO)
    assert seal['preparationContext']['pathResolution']=='absolute-original-preparation-context-not-relocated'
    consumed={}
    for row in seal['inputs']:
        path=Path(row['path']);assert path.is_absolute()and path not in consumed
        consumed[path]=(row['sha256'],row['bytes']);regular(path,*consumed[path])
    assert len(consumed)==receipt['inputFiles']==1302
    parents=[('measurement-producer-candidate-v1','35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc',43),
      ('measurement-extension-candidate-v1',EXTENSION_INDEX,13),
      ('independent-measurement-extension-review-v1',EXTENSION_REVIEW,12),
      ('trace-integration-candidate-v1','224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b',159)]
    expected={}
    def add(path,sha=None,size=None):
        path=absolute(path);row=regular(path,sha,size);value=(row['sha256'],row['bytes'])
        if path in expected:assert expected[path]==value
        expected[path]=value
    for name,pin,count in parents:
        packet=FAMILY/name;parent=indexed(packet,pin,count);add(packet/'index.json',pin)
        for row in parent['files']:add(packet/row['path'],row['sha256'],row['bytes'])
    for name,count in [('measurement-extension-candidate-v1',401),('measurement-producer-candidate-v1',666)]:
        original=document(FAMILY/name/'input-freeze.json');assert len(original['inputs'])==count
        for row in original['inputs']:add(row['path'],row['sha256'],row['bytes'])
    contract=document(BASE/'contract.json');policy=document(BASE/'policy.json',contract['sourcePolicySha256'])
    trace=FAMILY/'trace-integration-candidate-v1';production=document(trace/'contract.json')
    assert contract['sourcePolicySha256']==production['sourcePolicySha256']=='891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c'
    assert contract['sourceHelperSha256']==production['sourceHelperSha256']=='43bae8056534c1a6f384961e0b054a68d44d30030e21897bd9688a8fc8b65bc9'
    assert contract['recipeSha256']==RECIPE and contract['parentRecipeSha256']==production['productionRecipeSha256']==PARENT
    assert contract['classicTraceSourcePolicy']==policy['classicTraceSourcePolicy']==document(trace/'policy.json')['classicTraceSourcePolicy']
    assert contract['sourceContractVersion']=='sm-classic-trace-source-v1'
    assert contract['reviewedEnginePins']is None and contract['nativeSources']==342 and contract['declaredNativeAndBuildInputs']==344
    assert contract['previousProducerIndexSha256']==parents[0][1]and contract['productionTraceSourceIndexSha256']==parents[3][1]
    stage=Path(seal['preparationContext']['correctedReadOnlyWitnessRoot'])
    assert stage==Path('/private/tmp/starling-node-compat/classic-trace-source-v1')
    assert len(policy['expectedNativeSourceManifest'])==342
    for row in policy['expectedNativeSourceManifest']:add(stage/row['path'],row['sha256'])
    tools=document(BASE/'ancestry/tool-pins.json')
    assert tools==document(trace/'artifact-tools/tool-pins.json')and len(tools['toolDependencies'])==92
    for row in tools['toolDependencies']:add(stage/row['path'],row['sha256'],row['bytes'])
    assert len(contract['addonSources'])==2 and contract['externalEmbeddingInputs']==len(contract['externalSources'])==3
    for row in contract['addonSources']:add(stage/row['path'],row['sha256'])
    add('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node','e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
    python=document(BASE/'python-test-results.json');node=document(BASE/'host-test-results.json')
    # The sealer resolves its explicit completed-test-root argument before add().
    tests=Path(python['output']).parent.resolve(strict=True);assert Path(node['output']).parent.resolve(strict=True)==tests
    for child,report in [('python','python-test-results.json'),('node','host-test-results.json')]:
        for suffix in ['stdout.json','stderr.log']:add(tests/(child+'.'+suffix))
        add(tests/child/'results.json')
        assert (tests/child/'results.json').read_bytes()==(BASE/report).read_bytes()
        assert (tests/(child+'.stderr.log')).read_bytes()==(BASE/'evidence'/f'{child}.stderr.log').read_bytes()==b''
        assert (tests/(child+'.stdout.json')).read_bytes()==(BASE/'evidence'/f'{child}.stdout.json').read_bytes()
    # Exact source-time union; no path is reinterpreted relative to a relocation.
    for row in index['files']:
        if row['path']not in ['input-freeze.json','source-receipt.json']:add(BASE/row['path'],row['sha256'],row['bytes'])
    assert consumed==expected,'Whole1302 original-context union mismatch'
    regular(BASE/'before/build-engine.sh',PARENT);before=(BASE/'before/build-engine.sh').read_bytes()
    assert before==(trace/'source/tests/node-compat/build-engine.sh').read_bytes()
    proof=document(BASE/'producer-transformations.json')
    assert proof['parentRecipeSha256']==PARENT and proof['afterRecipeSha256']==RECIPE and len(proof['edits'])==16
    edits=[{**edit,'occurrences':edit['count']}for edit in proof['edits']]
    after=transform(before.decode(),edits).encode()
    regular(BASE/'build-classic-benchmark-engine.sh',RECIPE);assert after==(BASE/'build-classic-benchmark-engine.sh').read_bytes()
    patches=unified((BASE/'producer.UNAPPLIED.patch').read_text());assert len(patches)==1
    patch=next(iter(patches.values()));assert patched(before,patch)==after and patched(after,patch,True)==before
    support=document(BASE/'support-transformations.json');assert support['parentProducerIndexSha256']==parents[0][1]
    assert len(support['files'])==12 and support['actionsInvoked']is False
    support_count=0
    for row in support['files']:
        old=regular(FAMILY/'measurement-producer-candidate-v1'/row['path'],row['beforeSha256']).get('sha256')
        original=(FAMILY/'measurement-producer-candidate-v1'/row['path']).read_text()
        current=(BASE/row['path']).read_text();regular(BASE/row['path'],row['afterSha256'])
        forward=original
        for edit in reversed(row['edits']):
            at=edit['beforeOffset'];assert forward[at:at+len(edit['old'])]==edit['old'];forward=forward[:at]+edit['new']+forward[at+len(edit['old']):]
        reverse=current
        for edit in reversed(row['edits']):
            at=edit['afterOffset'];assert reverse[at:at+len(edit['new'])]==edit['new'];reverse=reverse[:at]+edit['old']+reverse[at+len(edit['new']):]
        assert forward==current and reverse==original and row['forwardAndReverseExact']is True
        support_count+=len(row['edits'])
    for name in ['artifact_common.py','build-one.py','tool-pins.json']:
        assert regular(BASE/'ancestry'/name)['sha256']==regular(trace/'artifact-tools'/name)['sha256']
    assert regular(BASE/'admission-pins.json')['sha256']==regular(trace/'admission-pins.json')['sha256']
    assert regular(BASE/'policy.json')['sha256']==regular(trace/'policy.json')['sha256']
    values=document(BASE/'parent-policy-values.json',contract['parentPolicyValuesSha256'])
    assert 'classicTraceSourcePolicy'not in values # Trace provenance is separately mandatory, not projected parent metadata.
    for field in ['strictEventExceptionPolicy','protectedAbortListenerPolicy','internalTickPolicy','classicStreamsPolicy']:assert field in values
    recipe=after.decode();common=(BASE/'benchmark_common.py').read_text();gate=(BASE/'verify-packet.py').read_text();launcher=(BASE/'build-one.py').read_text()
    contains(recipe,'[[ $# == 2 ]]', 'SOURCE_ROOT must be this containing corrected checkout',
      'python3 "$packet_root/verify-packet.py" "$1" "$repo_root"','-DCMAKE_EXE_LINKER_FLAGS=""',
      '-DCMAKE_PROJECT_ComponentizeJS_INCLUDE="$benchmark_root/benchmark.cmake"','-DENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK=ON',
      'classic-bench-trace-v2','artifact_name="sm-classic-bench-trace-v2.c$classic_enabled"',
      'benchmark-inputs-$artifact_name.json','recipe-$artifact_name.sha256','"${source_dir##*/}"','"${build_dir##*/}"',
      'Benchmark requires Release/OFF/no stress/one job/empty tag','benchmark-policy.py" external "$source_dir"',
      'benchmark-policy.py" before "$build_dir" "$artifact" "$addon_manifest"', 'metadata = benchmark.decorate(metadata, pathlib.Path(artifact))')
    assert recipe.count('python3 "$packet_root/verify-packet.py" "$1" "$repo_root"')==2
    assert recipe.index('verify-packet.py')<recipe.index('mkdir -p "$work_root/cache"')<recipe.index('fetch_checked "https://codeload')
    assert recipe.index('for generated_name in')<recipe.index('fetch_checked "https://codeload')
    assert recipe.index('benchmark-policy.py" external')<recipe.index('cmake -S "$source_dir"')
    post=recipe.index('python3 "$packet_root/verify-packet.py"',recipe.index('cmake --build'))
    assert post<recipe.index('import importlib.util',post)<recipe.index('classic_benchmark_build_policy',post)
    contains(gate,'assert hashlib.sha256(raw).hexdigest()==expected',"rows=json.loads(raw)['files']",'path.is_absolute()',
      'absolute-original-preparation-context-not-relocated','require_source_root(source_root)')
    assert gate.index('assert hashlib.sha256(raw).hexdigest()==expected')<gate.index('rows=json.loads(raw)')<gate.index('from benchmark_common import require_source_root')
    # The selected meaningful clauses are read directly; do not run their bodies.
    for text,needles in [(common,['root.resolve(strict=True)==REPO','layer().validate_sources(root)','capture_addons();tool_dependencies(root);adapter()',"metadata.get('classicTraceSourcePolicy')==CONTRACT['classicTraceSourcePolicy']",'for command in native+embedding+diagnostic:exact_release_command(command)',"'CMAKE_EXE_LINKER_FLAGS':''","text.index(line)>text.index('NS_DEF(builtins::node_compat)')",'semanticSourceProvenance','primaryPinsPath','nodeMitNoticePath','adapter()']),
      (launcher,['module.verify(index_sha)','require_source_root(source_root)',"verify_frozen('benchmark-classic-on')", "'NODE_COMPAT_JOBS':'1'", "'stopBelowFreeBytes':838860800", "'requiredStartFreeBytes':2147483648"]),
      ((BASE/'benchmark-policy.py').read_text(),['validate_external_sources(metadata[\'componentizeSourceManifest\'],Path(cache[\'CMAKE_HOME_DIRECTORY\']))','beforeCaptureSha256'])]:
        for needle in needles:
            assert needle in text,needle
    freeze=(BASE/'freeze-engine.py').read_text()
    assert freeze.index('verifier.verify(index_sha)')<freeze.index('require_source_root(source_root)')<freeze.index('classify(metadata,label)')<freeze.index('engine=checked(original_engine')
    contains(freeze,'verifier.verify(index_sha);validate_plan(plan,receipt_path,OUTPUT)','execute_plan(plan,OUTPUT)',"receipt_path.open('x')",'semanticSourceProvenance',"add(adapter(),'tooling/wasi_snapshot_preview1.wasm'",'for row in dependencies:add(REPO/row[\'path\']',"add(index,'producer/index.json',index_sha,True)")
    raw=(BASE/'runtime-preflight.mjs').read_text();admission=(BASE/'metadata-admission.mjs').read_text()
    contains(raw,'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V2', 'Explicit exact Root-reviewed authority digest required','Explicit containing corrected sourceRoot required',
      "assert.equal(resolve(sourceRoot),containingRoot)","join(here,'verify-frozen.py')",'variant,pin.freezeReceiptSha256,indexSha,containingRoot',
      "const result=await verify()", "await import('./metadata-admission.mjs')", "diagnosticExternalIds:Object.freeze(['starling:test-classic-benchmark'])",'recheck=async()=>{await verify();}')
    assert raw.index('const pin=selectPin')<raw.index('const result=await verify()')<raw.index("await import('./metadata-admission.mjs')")
    assert raw.index('assert.equal(hash(raw),reviewedPinsSha256)')<raw.index('const pin=selectPin')
    contains(admission,'assert.deepEqual(metadata.classicTraceSourcePolicy,contract.classicTraceSourcePolicy', 'assert.deepEqual(metadata.sourceManifest,policy.expectedNativeSourceManifest',
      "assert.throws(()=>selectedManifestsForEngine(metadata,{sourceRoot}),/Diagnostic engines are never classic production/)", 'names=', 'new Set(metadata.sourceManifest.map(row=>row.path)).size,342')
    null=document(BASE/'reviewed-pins.json');assert set(null['variants'].values())=={None}and len(null['variants'])==2
    export=(BASE/'export-pin-candidate.py').read_text();contains(export,'UNREVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V2','require_source_root(sys.argv[1])',"target.open('x')",'requiresIndependentReviewAndSeparateRootAuthority')
    assert python['passed']==len(python['cases'])==77 and node['passed']==len(node['cases'])==22
    assert python['actualEngineBytesRead']is node['engineBytesRead']is node['pythonVerifierInvoked']is node['toolchainOrPackagerLoaded']is False
    syntax=document(BASE/'syntax-results.json');assert len(syntax['javascript'])==3 and syntax['bashStatus']==0 and syntax['embeddedPythonBlocks']==4
    for row in syntax['javascript']:regular(BASE/row['path'],row['sha256']);assert row['status']==0
    ast_paths=[]
    for path in sorted(BASE.rglob('*.py')):ast.parse(path.read_text(),filename=str(path));ast_paths.append(str(path.relative_to(BASE)))
    assert len(ast_paths)==len(syntax['pythonAST'])==12
    for row in syntax['pythonAST']:regular(BASE/row['path'],row['sha256'])
    blocks=re.findall(r"<<'(PY[A-Z]*)'\n(.*?)\n\1",recipe,re.S);assert len(blocks)==4
    for label,code in blocks:ast.parse(code,filename='embedded:'+label)
    # Actual API/CMake/ABI source extension bytes are unchanged from review190a.
    assert contract['extensionIndexSha256']==EXTENSION_INDEX
    extension_inputs=document(EXTENSION/'input-freeze.json');assert len(extension_inputs['inputs'])==401
    for row in contract['addonSources']:regular(REPO/row['path'],row['sha256'])
    for row in contract['externalSources']:
        assert row['sha256'] in {'9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205','de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e','4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}
    regular(REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm','988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0',53512)
    indexed(BASE,INDEX,36);indexed(FAMILY/'measurement-producer-candidate-v1',parents[0][1],43)
    result={'schemaVersion':1,'state':'INDEPENDENT_CORRECTED_MEASUREMENT_PRODUCER_V2_SOURCE_REVIEW_PASSED_NO_ACTIONS',
      'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceIndexSha256':INDEX,'sourceFilesRehashed':36,'sourceInputsRehashed':1302,
      'exactOriginalContextInputUnionReconstructed':True,'originalAbsolutePreparationPathsNotRelocated':True,
      'parentProductionRecipeSha256':PARENT,'diagnosticRecipeSha256':RECIPE,'recipeTextEditsForwardAndReverse':16,'unifiedPatchRoundTrip':True,
      'supportFilesForwardAndReverse':12,'supportNonoverlappingEditHunks':support_count,
      'sourcePolicySha256':contract['sourcePolicySha256'],'sourceHelperSha256':contract['sourceHelperSha256'],'sourceContractVersion':contract['sourceContractVersion'],
      'correctedWitnessSourceRoot':str(stage),'readOnlyWitnessNativeRowsCompared':342,'unchangedNativePaths':339,'changedNativePaths':3,'addonRowsCompared':2,'declaredNativeAndBuildInputs':344,'externalEmbeddingInputs':3,'toolDependenciesCompared':92,
      'extensionIndexSha256':EXTENSION_INDEX,'extensionFilesRehashed':13,'extensionOriginalInputsRehashed':401,'extensionReviewIndexSha256':EXTENSION_REVIEW,
      'oldProducerIndexSha256':parents[0][1],'oldProducerFilesRehashed':43,'oldProducerOriginalInputsRehashed':666,'oldProducerUnchanged':True,
      'gatesReviewed':['caller index digest before interpreting rows; full source seal before output/fetch and after Ninja before metadata import','explicit SOURCE_ROOT equals containing corrected checkout; original old342 refused; separate absolute original preparation provenance','corrected full342 plus same addon2 and separately authenticated external3; exact source capture before/after','same CMake project hook/add_builtin install order; exact63 Release/layout/OOM flags and final empty-link options','exclusive freezer prechecked copies and preserved original new diagnostic metadata','production selector refusal for classic ON/OFF and finite native9/8 raw declarations','repository53512B adapter live/frozen relation and explicit Node primary/MIT annotation mapping','NULL two diagnostic pins and unreviewed exporter; separate Root digest and containing sourceRoot required before raw preflight loaders','byte-identical parent owned lifecycle;2GiB/800MiB/jobs1; ON frozen before OFF; separate v2 paths'],
      'ownerEvidenceAuthenticatedNotRerun':{'pythonSourceNegativeTinyCopy':77,'nodeSourceNullRefusalDeclarations':22,'bashSyntax':1,'javascriptSyntax':3,'pythonAst':12,'embeddedPythonAst':4},
      'newDiagnosticEngineArtifactsObserved':False,'independentRawOwnerTestExitsObserved':False,'reviewerFailures':document(HERE/'reader-history.json')['readerFailures'],
      'reviewedHelpersImportedOrExecuted':False,'ownerActionOrFixedOutputTestMainsExecuted':False,
      'activeProductionCheckoutReadOnly':True,'configureCompilerNativeGuestTargetHostPreflightFreezerExporterOrTimingExecuted':False,
      'runtimeAcceptanceClaim':False,'measurementClaim':False,
      'limitations':['This approves sealed source design only; no diagnostic native artifact, final component, private-budget behavior, workload correctness, timings or performance advantage is established.',
       'Preparation manifests deliberately retain absolute original context; relocation cannot silently repin historical rows. A copied packet must independently validate its containing corrected checkout.',
       'Positive declaration/command models contain no engine pins and are not build/production admission proof. Future source/action staging and Root artifact authority remain separately required.',
       'New workload, componentizer/tool-root/link seals, actual diagnostic native/freezer review and retained/fresh correctness gates remain future work.']}
    data=(json.dumps({'schemaVersion':1,'files':sorted(checks.values(),key=lambda row:row['path'])},indent=2)+'\n').encode()
    (HERE/'verified-files.json').write_bytes(data);result['verifiedFiles']={'path':'verified-files.json','sha256':digest(data),'bytes':len(data),'count':len(checks)}
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key]for key in ['state','sourceFilesRehashed','sourceInputsRehashed','recipeTextEditsForwardAndReverse','supportFilesForwardAndReverse']}))

if __name__=='__main__':main()

