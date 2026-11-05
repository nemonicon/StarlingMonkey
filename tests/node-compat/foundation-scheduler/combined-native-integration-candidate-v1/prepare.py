"""Prepare unapplied source files only; never import helpers or execute tools."""
import ast,copy,difflib,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
S=HERE.parent;K=S.parent/'foundation-crypto';Z=S.parent/'foundation-zlib'
BASE=K/'ownership-secret-integration-candidate-v1'
FROZEN=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze/source')
SELECTOR=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze/source')
CONTEXT=dict(configuredSourceRoot='/private/tmp/starling-node-compat/combined-native355-v1-source',workRoot='/private/tmp/starling-node-compat/combined-native355-v1-build',freezeRoot='/private/tmp/starling-node-compat/combined-native355-v1-freeze')
seen={};derivations=[]


def row(path):
    p=Path(path).absolute();b=p.read_bytes();r=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
    assert seen.get(str(p),r)==r;seen[str(p)]=r;return r
def load(path):row(path);return json.loads(Path(path).read_bytes())
def write(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n');return p
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def function(text,name):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==name)
    return ''.join(text.splitlines(True)[node.lineno-1:node.end_lineno])+'\n'
def transformed(label,source,edits):
    result=source
    for e in edits:
        n=e.get('count',1);assert result.count(e['before'])==n,(label,e['before'],result.count(e['before']))
        result=result.replace(e['before'],e['after'])
    derivations.append(dict(output=label,edits=edits,sourceBeforeSha256=hashlib.sha256(source.encode()).hexdigest(),sourceAfterSha256=hashlib.sha256(result.encode()).hexdigest()))
    return result
def exact_delta(source,target):
    a=Path(source).read_text();b=Path(target).read_text()
    edits=[dict(beforeOffset=i,afterOffset=k,before=a[i:j],after=b[k:l])for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b).get_opcodes()if tag!='equal']
    forward=a
    for e in reversed(edits):
        i=e['beforeOffset'];assert forward[i:i+len(e['before'])]==e['before'];forward=forward[:i]+e['after']+forward[i+len(e['before']):]
    assert forward==b
    reverse=b
    for e in reversed(edits):
        i=e['afterOffset'];assert reverse[i:i+len(e['after'])]==e['after'];reverse=reverse[:i]+e['before']+reverse[i+len(e['after']):]
    assert reverse==a
    return dict(before=row(source),after=dict(path=str(Path(target).absolute()),sha256=sha(target),bytes=Path(target).stat().st_size),edits=edits,forwardAndInverseByteExact=True)


policy=load(BASE/'policy.json');base_manifest=copy.deepcopy(policy['expectedNativeSourceManifest'])
base_index=row(BASE/'index.json');assert base_index['sha256']=='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108'
audit_index=row(S/'combined-source-convergence-audit-v1/index.json');assert audit_index['sha256']=='84901fd126b21259c0a3acd1729492ad7578c8613440fd9e1af3def0087912cd'
zindex=row(Z/'node-error-semantics-candidate-v1/index.json');zpeer=row(Z/'independent-node-error-semantics-source-review-v1/index.json')
assert zindex['sha256']=='7d620e00e55a0abcbb84fcaa415f406edf436320583c740ac888de3218b9edb5'and zpeer['sha256'].startswith('002458')
payloads={p:SELECTOR/p for p in ('builtins/web/timers.cpp','runtime/event_loop.cpp','host-apis/wasi-0.2.0/host_api.cpp','include/extension-api.h')}
for r in load(Z/'node-error-semantics-candidate-v1/derivations.json')['records']:payloads[r['path']]=Path(r['after']['path'])
assert len(payloads)==7
native=[];changes=[];before={r['path']:r['sha256']for r in base_manifest}
for item in base_manifest:
    relative=item['path'];original=FROZEN/relative;prior=row(original);assert prior['sha256']==item['sha256']
    if relative in payloads:
        source=payloads[relative];r=row(source);p=HERE/'after'/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source.read_bytes())
        target=row(p);changes.append(dict(path=relative,beforeSha256=prior['sha256'],afterSha256=r['sha256'],afterimage=target,reviewedPayload=r))
        native.append(dict(path=relative,original=str(p),sha256=r['sha256'],bytes=r['bytes'],role='EXACT_REVIEWED_SEVEN_FILE_AFTERIMAGE'))
    else:native.append(dict(path=relative,original=str(original),sha256=prior['sha256'],bytes=prior['bytes'],role='UNCHANGED_GENUINE_SECRET355_FROZEN_SOURCE'))
