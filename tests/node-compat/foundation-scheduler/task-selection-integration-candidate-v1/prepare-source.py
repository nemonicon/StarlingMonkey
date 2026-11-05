"""Read/hash and write this proposal only. Never import an owner helper or run a build."""
from pathlib import Path
import copy
import difflib
import hashlib
import json

OWN = Path(__file__).resolve().parent
REPO = OWN.parents[3]
SCHED = OWN.parent
PARENT = SCHED / 'resource-integration-candidate-v1'
FIX = SCHED / 'task-selection-candidate-v1'
PEER = SCHED / 'independent-task-selection-source-review-v1'
FROZEN = Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze')
SOURCE = '/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source'
WORK = '/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build'
FREEZE = '/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze'
inputs = {}
assert REPO == Path('/Users/dan/dev/StarlingMonkey')
assert OWN == REPO/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'
assert not (OWN/'index.json').exists(), 'Sealed source preparation is immutable'

def desc(path):
    p = Path(path)
    assert p.is_absolute() and not p.is_symlink() and p.is_file(), p
    before = p.stat()
    raw = p.read_bytes()
    after = p.stat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns) == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))

def capture(row):
    assert desc(row['path']) == row, row['path']
    prior = inputs.setdefault(row['path'], row)
    assert prior == row
    return row

def family(root, expected):
    index = capture(desc(root / 'index.json'))
    assert index['sha256'] == expected
    value = json.loads((root/'index.json').read_bytes())
    rows = [index]
    for row in value['files']:
        assert row['path'] and not row['path'].startswith('/') and all(p not in ('','.','..') for p in row['path'].split('/'))
        rows.append(capture(dict(row,path=str(root/row['path']))))
    assert len({r['path'] for r in rows}) == len(rows)
    assert {str(p) for p in root.rglob('*') if p.is_file()} == {r['path'] for r in rows}
    assert not any(p.is_symlink() for p in root.rglob('*'))
    return dict(index=index, rows=rows)

def write(name, value):
    p = OWN/name
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, (dict,list)):
        value = json.dumps(value,indent=2)+'\n'
    p.write_text(value)

def derive(donor, edits, target):
    original = Path(donor).read_text()
    text = original
    recorded = []
    for before, after in edits:
        count = text.count(before)
        assert count > 0 and before != after, (target,before[:100])
        text = text.replace(before,after)
        recorded.append(dict(before=before,after=after,count=count))
    reverse = text
    for edit in reversed(recorded):
        assert reverse.count(edit['after']) == edit['count'], target
        reverse = reverse.replace(edit['after'],edit['before'])
    assert reverse == original
    write(target,text)
    return dict(donor=capture(desc(donor)),afterimage=target,edits=recorded)

