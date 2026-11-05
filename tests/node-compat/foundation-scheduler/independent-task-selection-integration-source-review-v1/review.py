"""Independent source/hash/AST/extracted pure DATA audit; no owner imports."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import shlex
import stat
import types

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
SOURCE=HERE.parent/'task-selection-integration-candidate-v1'
SHA='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
checks=0
inputs={}


def check(v,note):
    global checks
    assert v,note;checks+=1


def d(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def regular(row):
    p=Path(row['path'])
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    check(p.is_absolute()and '..'not in p.parts,'absolute physical input')
    for q in (p,*p.parents):check(not q.is_symlink(),'no source links')
    a=p.stat();identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)
    check(stat.S_ISREG(a.st_mode)and a.st_size==row['bytes'],'regular expected size')
    if str(p)in inputs and inputs[str(p)]['identity']==identity:
        check(inputs[str(p)]['sha256']==row['sha256'],'compatible repeated input');return p
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();check(identity==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable source read')
    check(h.hexdigest()==row['sha256'],'source bytes pinned')
    inputs[str(p)]=dict(path=str(p),sha256=row['sha256'],bytes=row['bytes'],identity=identity);return p


def read(row):return json.loads(regular(row).read_bytes())


def family(row):
    value=read(row);root=Path(row['path']).parent;names=set();rows=[row]
    for r in value['files']:
        name=r['path'];check(name not in names and not Path(name).is_absolute()and all(x not in ('','.','..')for x in name.split('/')),'finite indexed member')
        names.add(name);v=dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']);regular(v);rows.append(v)
    actual=set()
    for p in root.rglob('*'):
        check(not p.is_symlink(),'family no links')
        if p.is_file():actual.add(str(p.relative_to(root)))
    check(actual==names|{'index.json'},'full exact family membership');return rows


def extract(path,names,scope):
    tree=ast.parse(path.read_bytes());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    check({n.name for n in nodes}==set(names),'exact pure definitions')
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path)+':pure','exec'),scope);return scope


def rejects(fn,note):
    try:fn()
    except (AssertionError,KeyError,TypeError,ValueError,AttributeError):check(True,note)
    else:check(False,note)


def put(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    check(not (HERE/'index.json').exists(),'new independent packet')
    index=d(SOURCE/'index.json');check(index['sha256']==SHA and index['bytes']==5120,'Root supplied source index')
    own=family(index);check(len(own)==33,'whole32-member source family')
    baseline=json.loads((SOURCE/'baseline-pins.json').read_bytes())
    freeze=json.loads((SOURCE/'input-freeze.json').read_bytes())
    check(len(freeze['files'])==540 and len({r['path']for r in freeze['files']})==540,'complete540 original-context preparation inputs')
    for row in freeze['files']:regular(row)
    for row in baseline['families'].values():family(row)
    for key in ['parentPolicy','resourceMetadata']:regular(baseline[key])
    policy=json.loads((SOURCE/'policy.json').read_bytes());parent=read(baseline['parentPolicy'])
    before={r['path']:r['sha256']for r in parent['expectedNativeSourceManifest']}
    after={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
    check(len(before)==len(after)==342 and before.keys()==after.keys(),'same342 path set')
    changed={k for k in before if before[k]!=after[k]}
    check(changed=={'include/extension-api.h','host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'}and sum(before[k]==after[k]for k in before)==339,'339 unchanged plus three selector files')
    check(after['builtins/web/timers.cpp']==before['builtins/web/timers.cpp']=='0024d009d11aab0705789f5d72fd8ec87deec9c44bdd8b913d970257aaadc9e4','timer ownership bytes retained')
    selection=policy['taskSelectionSourcePolicy']
    check(selection['sourceCandidateIndexSha256']=='d41686ae9e4cf9e7a4b76d60994065ca7f417a2d49b1940803cd996243ecfffb'and selection['sourceReviewIndexSha256']=='f0a9144156ddd49be291c8e65227777391fc4568d848c8da9d74ecf612ff503a','actual selector source/peer provenance')
    check(selection['requiresFullNativeRebuild']is True and selection['compatibleWithParentEngineAbi']is False,'real optional-return ABI rebuild obligation')
    native=json.loads((SOURCE/'native-inputs.json').read_bytes())['rows']
    check(len(native)==342 and {r['path']:r['source']['sha256']for r in native}==after,'complete native map')
    for row in native:
        regular(row['source']);check((row['path']in changed)==(row['role']=='new-selector-afterimage'),'native origin roles')
    cpp_calls=[];declarations=[]
    for row in native:
        if row['path'].endswith(('.cpp','.h')):
            for number,line in enumerate(Path(row['source']['path']).read_text().splitlines(),1):
                if 'AsyncTask::select('in line:cpp_calls.append(dict(path=row['path'],line=number,text=line))
                if 'static std::optional<size_t> select('in line:declarations.append(dict(path=row['path'],line=number,text=line))
    check(len(cpp_calls)==2 and len(declarations)==1,'complete new342 selector definition/one caller/header inventory')
    for row in baseline['externalEmbeddingSources']:
        path=Path(baseline['parentFreezeRoot'])/'componentize-source'/row['path']
        regular(dict(path=str(path),sha256=row['sha256'],bytes=path.stat().st_size))
        check('AsyncTask::select('not in path.read_text(),'unchanged external3 has no direct selector caller')
    selector_root=Path(baseline['families']['taskSelection']['path']).parent
    for row in selection['changes']:
        c=json.loads((selector_root/'source-contract.json').read_bytes())
        origin=next(x for x in c['changes']if x['path']==row['path'])
        regular(origin['original'])
        check(row['beforeSha256']==before[row['path']]and row['afterSha256']==after[row['path']],'immediate parent hash transition')
        check((SOURCE/'native'/row['path']).read_bytes()==(selector_root/'afterimages'/row['path']).read_bytes(),'exact reviewed d416 afterimage')
    inherited=['resourceOwnershipSourcePolicy','classicTraceSourcePolicy','embedding','nativePatchSha256','strictPolicyVersion','protectedPolicyVersion','classicPolicyVersion','profileVersion','classicManifest','classicManifestSha256','requiredHostInterfaces','privateTargetCpp']
    for field in inherited:check(policy[field]==parent[field],'unchanged inherited boundary/public field '+field)
    restored=copy.deepcopy(policy)
    restored['version']=parent['version'];restored['expectedNativeSourceManifest']=parent['expectedNativeSourceManifest'];del restored['taskSelectionSourcePolicy']
    for key in changed:
        if key in parent['sourceLayer']:restored['sourceLayer'][key]=parent['sourceLayer'][key]
        else:del restored['sourceLayer'][key]
    check(restored==parent,'whole finite policy reversal')
    derivations=json.loads((SOURCE/'derivations.json').read_bytes());edits=[]
    for key in ['helper','recipe','model','stage']:
        value=derivations[key];text=regular(value['donor']).read_text();original=text
        for e in value['edits']:
            check(text.count(e['before'])==e['count'],'derivation forward match '+key);text=text.replace(e['before'],e['after'])
        check(text==(SOURCE/value['afterimage']).read_text(),'complete derived afterimage '+key)
        for e in reversed(value['edits']):
            check(text.count(e['after'])==e['count'],'derivation reverse match '+key);text=text.replace(e['after'],e['before'])
        check(text==original,'complete donor reversal '+key);edits.append(dict(kind=key,edits=len(value['edits'])))
    check([x['edits']for x in edits]==[5,7,3,10],'finite25 exact text transformations')
    check((SOURCE/'task-selection-integration.UNAPPLIED.patch').read_bytes()==(selector_root/'task-selection.UNAPPLIED.patch').read_bytes(),'exact reviewed native patch')
    helper=(SOURCE/'layer-policy.py').read_text();recipe=(SOURCE/'proposed/tests/node-compat/build-engine.sh').read_text();stage=(SOURCE/'stage.py').read_text()
    check('PARENT.decorate('not in helper and 'PARENT.validate_sources('not in helper,'no old source/metadata validator substitution')
    check("PARENT_ROOT=HERE.parent/'integration-candidate-v1'"in helper and 'PARENT.validate_compilation(entries,embedding,ticks,repo)'in helper,'actual pure lower306 APIs only')
    check('checked_family(previous' in helper and 'checked_family(proposal' in helper and 'checked_family(peer' in helper,'whole immediate/selector/peer families before custom parent import')
    check(helper.index('verify_task_selection_ancestry()\nPARENT_ROOT')<helper.index('spec_from_file_location('),'ancestry barrier before custom import')
    check("metadata['taskSelectionPolicy']"in helper and "'nativeAllInvalidRuntimeValidation':None"in helper and "'allNativeDependentsRequireRebuild':True"in helper,'fresh truthful selector metadata policy')
    check(recipe.index('Task-selection source/work context mismatch')<recipe.index('"$node_bin" --version')and recipe.index('complete342 profile')<recipe.index('fetch_checked()'),'fresh contexts/full profile before actions')
    check('"$stress" == 0 && "$entropy_mode" == OFF' in recipe and '"$build_jobs" != 1' in recipe,'normal-OFF one-job selection')
    check(recipe.count(d(SOURCE/'layer-policy.py')['sha256'])==5 and recipe.count(d(SOURCE/'policy.json')['sha256'])==2,'all recipe helper/policy call sites pinned')
    check('source_manifest(repo)'in recipe and 'layer.decorate('in recipe and 'buildRecipeCheckedBeforeAndAfterBuild' in recipe,'actual source capture/decorate/recipe witness producer')
    # Reconstruct exact dynamic publication map without invoking stage.py.
    plan=json.loads((SOURCE/'stage-inputs.json').read_bytes());targets={}
    check(len(plan['files'])==533 and plan['nativeCount']==342 and plan['unchangedResourceParentFiles']==339,'actual533 base stage rows')
    for row in plan['files']:
        name=row['target'];check(name not in targets and not Path(name).is_absolute()and all(p not in ('','.','..')for p in name.split('/')),'safe unique stage target')
        regular(row['original']);targets[name]=row['original']
    for row in native:check(targets[row['path']]==row['source'],'all native paths actual stage source descriptors')
    for row in baseline['families'].values():
        rows=family(row);base=Path(row['path']).parent
        for r in rows:
            name=str(Path(r['path']).relative_to(REPO));check(targets[name]==r,'complete future helper ancestry dependency copied')
    old_count=len(targets)
    for row in own:targets[str(Path(row['path']).relative_to(REPO))]=row
    for row in plan['nativeAfterimageReplacements']:
        targets[row['path']]=next(r for r in own if r['path']==str(SOURCE/'native'/row['path']))
    targets['tests/node-compat/build-engine.sh']=next(r for r in own if r['path']==str(SOURCE/'proposed/tests/node-compat/build-engine.sh'))
    check(len(targets)==566 and old_count==533,'actual dynamic533+33 whole source seal566 targets')
    for row in native:check(targets[row['path']]['sha256']==after[row['path']],'all final staged native hashes')
    check("OWN==REPO/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'"in stage,'publisher original execution context only')
    check(stage.index('own=family(index)')<stage.index("for d in preparation['files']")<stage.index("subprocess.run(['git','clone'"),'whole source/preparation/peer before clone')
    check("'--no-local','--no-checkout'"in stage and "'checkout','--detach',BASE"in stage,'genuine isolated checkout mechanism')
    check('for d in captured:checked(d)'in stage and 'nativeReplacements=3' in stage,'final original byte checks and explicit new result scope')
    # Only extracted pure functions execute below: actual policy/hash maps and old command DATA.
    lower=SOURCE.parent/'integration-candidate-v1';lower_policy=read(d(lower/'policy.json'))
    pexpected=extract(lower/'layer-policy.py',['expected'],dict(POLICY=lower_policy))['expected']
    expected=extract(SOURCE/'layer-policy.py',['expected'],dict(POLICY=policy,PARENT=types.SimpleNamespace(expected=pexpected)))['expected']
    for name,value in after.items():
        layer=lower_policy['sourceLayer'].get(name)or policy['sourceLayer'].get(name);base=layer['beforeSha256']if layer else value
        check(expected(name,base)==value,'actual pure composed expected map '+name)
    for name in changed:rejects(lambda name=name:expected(name,'0'*64),'wrong preimage fails '+name)
    metadata=read(baseline['resourceMetadata']);database=Path(baseline['parentFreezeRoot'])/'normal-off-compile_commands.json';regular(d(database));entries=json.loads(database.read_bytes())
    scope=extract(SOURCE/'layer-policy.py',['_macro','_release','task_selection_commands'],dict(Path=Path,shlex=shlex))
    commands=scope['task_selection_commands'](entries,baseline['parentConfiguredRoot'],metadata)
    check(set(commands)=={'host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'},'real old command DATA parsed for two exact roles')
    host=next(r for r in entries if r['file'].endswith('/host-apis/wasi-0.2.0/host_api.cpp'))
    caller=next(r for r in entries if r['file'].endswith('/runtime/event_loop.cpp'))
    negative=0
    for bad in [[r for r in entries if r is not host],entries+[host],[r for r in entries if r is not caller],entries+[caller]]:
        rejects(lambda bad=bad:scope['task_selection_commands'](bad,baseline['parentConfiguredRoot'],metadata),'missing/duplicate actual compile role');negative+=1
    for token in ['-DNODE_COMPAT_INTERNAL_TICKS=1','-DNODE_COMPAT_CLASSIC_STREAMS=1','-DNODE_COMPAT_STRICT_INITIALIZATION=1','-DNODE_COMPAT_GC_STRESS=1','-UNDEBUG','-O0','-fsyntax-only']:
        bad=copy.deepcopy(entries);r=next(x for x in bad if x['file']==host['file']);r['command']+=' '+token
        rejects(lambda bad=bad:scope['task_selection_commands'](bad,baseline['parentConfiguredRoot'],metadata),'wrong actual host command macro/mode');negative+=1
    model=extract(SOURCE/'native-admission-model.py',['validate_metadata'],{})['validate_metadata']
    args=(policy,d(SOURCE/'policy.json')['sha256'],d(SOURCE/'layer-policy.py')['sha256'],d(SOURCE/'proposed/tests/node-compat/build-engine.sh')['sha256'],baseline['externalEmbeddingSources'],'normal-off')
    rejects(lambda:model(metadata,*args),'old342 metadata cannot claim new342 source')
    rejects(lambda:model(metadata,*args[:-1],'gc-off'),'unimplemented GC variant rejected')
    # Source/protocol fields and future gates remain distinct from actual runtime evidence.
    event=(SOURCE/'native/runtime/event_loop.cpp').read_text();header=(SOURCE/'native/include/extension-api.h').read_text();host_source=(SOURCE/'native/host-apis/wasi-0.2.0/host_api.cpp').read_text()
    check('static std::optional<size_t> select('in header and 'std::optional<size_t> api::AsyncTask::select('in host_source,'consistent changed C++ ABI')
    check(event.index('if (!selected)')<event.index('const size_t task_idx = *selected;')<event.index('JS::Rooted<TracedAsyncTask> running(cx);')<event.index('tasks->at(task_idx)'),'optional guard before rooted selected task access')
    check(host_source.index('if (tasks.empty())')<host_source.index('auto count = tasks.size()'),'reviewed no-empty-selector poll branch preserved')
    source_evidence=json.loads((SOURCE/'source-evidence.json').read_bytes())
    for item in source_evidence['files']:
        path=regular(item['descriptor']);lines=path.read_text().splitlines()
        for line in item['lines']:check(lines[line['line']-1]==line['text'],'actual CMake/Rust/source citation')
    future=json.loads((SOURCE/'future-authority.template.json').read_bytes());runtime_gates=json.loads((SOURCE/'runtime-gates.json').read_bytes());build=json.loads((SOURCE/'build-plan.json').read_bytes())
    for name in ['state','phase','sourceIndexSha256','sourceIndependentReview','rootAction','actualSourceStage','actualBuild','actualFreeze','actualNativeReview','packagingClosure','actualComponentReview','allInvalidFixtureSource','allInvalidFixtureReview']:check(future[name]is None,'unissued source/phase proof '+name)
    for name in ['stageAllowed','buildAllowed','componentAllowed','guestAllowed','sourcePromotionAllowed','runtimeAcceptanceClaim','fullResetOrReuse','als']:check(future[name]is False,'closed phase flag '+name)
    check(all(v is None for v in future['nativePins'].values())and build['ownedBuildController']is None and build['rootBuildAuthority']is None,'new tooling/pins/controller absent')
    for name in ['sourceRoot','workRoot','freezeRoot']:check(not Path(plan[name]).exists()and not Path(plan[name]).is_symlink(),'no actual stage/build/freeze')
    syntax=json.loads((SOURCE/'syntax-evidence.json').read_bytes());regular(syntax['tool'])
    check(syntax['argv']==['/bin/bash','-n',str(SOURCE/'proposed/tests/node-compat/build-engine.sh')]and syntax['rawExitCode']==0 and syntax['stdoutBytes']==syntax['stderrBytes']==0 and syntax['parsedSourceSha256']==d(SOURCE/'proposed/tests/node-compat/build-engine.sh')['sha256'],'stored genuine Bash parse-only observation')
    astfiles=[]
    for p in sorted(SOURCE.glob('*.py')):ast.parse(p.read_bytes());astfiles.append(p.name)
    embedded=[]
    for m in re.finditer(r"<<'(?P<tag>PY[A-Z]*)'\n(?P<code>[\s\S]*?)\n(?P=tag)(?:\n|$)",recipe):ast.parse(m['code']);embedded.append(m['tag'])
    check(len(embedded)==4,'actual four embedded Python blocks parsed')
    put('data-audit.json',dict(schemaVersion=1,checks=checks,uniqueReadHashInputs=len(inputs),sourceMembers=32,preparationInputs=540,nativePaths=342,
        unchangedResourceSources=339,nativeReplacements=3,baseStageRows=533,dynamicStageTargets=566,exactDerivations=edits,
        expectedFunctionCases=342,commandParserOldDataPositive=1,commandParserNegatives=negative,oldMetadataRejected=True,positiveMetadataFabricated=False,
        pythonAst=astfiles,embeddedPythonAst=embedded,producerBashParseStored=True,reviewerBashOrNodeOrCompilerInvoked=False,
        actualNativeSelectorUses=cpp_calls,actualOptionalDeclaration=declarations,externalEmbeddingSourcesRehashed=3))
    put('checked-inputs.json',dict(schemaVersion=1,files=[{k:r[k]for k in ['path','sha256','bytes']}for _,r in sorted(inputs.items())]))
    result=dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_TASK_SELECTION_INTEGRATION_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=SHA,
        sourceOnly=True,sourceReviewPassed=True,verifiedPassed=True,ownerActionsInvoked=False,sourceIndex=index,
        resourceSourceIndexSha256=selection['parentIntegrationIndexSha256'],selectorSourceIndexSha256=selection['sourceCandidateIndexSha256'],selectorSourceReviewIndexSha256=selection['sourceReviewIndexSha256'],
        nativeSourceFiles=342,unchangedResourceParentFiles=339,nativeReplacements=3,timerOwnershipPatchPreserved=True,
        publicModuleSurfaceChanged=False,fullNativeRebuildRequired=True,compatibleWithParentEngineAbi=False,
        actualOwnModuleImportInvoked=False,compilerOrCompiledModelInvoked=False,nodeInvoked=False,engineOrGuestOrRuntimeInvoked=False,
        actualStage=None,actualBuild=None,actualFreeze=None,actualComponent=None,nativePins=None,nativeAllInvalidFixture=None,
        operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False,adoptionAllowed=False,
        grantsStageOrBuildOrRuntimeAuthority=False,concreteBlockers=[],
        coverage=dict(sourceMembers=32,preparationInputRows=540,uniqueReadHashInputs=len(inputs),checks=checks,
            nativePaths=342,unchangedResourceSources=339,replacements=3,baseStageRows=533,dynamicStageTargets=566,
            exactTextDerivations=4,exactTextEdits=25,pureExpectedCases=342,oldCommandDataPositive=1,commandParserNegatives=negative,
            pythonAstFiles=len(astfiles),embeddedPythonAstBlocks=4),
        qualifications=['Historical resource policy, selector source/models/frontend evidence and peer are DATA; old metadata is rejected and no positive new receipt is fabricated',
            'Existing optional-return C++ ABI changes require rebuilding all dependents; no old engine/object/pin admission follows from equal342 counts or unchanged boundary tags',
            'Dormant publisher is original-context only and has no owned lifecycle/deadline or complete partial-failure journal of its own; a separately reviewed external stage controller and raw result review remain required',
            'Build controller, full new SDK/compile/link/archive/native proofs, new source-aware freezer/pin/bootstrap tooling and runtime packaging/fixture remain absent',
            'Actual all-invalid progression, interest release, task destructor/JS roots, cached pollable lifetime, WASI calls, timer regressions, reset/reuse and ALS remain unproved',
            'Coarse clock selection is unresolved packaging work: actual emitted standard0.2.10 imports/type audit remains a separate gate'])
    put('results.json',result)
    put('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],requiredFixedValues={k:result[k]for k in ['schemaVersion','sourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','nativeSourceFiles','unchangedResourceParentFiles','nativeReplacements','fullNativeRebuildRequired','compatibleWithParentEngineAbi','operationalAdmission','runtimeAcceptanceClaim','grantsStageOrBuildOrRuntimeAuthority']},requiredCoverage=result['coverage'],requiredExactDescriptors=dict(sourceIndex=index),issuesNoAuthority=True))
    print(json.dumps(dict(sourceReviewPassed=True,checks=checks,inputs=len(inputs),sourceMembers=32,stageTargets=566)))


if __name__=='__main__':main()