assert len(native)==355 and sum(r['role'].startswith('UNCHANGED')for r in native)==348
current={r['path']:r['sha256']for r in native}
policy['version']='sm-combined355-resource-selector-zlib-errors-source-v1'
policy['strictPolicyVersion']=policy['strictPolicyVersion']+'-combined355-v1'
policy['protectedPolicyVersion']=policy['protectedPolicyVersion']+'-combined355-v1'
policy['expectedNativeSourceManifest']=[dict(path=r['path'],sha256=r['sha256'])for r in native]
for change in changes:
    relative=change['path'];old=policy['sourceLayer'].get(relative)
    policy['sourceLayer'][relative]=dict(beforeSha256=old['beforeSha256']if old else before[relative],afterSha256=change['afterSha256'])
policy['contexts']=CONTEXT
policy['combinedSourcePolicy']=dict(version='sm-combined355-seven-file-source-layer-v1',parentSourceIndex=base_index,parentPolicy=row(BASE/'policy.json'),parentExpectedNativeSourceManifest=base_manifest,sourceFiles=355,unchangedParentFiles=348,changedSourceFiles=7,changes=changes,convergenceAudit=audit_index,fullAbiRebuildRequired=True,publicExportNamesChanged=False,privateBackendEvidenceHookEnabled=False,runtimeValidation=None,operationalAdmission=False)
resource=load(S/'resource-ownership-candidate-v1/derivations.json')
policy['resourceOwnershipSourcePolicy']=dict(version='sm-combined355-resource-owner-source-v1',payloadSourceIndex=row(S/'resource-ownership-candidate-v1/index.json'),parentSourceIndex=base_index,currentNativeSourceFiles=355,changes=resource['files'],timerSourceSha256=current['builtins/web/timers.cpp'],eventLoopCurrentSourceSha256=current['runtime/event_loop.cpp'],nativeRuntimeValidation=None,fullResetOrReuse=False)
task=load(S/'task-selection-candidate-v1/source-contract.json')
policy['taskSelectionSourcePolicy']=dict(version='sm-combined355-optional-task-selection-source-v1',payloadSourceIndex=row(S/'task-selection-candidate-v1/index.json'),parentSourceIndex=base_index,currentNativeSourceFiles=355,changes=task['changes'],nativeReturnContract='std::optional<size_t>; nullopt after invalid-task pruning leaves no work',allNativeDependentsRequireRebuild=True,nativeAllInvalidRuntimeValidation=None,fullResetOrReuse=False)
policy['zlibErrorSemanticsSourcePolicy']=dict(version='sm-combined355-zlib-error-semantics-source-v1',payloadSourceIndex=zindex,payloadSourceReview=zpeer,changes=[r for r in changes if r['path'].startswith('builtins/node-compat/zlib/')or r['path']=='builtins/node-compat/export-manifest.zlib.node-v22.14.0.json'],targetedRecordedRowsPredictedOnly=7,remainingRecordedDifferences=15,remainingDeviationsApproved=False,runtimeValidation=None,runtimeBackendProof=dict(verified=False,version=None,vernum=None))
zmanifest=HERE/'after/builtins/node-compat/export-manifest.zlib.node-v22.14.0.json'
policy['zlibManifestSha256']=sha(zmanifest)
secret_meta=load(FROZEN.parent/'normal-off.engine.wasm.build.json')
policy['expectedComponentizeSourceManifest']=copy.deepcopy(secret_meta['componentizeSourceManifest'])
assert len(policy['expectedComponentizeSourceManifest'])==3
policy['selectedModuleManifests']=copy.deepcopy(secret_meta['selectedModuleManifests'])
next(r for r in policy['selectedModuleManifests']if r['path']==policy['zlibManifest'])['sha256']=sha(zmanifest)
policy['selectedManifestValues']=[load(payloads.get(r['path'],FROZEN/r['path']))for r in policy['selectedModuleManifests']]
policy['admissionModelSha256']=sha(HERE/'native-admission-model.py')
write('policy.json',policy);policy_sha=sha(HERE/'policy.json')
write('native-origins.json',dict(schemaVersion=1,sourceFiles=355,unchangedParentNativeFiles=348,changedNativeFiles=7,originalContext=str(FROZEN),files=native))