families = {
    'resourceIntegration': family(PARENT,'20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'),
    'taskSelection': family(FIX,'d41686ae9e4cf9e7a4b76d60994065ca7f417a2d49b1940803cd996243ecfffb'),
    'taskSelectionSourcePeer': family(PEER,'f0a9144156ddd49be291c8e65227777391fc4568d848c8da9d74ecf612ff503a'),
}
peer = json.loads((PEER/'results.json').read_bytes())
assert peer['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION_SOURCE_REVIEW_PASSED_V1'
assert peer['sourceIndexSha256']==families['taskSelection']['index']['sha256']
assert peer['sourceOnly'] is True and peer['sourceReviewPassed'] is True and peer['ownerActionsInvoked'] is False
old = json.loads((PARENT/'policy.json').read_bytes())
contract = json.loads((FIX/'source-contract.json').read_bytes())
before = {r['path']:r['sha256'] for r in old['expectedNativeSourceManifest']}
assert len(before)==342
changes = contract['changes']
assert len(changes)==3 and {c['path'] for c in changes}=={'include/extension-api.h','host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'}
for change in changes:
    assert before[change['path']]==change['before']['sha256']
    capture(change['original']); capture(change['before']); capture(change['after'])
    assert Path(change['original']['path']).read_bytes()==Path(change['before']['path']).read_bytes()
    write('native/'+change['path'],Path(change['after']['path']).read_text())

policy = copy.deepcopy(old)
policy['version'] = 'sm-private-ticks-classic-resource-task-selection-source-v1'
new = {c['path']:c['after']['sha256'] for c in changes}
for row in policy['expectedNativeSourceManifest']:
    row['sha256']=new.get(row['path'],row['sha256'])
for change in changes:
    name = change['path']
    if name in policy['sourceLayer']:
        policy['sourceLayer'][name]['afterSha256']=new[name]
    else:
        policy['sourceLayer'][name]=dict(beforeSha256=before[name],afterSha256=new[name])
selection = dict(
    version='sm-optional-task-selection-source-v1',
    parentIntegrationIndexSha256=families['resourceIntegration']['index']['sha256'],
    parentPolicySha256=desc(PARENT/'policy.json')['sha256'],
    parentHelperSha256=desc(PARENT/'layer-policy.py')['sha256'],
    parentRecipeSha256=desc(PARENT/'proposed/tests/node-compat/build-engine.sh')['sha256'],
    sourceCandidateIndexSha256=families['taskSelection']['index']['sha256'],
    sourceReviewIndexSha256=families['taskSelectionSourcePeer']['index']['sha256'],
    nativeFiles=342,unchangedResourceParentFiles=339,
    changes=[dict(path=c['path'],beforeSha256=c['before']['sha256'],afterSha256=c['after']['sha256'],bytes=c['after']['bytes']) for c in changes],
    timerOwnershipSourceSha256=before['builtins/web/timers.cpp'],
    nativeReturnContract='std::optional<size_t>; nullopt after pruning all invalid tasks; engaged zero is valid',
    requiresFullNativeRebuild=True,compatibleWithParentEngineAbi=False,
    hostCapabilityChange=False,publicModuleSurfaceChange=False,nativeAllInvalidRuntimeValidation=None,
    interestAccountingChanged=False,fullResetOrReuse=False)
policy['taskSelectionSourcePolicy']=selection
write('policy.json',policy)
policy_sha = desc(OWN/'policy.json')['sha256']

# Retain real parent306 expected/compilation calls. Do not import or adapt an
# old342 validator/decorator to new source bytes.
helper = (PARENT/'layer-policy.py').read_text()
start = helper.index('def verify_resource_ancestry():')
end = helper.index('\nPARENT_ROOT=',start)
old_ancestry = helper[start:end]
new_ancestry = '''def checked_family(root, expected_index_sha256):
    assert digest(root/'index.json')==expected_index_sha256
    index=json.loads((root/'index.json').read_bytes());names=set()
    for row in index['files']:
        name=row['path'];assert name and not name.startswith('/') and all(p not in('','.','..')for p in name.split('/'))and name not in names;names.add(name)
        path=root/name;assert path.is_file()and not path.is_symlink()and path.stat().st_size==row['bytes']and digest(path)==row['sha256']
    assert not any(p.is_symlink()for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names|{'index.json'}
    return index
def verify_task_selection_ancestry():
    source=POLICY['taskSelectionSourcePolicy'];previous=HERE.parent/'resource-integration-candidate-v1'
    checked_family(previous,source['parentIntegrationIndexSha256'])
    assert digest(previous/'policy.json')==source['parentPolicySha256']
    assert digest(previous/'layer-policy.py')==source['parentHelperSha256']
    assert digest(previous/'proposed/tests/node-compat/build-engine.sh')==source['parentRecipeSha256']
    old=json.loads((previous/'policy.json').read_bytes())
    before={r['path']:r['sha256']for r in old['expectedNativeSourceManifest']}
    after={r['path']:r['sha256']for r in POLICY['expectedNativeSourceManifest']}
    assert len(before)==len(after)==342 and set(before)==set(after)
    assert sum(before[p]==after[p]for p in before)==339
    assert {r['path']for r in source['changes']}=={'include/extension-api.h','host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'}
    for r in source['changes']:assert before[r['path']]==r['beforeSha256']and after[r['path']]==r['afterSha256']
    assert before['builtins/web/timers.cpp']==after['builtins/web/timers.cpp']==source['timerOwnershipSourceSha256']
    for field in('resourceOwnershipSourcePolicy','classicTraceSourcePolicy','embedding','nativePatchSha256','strictPolicyVersion','protectedPolicyVersion','classicPolicyVersion','profileVersion'):
        assert POLICY[field]==old[field]
    proposal=HERE.parent/'task-selection-candidate-v1';checked_family(proposal,source['sourceCandidateIndexSha256'])
    contract=json.loads((proposal/'source-contract.json').read_bytes())
    assert [{k:r[k]for k in('path','beforeSha256','afterSha256','bytes')}for r in source['changes']]==[dict(path=r['path'],beforeSha256=r['before']['sha256'],afterSha256=r['after']['sha256'],bytes=r['after']['bytes'])for r in contract['changes']]
    peer=HERE.parent/'independent-task-selection-source-review-v1';checked_family(peer,source['sourceReviewIndexSha256'])
    reviewed=json.loads((peer/'results.json').read_bytes())
    assert reviewed['state']=='INDEPENDENT_SCHEDULER_TASK_SELECTION_SOURCE_REVIEW_PASSED_V1'and reviewed['sourceIndexSha256']==source['sourceCandidateIndexSha256']and reviewed['sourceOnly']is True and reviewed['sourceReviewPassed']is True and reviewed['ownerActionsInvoked']is False
    return True
verify_task_selection_ancestry()'''
host_function = '''def task_selection_commands(entries,repo,metadata):
    repo=Path(repo);paths=['host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'];found={}
    for name in paths:
        rows=[row for row in entries if row['file']==str(repo/name)]
        assert len(rows)==1,'Exactly one actual selector implementation/caller command required: '+name
        words=shlex.split(rows[0]['command']);assert words.count('-c')==1 and words[words.index('-c')+1]==str(repo/name)and '-fsyntax-only'not in words
        _release(words);_macro(words,'NODE_COMPAT_ENTROPY_POLICY',True)
        _macro(words,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',metadata['entropyPolicy']=='runtime-only')
        if name.startswith('host-apis/'):
            for macro in('NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_CLASSIC_STREAMS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_GC_STRESS'):_macro(words,macro,False)
        found[name]=rows[0]['command']
    return found
'''
insert = "    metadata['taskSelectionPolicy']={'sourcePolicy':copy.deepcopy(POLICY['taskSelectionSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'actualHostApiCompileCommands':[selection_commands['host-apis/wasi-0.2.0/host_api.cpp']],'actualEventLoopCompileCommands':[selection_commands['runtime/event_loop.cpp']],'allNativeDependentsRequireRebuild':True,'nativeAllInvalidRuntimeValidation':None,'fullResetOrReuse':False}\n"
helper_derivation = derive(PARENT/'layer-policy.py',[
    ("POLICY_SHA256='"+selection['parentPolicySha256']+"'","POLICY_SHA256='"+policy_sha+"'"),
    (old_ancestry,new_ancestry),
    ('def decorate(metadata,repo,source_dir,entries,embedding_commands,enabled):',host_function+'def decorate(metadata,repo,source_dir,entries,embedding_commands,enabled):'),
    ('    native,queue,private=validate_classic_compilation(entries,embedding_commands,repo,metadata)','    native,queue,private=validate_classic_compilation(entries,embedding_commands,repo,metadata)\n    selection_commands=task_selection_commands(entries,repo,metadata)'),
    ("    metadata['classicStreamsPolicy']={",insert+"    metadata['classicStreamsPolicy']={"),
], 'layer-policy.py')
helper_sha = desc(OWN/'layer-policy.py')['sha256']
old_recipe = PARENT/'proposed/tests/node-compat/build-engine.sh'
recipe_derivation = derive(old_recipe,[
    ('/private/tmp/starling-node-compat/scheduler-resource-v1-build',WORK),
    ('tests/node-compat/foundation-scheduler/resource-integration-candidate-v1','tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'),
    (selection['parentHelperSha256'],helper_sha),
    (selection['parentPolicySha256'],policy_sha),
    ('resource-v1.$entropy_mode','resource-selection-v1.$entropy_mode'),
    ('Resource source candidate requires one build job','Resource task-selection candidate requires one build job'),
    ('layer_root="$repo_root/tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1"',
     '[[ "$repo_root" == '+SOURCE+' && "$work_root" == '+WORK+' ]] || { echo "Task-selection source/work context mismatch" >&2; exit 1; }\n'+
     '[[ "$stress" == 0 && "$entropy_mode" == OFF ]] || { echo "This integration source cut selects normal-OFF only" >&2; exit 1; }\n'+
     'for selected in "$path_enabled" "$events_enabled" "$string_decoder_enabled" "$assert_enabled" "$querystring_enabled" "$util_enabled" "$stream_web_enabled" "$ticks_enabled" "$classic_enabled"; do\n'+
     '  [[ "$selected" == 1 ]] || { echo "Task-selection source cut requires the complete342 profile" >&2; exit 1; }\n'+
     'done\nlayer_root="$repo_root/tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1"'),
], 'proposed/tests/node-compat/build-engine.sh')
model_donor = PARENT/'native-admission-model.py'
model_derivation = derive(model_donor,[
    ("assert variant in ('normal-off', 'gc-off')","assert variant == 'normal-off'"),
    ("    # Actual independent native/freezer proof still must verify each captured", "    selected = metadata['taskSelectionPolicy']\n    assert selected['sourcePolicy'] == policy['taskSelectionSourcePolicy']\n    assert selected['policyFileSha256'] == policy_sha256 and selected['helperSha256'] == helper_sha256\n    assert selected['allNativeDependentsRequireRebuild'] is True and selected['nativeAllInvalidRuntimeValidation'] is None and selected['fullResetOrReuse'] is False\n    for field in ('actualHostApiCompileCommands','actualEventLoopCompileCommands'):\n        assert type(selected[field]) is list and len(selected[field]) == 1 and type(selected[field][0]) is str\n    # Actual independent native/freezer proof still must verify each captured"),
    ('FINITE_RESOURCE342_METADATA_SHAPE_ONLY','FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY'),
], 'native-admission-model.py')
stage_derivation = derive(PARENT/'stage.py',[
    ('Dormant exact accepted342 reconstruction and two-source overlay','Dormant resource342 reconstruction and three-source task-selection overlay'),
    ('scheduler-resource-v1-source','scheduler-resource-selection-v1-source'),
    ('scheduler-resource-v1-stage.json','scheduler-resource-selection-v1-stage.json'),
    ('tests/node-compat/foundation-scheduler/resource-integration-candidate-v1','tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'),
    ('ROOT_REVIEWED_SCHEDULER_RESOURCE342_SOURCE_STAGE_V1','ROOT_REVIEWED_SCHEDULER_RESOURCE_TASK_SELECTION342_SOURCE_STAGE_V1'),
    ('INDEPENDENT_SCHEDULER_RESOURCE_INTEGRATION_SOURCE_REVIEW_PASSED_V1','INDEPENDENT_SCHEDULER_TASK_SELECTION_INTEGRATION_SOURCE_REVIEW_PASSED_V1'),
    (" captured=[config_descriptor,config['rootAuthority'],*own,*peers]", " captured=[config_descriptor,config['rootAuthority'],*own,*peers]\n preparation=read(next(r for r in own if r['path']==str(OWN/'input-freeze.json')))\n for d in preparation['files']:checked(d);captured.append(d)\n assert root['workRoot']=='"+WORK+"'and root['freezeRoot']=='"+FREEZE+"'\n assert not Path(root['workRoot']).exists()and not Path(root['freezeRoot']).exists()"),
    (" assert not DEST.exists()and not DEST.is_symlink()and not JOURNAL.exists()and not JOURNAL.is_symlink()", " assert plan['sourceRoot']==str(DEST)and plan['workRoot']==root['workRoot']and plan['freezeRoot']==root['freezeRoot']and plan['nativeCount']==342\n assert not DEST.exists()and not DEST.is_symlink()and not JOURNAL.exists()and not JOURNAL.is_symlink()"),
    ("state='RESOURCE342_SOURCE_STAGED_UNREVIEWED_V1'","state='RESOURCE_TASK_SELECTION342_SOURCE_STAGED_UNREVIEWED_V1'"),
    ('nativeReplacements=2,copies=copied','nativeReplacements=3,workRoot=root[\'workRoot\'],freezeRoot=root[\'freezeRoot\'],copies=copied'),
], 'stage.py')
write('derivations.json',dict(schemaVersion=1,helper=helper_derivation,recipe=recipe_derivation,model=model_derivation,stage=stage_derivation,nativeChanges=selection['changes'],nativeSourceEdits=sum(len(c['edits'])for c in changes),boundaryTagsPreserved=True))
patch=[]
for change in changes:
    name=change['path']
    patch.extend(difflib.unified_diff(Path(change['before']['path']).read_text().splitlines(True),Path(change['after']['path']).read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
write('task-selection-integration.UNAPPLIED.patch',''.join(patch))

# Finite stage inventory: real resource342 inputs, inherited build dependencies,
# then explicitly indexed ancestry at their real repository-relative contexts.
parent_plan = json.loads((PARENT/'stage-inputs.json').read_bytes())
stage = {}
native_inputs=[]
for row in policy['expectedNativeSourceManifest']:
    name=row['path']; physical=OWN/'native'/name if name in new else FROZEN/'source'/name
    d=desc(physical);assert d['sha256']==row['sha256']
    if name not in new:capture(d)
    native_inputs.append(dict(path=name,source=d,role='new-selector-afterimage'if name in new else'unchanged-resource-frozen-source'))
    stage[name]=dict(target=name,original=d,role='native342')
for row in parent_plan['files']:
    if row['role']=='accepted342-native':continue
    capture(row['original']);stage[row['target']]=row
for label,fam in families.items():
    for d in fam['rows']:
        name=str(Path(d['path']).relative_to(REPO))
        stage[name]=dict(target=name,original=d,role='indexed-'+label)
stage['tests/node-compat/build-engine.sh']=dict(target='tests/node-compat/build-engine.sh',original=desc(OWN/'proposed/tests/node-compat/build-engine.sh'),role='new-build-recipe')
write('native-inputs.json',dict(schemaVersion=1,sourceFiles=342,resourceParentFilesUnchanged=339,rows=native_inputs))
write('stage-inputs.json',dict(schemaVersion=1,baseline='54b3329b3ce818fd1f244e871e9c259b63667cda',sourceRoot=SOURCE,workRoot=WORK,freezeRoot=FREEZE,nativeCount=342,unchangedResourceParentFiles=339,nativeAfterimageReplacements=selection['changes'],files=sorted(stage.values(),key=lambda r:r['target']),proposalRelativeRoot=str(OWN.relative_to(REPO)),actualStageExecuted=False))

metadata=FROZEN/'normal-off.engine.wasm.build.json'
receipt=FROZEN/'normal-off-freeze-receipt.json'
review=SCHED/'independent-resource-normal-off-frozen-artifact-review-v1'
baseline=dict(schemaVersion=1,families={k:v['index']for k,v in families.items()},parentPolicy=capture(desc(PARENT/'policy.json')),parentHelper=capture(desc(PARENT/'layer-policy.py')),parentRecipe=capture(desc(old_recipe)),resourceMetadata=capture(desc(metadata)),resourceFreezeReceipt=capture(desc(receipt)),resourceFrozenReviewIndex=capture(desc(review/'index.json')),externalEmbeddingSources=json.loads(metadata.read_bytes())['componentizeSourceManifest'],parentConfiguredRoot='/private/tmp/starling-node-compat/scheduler-resource-v1-source',parentWorkRoot='/private/tmp/starling-node-compat/scheduler-resource-v1-build',parentFreezeRoot=str(FROZEN))
for r in baseline['externalEmbeddingSources']:
    capture(desc(FROZEN/'componentize-source'/r['path']))
write('baseline-pins.json',baseline)

# Exact source evidence only, not a complete packaging or native-tool closure.
evidence_paths=['CMakeLists.txt','cmake/build-crates.cmake','cmake/builtins.cmake','cmake/add_builtin.cmake','host-apis/wasi-0.2.10/host_api.cmake','runtime/crates/staticlib-template/Cargo.lock','crates/rust-hooks/src/lib.rs','crates/rust-hooks/src/wrappers.cpp','runtime/event_loop.cpp','include/extension-api.h','host-apis/wasi-0.2.0/host_api.cpp','builtins/web/timers.cpp']
api=[]
for name in evidence_paths:
    p=FROZEN/'source'/name;d=capture(desc(p));lines=p.read_text().splitlines()
    needles={'CMakeLists.txt':['add_library(extension_api','runtime/event_loop.cpp','target_link_libraries(starling-raw.wasm'],
    'cmake/build-crates.cmake':['corrosion_import_crate','add_rust_lib(rust-hooks','add_rust_lib(rust-url'],
    'host-apis/wasi-0.2.10/host_api.cmake':['add_library(host_api','${WASI_0_2_0}/host_api.cpp'],
    'runtime/event_loop.cpp':['api::AsyncTask::select','interest_complete()','tasks_size == 0'],
    'include/extension-api.h':['static size_t select'],
    'host-apis/wasi-0.2.0/host_api.cpp':['size_t api::AsyncTask::select'],
    'builtins/web/timers.cpp':['REQUEST_HANDLER_ONLY','class TimerTask']}.get(name,[])
    api.append(dict(relativePath=name,descriptor=d,lines=[dict(line=i+1,text=line)for i,line in enumerate(lines)if any(n in line for n in needles)]))
write('source-evidence.json',dict(schemaVersion=1,files=api,scope='Pinned source citations; no CMake/Rust/native action, registration or packaging validation executed.'))
# The pure command-parser regression reads this real old database as DATA.
# Its paths/commands are never asserted to be a new-build observation.
capture(desc(FROZEN/'normal-off-compile_commands.json'))
build = json.loads((PARENT/'build-plan.json').read_bytes())
build.update(state='UNEXECUTED_RESOURCE_TASK_SELECTION342_NORMAL_OFF_BUILD_PLAN',recipe=desc(OWN/'proposed/tests/node-compat/build-engine.sh'),variants={'normal-off':{'NODE_COMPAT_GC_STRESS':'0'}},sourceRoot=SOURCE,workRoot=WORK,freezeRoot=FREEZE,taskSelectionCommands={'hostApi':1,'eventLoop':1},requiresFullNativeRebuild=True,engine=None,metadata=None,freezeReceipt=None,reviewedPins=None,rootBuildAuthority=None)
build['explicitEnvironment']['NODE_COMPAT_BUILD_ROOT']=WORK
build['explicitEnvironment']['NODE_COMPAT_GC_STRESS']='0'
write('build-plan.json',build)
write('future-config.template.json',dict(schemaVersion=1,sourceIndex=None,rootAuthority=None))
write('future-authority.template.json',dict(schemaVersion=1,state=None,sourceIndexSha256=None,sourceIndependentReview=None,phase=None,baseline='54b3329b3ce818fd1f244e871e9c259b63667cda',sourceRoot=SOURCE,workRoot=WORK,freezeRoot=FREEZE,stageAllowed=False,buildAllowed=False,componentAllowed=False,guestAllowed=False,sourcePromotionAllowed=False,runtimeAcceptanceClaim=False,rootAction=None,actualSourceStage=None,actualBuild=None,actualFreeze=None,actualNativeReview=None,nativePins={'normal-off':None,'gc-off':None,'normal-runtime':None},packagingClosure=None,actualComponentReview=None,allInvalidFixtureSource=None,allInvalidFixtureReview=None,fullResetOrReuse=False,als=False))
write('future-source-review-contract.json',dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_TASK_SELECTION_INTEGRATION_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,grantsStageOrBuildOrRuntimeAuthority=False))
write('runtime-gates.json',dict(schemaVersion=1,state='UNIMPLEMENTED_TASK_SELECTION342_RUNTIME_GATES',nativeAllInvalidComponentFixture=None,fixtureIndependentReview=None,packagingContext=None,actualComponent=None,actualGuest=None,actualHost=None,selectedTimerInterfaces=['wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'],pureExpectedImports=[],coarseClocksMayEmitAdditionalInterfaces=True,additionalImportsAuthorized=False,allInvalidHandleFixtureMustReleaseOwnedInterest=True,survivingFifoAndEngagedZeroRequired=True,unaccountedInterestMustKeepExistingFailure=True,actualNativeGcCountsObserved=False,rootIsolationProved=False,fullResetOrReuse=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
write('input-freeze.json',dict(schemaVersion=1,state='ORIGINAL_CONTEXT_TASK_SELECTION_INTEGRATION_PREPARATION_INPUTS',files=sorted(inputs.values(),key=lambda r:r['path']),originalContextsRetained=True,notAPackagingOrNativeArtifactClosure=True))
print(json.dumps(dict(sourceRows=342,resourceUnchanged=339,stageRows=len(stage),externalPreparationInputs=len(inputs),helperSha256=helper_sha,policySha256=policy_sha,recipeSha256=desc(OWN/'proposed/tests/node-compat/build-engine.sh')['sha256'],noOwnerActions=True)))
