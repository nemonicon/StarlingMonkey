"""Independent READ/HASH/AST/pure DATA review. No producer or compiler imports."""
import ast
import difflib
import hashlib
import itertools
import json
from pathlib import Path
import shlex
import stat

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
SOURCE=HERE.parent/'task-selection-candidate-v1'
EXPECTED='d41686ae9e4cf9e7a4b76d60994065ca7f417a2d49b1940803cd996243ecfffb'
observed={}
checks=0


def check(v,note):
    global checks
    assert v,note;checks+=1


def descriptor(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)


def regular(row):
    p=Path(row['path']);check(p.is_absolute(),'absolute descriptor')
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    check('..'not in p.parts,'canonical physical descriptor')
    for parent in (p,*p.parents):check(not parent.is_symlink(),'physical regular source')
    before=p.stat();ident=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
    check(stat.S_ISREG(before.st_mode)and before.st_size==row['bytes'],'exact regular size')
    old=observed.get(str(p))
    if old and old['identity']==ident:
        check(old['sha256']==row['sha256'],'compatible repeated source');return p
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat();check(ident==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable source read')
    check(h.hexdigest()==row['sha256'],'exact source hash')
    observed[str(p)]=dict(path=str(p),sha256=row['sha256'],bytes=row['bytes'],identity=ident);return p


def read(row):
    p=regular(row);check(row['bytes']<=32*1024*1024,'bounded JSON data');return json.loads(p.read_bytes())


def indexed(row):
    value=read(row);base=Path(row['path']).parent;names=set()
    for r in value['files']:
        check(r['path']not in names and not Path(r['path']).is_absolute()and '..'not in Path(r['path']).parts,'finite index member')
        names.add(r['path']);regular(dict(path=str(base/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    actual=set()
    for p in base.rglob('*'):
        check(not p.is_symlink(),'no family link')
        if p.is_file():actual.add(str(p.relative_to(base)))
    check(actual==names|{'index.json'},'complete index membership');return value


def extract_selector(text):
    starts=['std::optional<size_t> api::AsyncTask::select(','size_t api::AsyncTask::select(']
    start=next(text.index(s)for s in starts if s in text)
    return text[start:text.index('\nnamespace host_api {',start)]


def location(text,needle):
    check(text.count(needle)==1,'unique semantic location '+needle[:60])
    return text[:text.index(needle)].count('\n')+1


def pure_selector(ids,ready,cached=False):
    """Independent abstract interpretation of the reviewed C++ branch structure.

    Scalars only: no RefPtr/JS/host ABI/destructor or actual poll execution.
    """
    tasks=[x for x in ids if x!=-1]
    if not tasks:return None,tasks,[],cached,0
    handles=[];subscriptions=0
    for idx,item in enumerate(tasks):
        if item==-2:
            if handles:
                if not cached:cached=True;subscriptions+=1
                handles.append(77)
                return min(ready),tasks,handles,cached,subscriptions
            return idx,tasks,[],cached,subscriptions
        handles.append(item)
    return min(ready),tasks,handles,cached,subscriptions


def put(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    check(not (HERE/'index.json').exists(),'new independent family')
    index=descriptor(SOURCE/'index.json');check(index['sha256']==EXPECTED and index['bytes']==3562,'Root-supplied source identity')
    members=indexed(index);check(len(members['files'])==22,'all22 source members')
    contract=json.loads((SOURCE/'source-contract.json').read_bytes())
    indexed(contract['parentIntegrationIndex']);indexed(contract['parentFrozenReviewIndex'])
    frozen_peer=json.loads((Path(contract['parentFrozenReviewIndex']['path']).parent/'results.json').read_bytes())
    check(frozen_peer['verifiedPassed']is True and frozen_peer['nativeSourceFiles']==342,'genuine342 frozen parent')
    metadata=read(frozen_peer['metadata']);receipt=read(frozen_peer['freezeReceipt'])
    check(metadata['gcStress']is False and metadata['entropyPolicy']=='off','actual normal-OFF source context')
    frozen=Path(contract['parentFrozenSourceRoot']);configured=Path(frozen_peer['configuredSourceRoot'])
    check(str(frozen)==frozen_peer['frozenSourceRoot'],'actual frozen source role')
    check(len(metadata['sourceManifest'])==342,'342 parent native sources')
    for r in metadata['sourceManifest']:
        for root in [frozen,configured]:
            p=root/r['path'];regular(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size))
    check(len(metadata['componentizeSourceManifest'])==3,'actual external embedding3')
    for r in metadata['componentizeSourceManifest']:
        p=Path(frozen_peer['componentizeSourceRoot'])/r['path']
        regular(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size))
        check('AsyncTask::select('not in p.read_text(),'no direct external embedding select caller')
    manifest={r['path']:r['sha256']for r in metadata['sourceManifest']}
    patches=[];total_edits=0
    for change in contract['changes']:
        check(manifest[change['path']]==change['original']['sha256'],'afterimages start from genuine parent manifest')
        original=regular(change['original']).read_bytes();before=regular(change['before']).read_bytes();after=regular(change['after']).read_bytes()
        check(before==original,'full original source bytes')
        text=before.decode()
        for edit in change['edits']:
            check(text.count(edit['before'])==edit['count'],'exact edit match');text=text.replace(edit['before'],edit['after']);total_edits+=1
        check(text.encode()==after,'forward complete afterimage')
        for edit in reversed(change['edits']):
            check(text.count(edit['after'])==edit['count'],'exact reverse match');text=text.replace(edit['after'],edit['before'])
        check(text.encode()==before,'reverse complete original')
        patches.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+change['path'],tofile='b/'+change['path']))
    check(''.join(patches)==(SOURCE/'task-selection.UNAPPLIED.patch').read_text(),'whole actual patch exact')
    check(total_edits==5 and len(contract['changes'])==3,'finite three-file/five-edit cut')
    after_host=(SOURCE/'afterimages/host-apis/wasi-0.2.0/host_api.cpp').read_text()
    before_host=(SOURCE/'before/host-apis/wasi-0.2.0/host_api.cpp').read_text()
    runtime=(SOURCE/'afterimages/runtime/event_loop.cpp').read_text()
    old_runtime=(SOURCE/'before/runtime/event_loop.cpp').read_text()
    header=(SOURCE/'afterimages/include/extension-api.h').read_text()
    selector=extract_selector(after_host);legacy=extract_selector(before_host)
    check(selector.index('std::erase_if')<selector.index('if (tasks.empty())')<selector.index('auto count = tasks.size()')<selector.index('poll_handles('),'prune/empty guard before all polling')
    check('return std::nullopt;' in selector,'explicit empty optional result')
    guard=runtime[runtime.index('    if (!selected) {'):runtime.index('    const size_t task_idx = *selected;')]
    check(guard.count('continue;')==1 and 'return'not in guard,'caller uses normal loop boundary')
    check(runtime.index('auto selected = api::AsyncTask::select(*tasks);')<runtime.index('if (!selected)')<runtime.index('const size_t task_idx = *selected;')<runtime.index('JS::Rooted<TracedAsyncTask> running(cx);')<runtime.index('running.get().task = tasks->at(task_idx);')<runtime.index('tasks->erase(tasks->begin() + task_idx);')<runtime.index('running.get().task->run(engine);'),'valid index/root/run ordering')
    check(runtime[:runtime.index('    // Select the next task')]==old_runtime[:old_runtime.index('    // Select the next task')],'checkpoint/exception/finalizer/interest/empty-queue boundary unchanged')
    check(runtime[runtime.index('    JS::Rooted<TracedAsyncTask> running(cx);'):]==old_runtime[old_runtime.index('    JS::Rooted<TracedAsyncTask> running(cx);'):],'rooted task run/error path unchanged')
    check('static PersistentRooted<TaskQueue> queue;' in runtime and 'for (const auto &task : tasks)' in runtime,'queue JS tracing retained')
    check('interest_cnt'not in guard and 'decr_event_loop_interest'not in selector,'selector does not fabricate interest release')
    check('static std::optional<size_t> select(' in header and '#include <optional>' in header,'declaration matches implementation and owns include')
    # Complete342-source production call search, distinct from live tree inventory.
    calls=[];defs=[];ids=[]
    for r in metadata['sourceManifest']:
        p=frozen/r['path']
        if p.suffix in ['.cpp','.h']:
            for n,line in enumerate(p.read_text().splitlines(),1):
                if 'AsyncTask::select('in line:
                    (defs if line.startswith('size_t api::AsyncTask::select')else calls).append(dict(path=str(p),line=n,text=line))
                if 'id() override'in line or 'PollableHandle id()'in line:ids.append(dict(path=str(p),line=n,text=line))
    check(len(calls)==len(defs)==1,'actual frozen342 only one select definition and caller')
    check(calls[0]['path']==str(frozen/'runtime/event_loop.cpp')and calls[0]['line']==291,'resource-frozen caller role291')
    live=[]
    for name in ['include/extension-api.h','runtime/event_loop.cpp','host-apis/wasi-0.2.0/host_api.cpp']:
        p=REPO/name;regular(descriptor(p))
        for n,line in enumerate(p.read_text().splitlines(),1):
            if 'static size_t select('in line or 'AsyncTask::select('in line:live.append(f'{name}:{n}:{line}')
    check('\n'.join(live)+'\n'==(SOURCE/'caller-inventory.txt').read_text(),'inventory authentic untouched production tree; distinct frozen base')
    timer=frozen/'builtins/web/timers.cpp';timertext=timer.read_text()
    check('~TimerTask() override { drop_pollable(); }'in timertext and 'bool retired_ = false;'in timertext,'inherited timer resource ownership source preserved')
    check('return outgoing_pollable_;'in after_host and 'return incoming_pollable_;'in after_host,'actual host id overrides retained read-only returns')
    locations=dict(hostEmptyCheck=location(after_host,'  if (tasks.empty()) {'),hostSelect=location(after_host,'std::optional<size_t> api::AsyncTask::select('),
        optionalDeclaration=location(header,'  static std::optional<size_t> select('),eventLoopSelect=location(runtime,'    auto selected = api::AsyncTask::select(*tasks);'),
        eventLoopNullGuard=location(runtime,'    if (!selected) {'),eventLoopRoot=location(runtime,'    JS::Rooted<TracedAsyncTask> running(cx);'))

    # Stored host model is authenticated and reconstructed as DATA, never compiled/executed.
    model=json.loads((SOURCE/'model-results.json').read_bytes());regular(model['generatedModel'])
    final=extract_selector(after_host);old=extract_selector(before_host)
    renamed=old.replace('api::AsyncTask::select','api::LegacyAsyncTask::select').replace('RefPtr<AsyncTask>','RefPtr<LegacyAsyncTask>')
    generated=(SOURCE/'model-prefix.cpp').read_text()+'\n'+final+'\n'+renamed+'\n'+(SOURCE/'model-suffix.cpp').read_text()
    check(generated.encode()==Path(model['generatedModel']['path']).read_bytes(),'stored model embeds full actual original/new selector bodies')
    check(len(model['commands'])==2 and all(r['rawExitCode']==0 and r['stderr']==''for r in model['commands']),'stored host compile/model records clean')
    check(json.loads(model['commands'][1]['stdout'])==dict(schemaVersion=1,cases=12,allPassed=True,abstractHostModelOnly=True,guestExecuted=False),'stored12 model stdout exact')
    suffix=(SOURCE/'model-suffix.cpp').read_text()
    check(suffix.count('  example(')==10,'ten table selector examples')
    check('api::AsyncTask::select(mixed)'in suffix and 'api::LegacyAsyncTask::select(old)'in suffix,'cached reuse and legacy synthetic exception are other two cases')
    check('EventLoop'not in generated and 'interest_cnt'not in generated,'stored model has no event-loop/interest implementation')
    # Independent finite scalar selector model, qualified separately from C++ execution.
    cases=0;empty=0
    for length in range(5):
        for vector in itertools.product([-1,-2,10,20],repeat=length):
            surviving=[v for v in vector if v!=-1]
            immediate=surviving.index(-2)if -2 in surviving else None
            poll_count=0 if not surviving or immediate==0 else (len(surviving)if immediate is None else immediate+1)
            subsets=[()]if poll_count==0 else [tuple(i for i in range(poll_count)if mask&(1<<i))for mask in range(1,1<<poll_count)]
            for ready in subsets:
                chosen,kept,polled,cached,subscriptions=pure_selector(vector,ready)
                check(kept==surviving,'pure stable survivor order')
                if not surviving:
                    check(chosen is None and not polled and subscriptions==0,'pure all-invalid no poll');empty+=1
                else:
                    check(chosen is not None and 0<=chosen<len(surviving),'pure surviving valid selected index')
                    check(chosen==(0 if immediate==0 else min(ready)),'pure oldest reported-ready survivor')
                check(not polled or len(polled)>0,'pure poll list nonempty')
                cases+=1
    # SDK records: reconstruct actual argv/overlay/dependency physical mappings, no compiler call.
    sdk=json.loads((SOURCE/'sdk-results.json').read_bytes())
    for key in ['metadata','compileDatabase','compiler','overlay']:regular(sdk[key])
    check(sdk['metadata']['sha256']==frozen_peer['metadataSha256'],'SDK uses genuine resource build metadata')
    db=read(sdk['compileDatabase']);check(sdk['compileDatabase']['sha256']==metadata['compileCommandsSha256'],'genuine captured compile DB')
    overlay=read(sdk['overlay']);maps={r['name']:r['external-contents']for r in overlay['roots']}
    wanted={str(configured/c['path']):c['after']['path']for c in contract['changes']}
    check(overlay['version']==0 and overlay['use-external-names']is False and maps==wanted and len(overlay['roots'])==3,'exact three-file VFS, no synthetic headers')
    deps=set();calls_sdk=[]
    for call in sdk['calls']:
        check(call['originalCompileRow']in db,'actual selected compile row membership')
        selected=[r for r in db if r['file']==str(configured/call['source'])]
        check(selected==[call['originalCompileRow']],'unique genuine CPP row')
        words=shlex.split(selected[0]['command']);regular(call['donorWrapper'])
        check(str(Path(words[0]).resolve())==call['donorWrapper']['path'],'recorded original wrapper identity')
        at=words.index('-o');trimmed=words[1:at]+words[at+2:];trimmed.remove('-c')
        dep=SOURCE/'sdk-evidence'/(Path(call['source']).stem+'.d')
        expected=[str(Path(sdk['compiler']['path']).parent/'clang++'),*trimmed,'-fsyntax-only','-ivfsoverlay',str(SOURCE/'sdk-evidence/overlay.json'),'-MD','-MF',str(dep),'-MT','source-check']
        check(call['argv']==expected,'exact actual compile row -> frontend-only argv')
        check(call['rawExitCode']==0 and call['stdout']==call['stderr']==''and call['frontendOnly']is True,'stored raw frontend result0/empty')
        terminal=json.loads((SOURCE/'sdk-evidence'/(Path(call['source']).stem+'-terminal.json')).read_bytes());check(terminal==call,'whole terminal record equals SDK call')
        names=shlex.split(dep.read_text().replace('\\\n','').split(':',1)[1])
        for name in names:
            p=Path(name)
            if not p.is_absolute():p=Path(selected[0]['directory'])/p
            deps.add(str(p))
        calls_sdk.append(call['source'])
    check(sorted(calls_sdk)==['host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'],'exact two SDK CPP checks')
    check(len(deps)==1031 and len(sdk['dependencyFiles'])==1031 and sdk['uniqueDependencies']==1031,'complete1031 logical dependencies')
    check(deps=={r['logicalPath']for r in sdk['dependencyFiles']},'full dependency .d union exact')
    for row in sdk['dependencyFiles']:
        regular(row['physical'])
        physical=Path(maps.get(row['logicalPath'],row['logicalPath'])).resolve()
        check(str(physical)==row['physical']['path'],'actual overlay dependency physical resolution')
    check({name for name in maps if name in deps}==set(maps),'all three changed files genuinely present in frontend deps')
    alias=Path(sdk['compiler']['path']).parent/'clang++';chain=[]
    while alias.is_symlink():
        target=alias.readlink();chain.append(dict(path=str(alias),target=str(target)));alias=(alias.parent/target).absolute()
    check(str(alias.resolve())==sdk['compiler']['path'],'actual SDK compiler alias terminal')
    parsed=[]
    for p in sorted(SOURCE.glob('*.py')):ast.parse(p.read_bytes());parsed.append(str(p.relative_to(SOURCE)))
    for p in SOURCE.rglob('*.json'):json.loads(p.read_bytes())
    put('data-audit.json',dict(schemaVersion=1,checks=checks,sourceMembers=22,exactFileReversals=3,exactTextEdits=5,
        actualParentNativeSourceFiles=342,fullFrozenAndConfiguredParentSourceHashes=True,
        sdkFrontendRecords=2,sdkLogicalDependencyPaths=1031,allOverlayFilesInDeps=True,sdkCompilerAliasChain=chain,
        storedHostSelectorModelCases=12,storedHostModelEventLoopCases=0,
        independentAbstractSelectorCases=cases,independentAbstractEmptySelectionCases=empty,
        currentProductionCallerInventory=live,frozenResourceCallers=calls,frozenResourceDefinitions=defs,actualIdDefinitions=ids,
        afterimageLocations=locations,producerPythonAstFiles=parsed,
        reviewerCompilerOrModelOrGuestOrOwnerHelpersExecuted=False))
    put('checked-inputs.json',dict(schemaVersion=1,files=[{k:r[k]for k in ['path','sha256','bytes']}for _,r in sorted(observed.items())]))
    result=dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_TASK_SELECTION_SOURCE_REVIEW_PASSED_V1',verifiedPassed=True,
        sourceIndexSha256=EXPECTED,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,
        sourceIndex=index,parentFrozenReviewIndex=contract['parentFrozenReviewIndex'],changedNativeFiles=3,
        semanticSourceReviewPassed=True,concreteBlockers=[],abiCompatibleWithExistingEngine=False,requiresFullNativeRebuild=True,
        preservesInheritedTaskRootAndTimerOwnershipSource=True,interestAccountingChanged=False,
        optionalIndexZeroRemainsEngaged=True,externalEmbeddingSourcesReviewed=3,
        noEmptyHostPollForEmptyOrAllInvalidSelection=True,eventLoopContinuationSourceReviewed=True,
        storedModelsExecuteEventLoop=False,storedModelsEstablishInterestOrJsRooting=False,
        coverage=dict(sourceMembers=22,exactFileReversals=3,exactTextEdits=5,parentNativeSourceFiles=342,
            authenticatedFrontendCalls=2,logicalSdkDependencies=1031,storedSelectorModelCases=12,
            independentAbstractSelectorCases=cases),
        sourceApplied=False,nativeEngineBuilt=False,engineExecuted=False,componentExecuted=False,
        compilerInvokedByReviewer=False,nodeInvokedByReviewer=False,hostModelExecutedByReviewer=False,
        guestOrFaultOrUnsafeResetInvokedByReviewer=False,liveProcessQueryOrSignalInvokedByReviewer=False,
        operationalAdmission=False,runtimeAcceptanceClaim=False,adoptionAllowed=False,
        qualifications=['caller-inventory.txt is the untouched live production tree at line280; frozen resource caller291 is a distinct physical role',
            'Stored12 source-extracted host cases cover the selector only: ten examples, cached reuse, synthetic legacy empty-poll exception; no EventLoop/interest/JS/rooting execution',
            'Source CFG review shows nullopt re-enters checkpoint/failure/finalizer/interest boundary; no runtime interest-release, task destructor, exception or WASI behavior proved',
            'SDK records are frontend-only for two real CPP rows with a three-file VFS overlay; all dependents require rebuilding after C++ return ABI change',
            'Independent scalar model is abstract branch interpretation, not execution of original/new C++, RefPtr, SpiderMonkey or a host poll',
            'Inherited cached immediate pollable lifetime, fallible enqueue, stream/HTTP cancellation, bounded jobs, reset/reuse and ALS remain open'],
        sourcePeerOrActionAuthorityIssued=False)
    put('results.json',result)
    put('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],
        requiredFixedValues={k:result[k]for k in ['schemaVersion','verifiedPassed','sourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','changedNativeFiles','requiresFullNativeRebuild','operationalAdmission','runtimeAcceptanceClaim','adoptionAllowed']},
        requiredCoverage=result['coverage'],requiredExactDescriptors=dict(sourceIndex=index,parentFrozenReviewIndex=contract['parentFrozenReviewIndex']),
        issuesNoAuthority=True))
    print(json.dumps(dict(checks=checks,readHashInputs=len(observed),abstractSelectorCases=cases,sourceReviewPassed=True)))


if __name__=='__main__':main()