# Finite repository tool layout. Old families stay byte-exact DATA at their
# actual repository-relative paths; only the selected top-level recipe changes.
tools={r['path']:copy.deepcopy(r)for r in load(BASE/'tool-origins.json')['files']if r['path']not in current and r['path']!='tests/node-compat/build-engine.sh'}
families=[BASE,S/'combined-source-convergence-audit-v1',S/'resource-ownership-candidate-v1',S/'task-selection-candidate-v1',S/'task-selection-integration-candidate-v1',Z/'node-error-semantics-candidate-v1',Z/'independent-node-error-semantics-source-review-v1']
for family in families:
    idx=load(family/'index.json')
    for relative in ['index.json']+[r['path']for r in idx['files']]:
        p=family/relative;r=row(p);name=str(p.relative_to(REPO));entry=dict(path=name,original=str(p),sha256=r['sha256'],bytes=r['bytes'])
        assert name not in tools or tools[name]['sha256']==r['sha256'];tools[name]=entry
for r in tools.values():
    got=row(r['original']);assert got['sha256']==r['sha256']and got['bytes']==r['bytes']
auth=[dict(path=r['path'],sha256=r['sha256'],bytes=r['bytes'])for r in sorted(tools.values(),key=lambda r:r['path'])]
write('donor-inputs.json',dict(schemaVersion=1,role='EXPLICIT_STAGE_REPOSITORY_LAYOUT_ANCESTRY_AND_GENERIC_CODE_INPUTS',files=auth,originalPreparationRowsNotRebased=True))
auth_sha=sha(HERE/'donor-inputs.json')

old_helper=(BASE/'layer-policy.py').read_text();row(BASE/'layer-policy.py')
old_layout=(S/'integration-candidate-v1/layer-policy.py').read_text();row(S/'integration-candidate-v1/layer-policy.py')
selector_helper=(S/'task-selection-integration-candidate-v1/layer-policy.py').read_text();row(S/'task-selection-integration-candidate-v1/layer-policy.py')
layout=function(old_layout,'validate_compilation').replace('def validate_compilation(','def validate_layout_compilation(',1)
generic='\n'.join([function(old_helper,'_macro'),function(old_helper,'_release'),layout,function(selector_helper,'task_selection_commands')])
compile_source=function(old_helper,'validate_classic_compilation')
start=compile_source.index("    codec_file=HERE.parents[1]")
end=compile_source.index("    selected=metadata['zlibSelectedCodecInput']",start)
compile_source=transformed('validate_classic_compilation',compile_source,[
    dict(before=compile_source[start:end],after='    validate_sources(repo)\n    codec=load_codec()\n'),
    dict(before='PARENT.validate_compilation(',after='validate_layout_compilation(')])
decorator=function(old_helper,'decorate')
decorator=transformed('decorate',decorator,[
    dict(before='Only initial normal-OFF secret source producer is implemented',after='Only initial normal-OFF combined355 producer is implemented'),
    dict(before='PARENT.POLICY',after='ANCESTOR',count=5),
    dict(before='PARENT_POLICY_SHA256',after="POLICY['parentPolicySha256']"),
    dict(before='PARENT_HELPER_SHA256',after="POLICY['parentHelperSha256']"),
    dict(before="str(PARENT_ROOT.parent/'taskqueue-owner-v2/componentize-taskqueue-ticks.UNAPPLIED.patch')",after="str(ANCESTOR_ROOT.parent/'taskqueue-owner-v2/componentize-taskqueue-ticks.UNAPPLIED.patch')"),
    dict(before='    return metadata\n',after='    # @COMBINED_METADATA@\n    return metadata\n')])
combined='''    assert Path(repo).resolve()==Path(POLICY['contexts']['configuredSourceRoot'])
    database=list(entries)
    assert len(database)==len({r['file']for r in database})==68
    source_prefix=str(Path(repo))+'/'
    generated=[r['command']for r in database if r['file']==str(cache.parent/'starling-raw.wasm/null.cpp')]
    other=[r['command']for r in database if r['file'].startswith(source_prefix)and not r['file'].startswith((source_prefix+'builtins/',source_prefix+'runtime/'))]
    assert len(native)==62 and len(other)==5 and len(generated)==1 and len(private)==6
    assert values['ENABLE_BUILTIN_WEB_TIMERS']=='ON'
    assert install_text.count('NS_DEF(builtins::web::timers)')==1
    commands={r['file']:r['command']for r in database}
    assert str(Path(repo)/'host-apis/wasi-0.2.0/host_api.cpp')in commands
    selection_commands=task_selection_commands(database,repo,metadata)
    metadata['resourceOwnershipPolicy']={'sourcePolicy':copy.deepcopy(POLICY['resourceOwnershipSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'timerInstallation':{'path':str(install),'sha256':digest(install),'webTimersEnabled':'ON'},'nativeRuntimeValidation':None,'fullResetOrReuse':False}
    metadata['taskSelectionPolicy']={'sourcePolicy':copy.deepcopy(POLICY['taskSelectionSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'actualHostApiCompileCommands':[selection_commands['host-apis/wasi-0.2.0/host_api.cpp']],'actualEventLoopCompileCommands':[selection_commands['runtime/event_loop.cpp']],'allNativeDependentsRequireRebuild':True,'nativeAllInvalidRuntimeValidation':None,'fullResetOrReuse':False}
    metadata['zlibErrorSemanticsPolicy']={'sourcePolicy':copy.deepcopy(POLICY['zlibErrorSemanticsSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'remainingRecordedDifferences':15,'remainingDeviationsApproved':False,'runtimeValidation':None}
    manifest_values=[json.loads((Path(repo)/r['path']).read_bytes())for r in metadata['selectedModuleManifests']]
    assert metadata['selectedModuleManifests']==POLICY['selectedModuleManifests']and manifest_values==POLICY['selectedManifestValues']
    artifact_name=Path(metadata['enginePath']).name.removesuffix('.wasm')
    fresh_path=Path(POLICY['contexts']['workRoot'])/('fresh-abi-'+artifact_name+'.json')
    fresh=json.loads(fresh_path.read_bytes())
    assert fresh['state']=='ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'
    assert fresh['configuredSourceRoot']==str(Path(repo))and fresh['workRoot']==POLICY['contexts']['workRoot']
    assert fresh['sourceDirExisted']is fresh['buildDirExisted']is fresh['artifactExisted']is False
    assert fresh['sourceDir']==str(Path(source_dir))and fresh['buildDir']==str(cache.parent)and fresh['artifact']==metadata['enginePath']
    for key in('CMAKE_C_COMPILER_LAUNCHER','CMAKE_CXX_COMPILER_LAUNCHER'):assert values[key]==''
    for command in metadata['generatedRustProject']['actualCargoBuildCommands']:
        words=shlex.split(command);assert words.count('--target-dir')==1
        assert Path(words[words.index('--target-dir')+1]).resolve()==(cache.parent/'cargo/build').resolve()
        assert '--locked'in words
    assert fresh['compilerLauncherReuseAllowed']is False and fresh['rustIncrementalReuseAllowed']is False
    metadata['combinedNativeSourcePolicy']={'sourcePolicy':copy.deepcopy(POLICY['combinedSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'configuredSourceRoot':str(Path(repo)),'workRoot':POLICY['contexts']['workRoot'],'externalConfiguredSourceRoot':str(Path(source_dir)),'selectedManifests':manifest_values,'sourceManifestCheckedBeforeAndAfterBuild':metadata['sourceInputsCapturedBeforeBuild']and metadata['buildRecipeCheckedBeforeAndAfterBuild'],'actualCompileDatabaseRows':68,'actualPolicyCppCompileCommands':native,'actualOtherConfiguredCompileCommands':other,'actualGeneratedNullCompileCommands':generated,'actualSeparateEmbeddingCompileCommands':embedding_commands,'freshAbiEvidence':fresh,'freshAbiEvidenceFile':{'path':str(fresh_path),'sha256':digest(fresh_path)},'privateBackendEvidenceHookEnabled':False,'runtimeValidation':None,'operationalAdmission':False}
    authenticate_inputs()
'''
decorator=decorator.replace('    # @COMBINED_METADATA@\n',combined)
template=(HERE/'helper-prefix.template.py').read_text()
helper=template.replace('@POLICY_SHA@',policy_sha).replace('@AUTH_SHA@',auth_sha).replace('# @GENERIC_FUNCTIONS@',generic).replace('# @COMPILE_FUNCTION@',compile_source).replace('# @DECORATE_FUNCTION@',decorator)
(HERE/'layer-policy.py').write_text(helper);helper_sha=sha(HERE/'layer-policy.py')

old_recipe=(BASE/'proposed/tests/node-compat/build-engine.sh').read_text();row(BASE/'proposed/tests/node-compat/build-engine.sh')
recipe=transformed('proposed/tests/node-compat/build-engine.sh',old_recipe,[
    dict(before='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-build',after=CONTEXT['workRoot'],count=2),
    dict(before='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source',after=CONTEXT['configuredSourceRoot']),
    dict(before='tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1',after='tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1',count=3),
    dict(before='secretfailure-v1.',after='combined355-v1.',count=2),
    dict(before='e82d9ce3794735a391d3e9e689c35ef4417e74ef497a81f0d26851c43d1b45bb',after=helper_sha,count=5),
    dict(before='cb35fec0a5628110a046cef0a51ffed058ffd31b2a732d94711fabda08b4a612',after=policy_sha,count=2),
    dict(before='Exact separate configured secret source root required',after='Exact separate configured combined355 source root required'),
    dict(before='Exact separate secret work root required',after='Exact separate combined355 work root required'),
    dict(before='Only initial ordinary Release normal-OFF is implemented in this source candidate',after='Only initial ordinary Release combined355 normal-OFF is implemented'),
    dict(before='# Authenticate actual corrected342 sources before any archive fetch.',after='# Authenticate actual combined355 sources before any archive fetch.'),
    dict(before='cmake -S "$source_dir" -B "$build_dir" -G Ninja \\\n',after='cmake -S "$source_dir" -B "$build_dir" -G Ninja \\\n  -DCMAKE_C_COMPILER_LAUNCHER= -DCMAKE_CXX_COMPILER_LAUNCHER= -DENABLE_BUILTIN_WEB_TIMERS=ON -DENABLE_BUILTIN_WEB_CRYPTO=ON \\\n'),
    dict(before="    'ENABLE_BUILTIN_WEB_TEXT_CODEC': 'ON',",after="    'ENABLE_BUILTIN_WEB_TEXT_CODEC': 'ON', 'ENABLE_BUILTIN_WEB_TIMERS':'ON', 'ENABLE_BUILTIN_WEB_CRYPTO':'ON',\n    'CMAKE_C_COMPILER_LAUNCHER':'', 'CMAKE_CXX_COMPILER_LAUNCHER':'',")])
fresh='''# Initial complete355 build only: no old configured tree, build cache or object reuse.
[[ ! -e "$source_dir" && ! -L "$source_dir" && ! -e "$build_dir" && ! -L "$build_dir" && ! -e "$artifact" && ! -e "$artifact.build.json" ]] || { echo 'Fresh combined355 ABI source/build/artifact paths required' >&2; exit 1; }
for required in "$path_enabled" "$events_enabled" "$string_decoder_enabled" "$assert_enabled" "$querystring_enabled" "$util_enabled" "$stream_web_enabled" "$ticks_enabled" "$classic_enabled" "$zlib_enabled" "$consumers_enabled"; do [[ "$required" == 1 ]] || { echo 'Initial combined355 requires all eleven native selections' >&2; exit 1; }; done
for reuse_variable in RUSTC_WRAPPER RUSTC_WORKSPACE_WRAPPER CARGO_BUILD_RUSTC_WRAPPER CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER CARGO_TARGET_DIR CARGO_BUILD_TARGET_DIR; do
  [[ -z "${!reuse_variable-}" ]] || { echo 'Inherited compiler-cache or Cargo target override is outside the fresh ABI build contract' >&2; exit 1; }
done
export CCACHE_DISABLE=1 SCCACHE_DISABLE=1 CARGO_INCREMENTAL=0
python3 - "$repo_root" "$work_root" "$source_dir" "$build_dir" "$artifact" "$work_root/fresh-abi-$artifact_name.json" <<'PYFRESH'
import json,os,sys
repo,work,source,build,artifact,target=sys.argv[1:]
record=dict(state='ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1',configuredSourceRoot=repo,workRoot=work,sourceDir=source,buildDir=build,artifact=artifact,sourceDirExisted=os.path.lexists(source),buildDirExisted=os.path.lexists(build),artifactExisted=os.path.lexists(artifact),compilerLauncherReuseAllowed=False,rustIncrementalReuseAllowed=False)
assert record['sourceDirExisted']is record['buildDirExisted']is record['artifactExisted']is False
with open(target,'x')as f:json.dump(record,f,indent=2);f.write('\\n')
PYFRESH
'''
anchor='artifact="$work_root/artifacts/$artifact_name.wasm"\n';assert recipe.count(anchor)==1;recipe=recipe.replace(anchor,anchor+fresh)
model_call='''# New355-only raw metadata shape gate, after genuine codec witness and before publication.
model_file=layer_file.parent/'native-admission-model.py'
assert digest(model_file)==layer.POLICY['admissionModelSha256']
model_spec=importlib.util.spec_from_file_location('actual_combined355_metadata_shape',model_file)
model=importlib.util.module_from_spec(model_spec);model_spec.loader.exec_module(model)
classification=model.validate_metadata(metadata,layer.POLICY,layer.POLICY_SHA256,digest(layer_file),digest(pathlib.Path(repo)/'tests/node-compat/build-engine.sh'),componentize_inputs,'normal-off')
assert classification==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
'''
anchor="with open(artifact + '.build.json', 'x') as output:\n";assert recipe.count(anchor)==1;recipe=recipe.replace(anchor,model_call+anchor)
p=HERE/'proposed/tests/node-compat/build-engine.sh';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(recipe)
tools['tests/node-compat/build-engine.sh']=dict(path='tests/node-compat/build-engine.sh',original=str(p),sha256=sha(p),bytes=p.stat().st_size)
write('tool-origins.json',dict(schemaVersion=1,state='FINITE_COMBINED355_SOURCE_BUILD_TOOLS_NO_ACTION',files=sorted(tools.values(),key=lambda r:r['path']),ownSealedFamilyRowsAddedAfterSeal=True,activeFreezer=None,exporter=None,bootstrap=None))
write('stage-input-plan.json',dict(schemaVersion=1,state='SOURCE_ONLY_FINITE_INPUT_PLAN_NOT_STAGE_IMPLEMENTATION',destination=CONTEXT['configuredSourceRoot'],nativeSourceFiles=355,toolRows=len(tools),files=native+list(tools.values()),ownSealedFamilyAddedSeparately=True,stageExecuted=False))
write('derivations.json',dict(schemaVersion=1,scope='Source-only real355 producer derivations; no old metadata transformed',textDerivations=derivations,genericLayoutDonor=row(S/'integration-candidate-v1/layer-policy.py'),compileAndDecoratorDonor=row(BASE/'layer-policy.py'),newSourcePolicyParent=row(BASE/'policy.json'),changedFiles=changes,privateBackendHookIncluded=False))
write('exact-derivations.json',dict(schemaVersion=1,role='FULL_SOURCE_TOOLING_FORWARD_AND_INVERSE_BYTE_PROOFS',files=[exact_delta(BASE/'policy.json',HERE/'policy.json'),exact_delta(BASE/'layer-policy.py',HERE/'layer-policy.py'),exact_delta(BASE/'proposed/tests/node-compat/build-engine.sh',p)],nativePayloads=[dict(path=r['path'],before=row(FROZEN/r['path']),after=r['afterimage'],reviewedPayload=r['reviewedPayload'])for r in changes],newFiles=['native-admission-model.py','helper-prefix.template.py'],noOldMetadataTransformed=True))
write('input-hashes.json',dict(schemaVersion=1,files=sorted(seen.values(),key=lambda r:r['path']),noOwnerHelpersImportedOrExecuted=True))
write('future-authority.json',dict(schemaVersion=1,state='UNISSUED_COMBINED355_SOURCE_ONLY',contexts=CONTEXT,sourcePeer=None,rootAuthority=None,stage=None,build=None,freeze=None,export=None,reviewedPins=None,bootstrap=None,component=None,runtime=None,operationalAdmission=False))
print(json.dumps(dict(state='COMBINED355_SOURCE_PREPARED_UNSEALED',native355=355,retained348=348,changes7=7,donorRows=len(auth),toolRows=len(tools),inputRows=len(seen),helperSha256=helper_sha,policySha256=policy_sha,recipeSha256=sha(p),noHelpersOrRuntimeExecuted=True)))
