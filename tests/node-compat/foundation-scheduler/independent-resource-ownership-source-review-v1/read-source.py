"""Independent read/hash, source reversals and retained frontend evidence; no compiler/model execution."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shlex

REPO = Path('/Users/dan/dev/StarlingMonkey')
OWNER = REPO / 'tests/node-compat/foundation-scheduler/resource-ownership-candidate-v1'
HERE = Path(__file__).resolve().parent
seen = {}
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


def checked(row):
    path = Path(row['path'])
    check(path.is_absolute())
    physical = path.resolve(strict=True)
    check(physical.is_file())
    a = physical.stat()
    h = hashlib.sha256()
    with physical.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    b = physical.stat()
    check((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns) == (b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns))
    actual = dict(path=str(path),sha256=h.hexdigest(),bytes=b.st_size)
    check(actual == {k:row[k] for k in actual})
    if str(path) in seen:
        check(seen[str(path)]['declared'] == actual)
    seen[str(path)] = dict(declared=actual,resolvedPath=str(physical),leafSymlink=path.is_symlink(),linkText=str(path.readlink()) if path.is_symlink() else None)
    return physical


def read(row):
    path = checked(row)
    raw = path.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == row['sha256'])
    return json.loads(raw)


index_row = dict(path=str(OWNER/'index.json'),sha256='02e9779be8c2e360996d0d6a878afddd6490da8ad8c12e7c3177dc5e745d6f4c',bytes=3996)
index = read(index_row)
names = [r['path'] for r in index['files']]
check(len(names) == len(set(names)) == 25)
check(not any(p.is_symlink() for p in OWNER.rglob('*')))
check(sorted(p.relative_to(OWNER).as_posix() for p in OWNER.rglob('*') if p.is_file()) == sorted(names+['index.json']))
for r in index['files']:
    checked(dict(r,path=str(OWNER/r['path'])))
source_inputs = json.loads((OWNER/'source-inputs.json').read_bytes())['files']
check(len(source_inputs) == len({r['path'] for r in source_inputs}) == 1075)
for r in source_inputs:
    checked(r)
proof = json.loads((OWNER/'derivations.json').read_bytes())
derivations = []
patch = ''
for r in proof['files']:
    before = (OWNER/'base'/r['path']).read_bytes()
    after = (OWNER/'afterimages'/r['path']).read_bytes()
    check(before == (REPO/r['path']).read_bytes())
    check(hashlib.sha256(before).hexdigest() == r['beforeSha256'] and len(before) == r['beforeBytes'])
    check(hashlib.sha256(after).hexdigest() == r['afterSha256'] and len(after) == r['afterBytes'])
    text = before.decode()
    for edit in r['edits']:
        check(text.count(edit['before']) == 1)
        text = text.replace(edit['before'],edit['after'])
    check(text.encode() == after)
    for edit in reversed(r['edits']):
        check(text.count(edit['after']) == 1)
        text = text.replace(edit['after'],edit['before'])
    check(text.encode() == before)
    patch += ''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+r['path'],tofile='b/'+r['path']))
    derivations.append(dict(path=r['path'],edits=len(r['edits']),forwardAndReverseExact=True,liveOriginalUnchanged=True))
check(patch.encode() == (OWNER/'resource-ownership.UNAPPLIED.patch').read_bytes())
check(sum(r['edits'] for r in derivations) == 9)
header_map = json.loads((OWNER/'header-closure.json').read_bytes())
declared = header_map['actualFrontendDependencies']
check(len(declared) == header_map['uniqueDeclaredDependencies'] == 1028)
for r in declared:
    check(str(checked(r['declared'])) == r['resolvedPath'])
cpp_deps = [r for r in declared if r['declared']['path'].endswith('.cpp')]
check(len(cpp_deps) == 2)
frontends = []
dependency_union = set()
for stem, relative in [('timers','builtins/web/timers.cpp'),('event_loop','runtime/event_loop.cpp')]:
    t = json.loads((OWNER/'evidence'/(stem+'.terminal.json')).read_bytes())
    check(t['rawExitCode'] == 0 and not t['timeout'] and t['frontendOnly'] and not t['objectOrLinkOrNativeBuildRequested'])
    for key in ('sourceAfterimage','actualCompileDatabase','originalWrapper','actualDirectCompiler','stdout','stderr','dependencyFile'):
        checked(t[key])
    check(t['stdout']['bytes'] == t['stderr']['bytes'] == 0)
    db = read(t['actualCompileDatabase'])
    check(t['originalCompileRow'] in db)
    original = t['originalCompileRow']
    words = shlex.split(original['command'])
    check(words.pop(0) == t['originalWrapper']['path'])
    check(words.count('-o') == words.count('-c') == 1)
    at = words.index('-o');del words[at:at+2]
    at = words.index('-c');check(words[at+1] == original['file']);del words[at:at+2]
    expected = [t['actualDirectCompiler']['path'],*words,'-iquote',str(Path(original['file']).parent),'-fsyntax-only','-MD','-MF',t['dependencyFile']['path'],'-MT','source-only-'+stem,str(OWNER/'afterimages'/relative)]
    check(t['argv'] == expected and t['cwd'] == original['directory'])
    check('-o' not in expected and '-c' not in expected and '-fsyntax-only' in expected)
    check(str(Path(t['actualDirectCompiler']['path']).resolve()) == t['resolvedCompiler'])
    wrapper = Path(t['originalWrapper']['path']).read_text()
    check(t['actualDirectCompiler']['path'] in wrapper and '"$@"' in wrapper)
    text = Path(t['dependencyFile']['path']).read_text()
    deps = shlex.split(text.split(':',1)[1].replace('\\\n',' '))
    dependency_union.update(deps)
    check(all(x in {r['declared']['path'] for r in declared} for x in deps))
    frontends.append(dict(name=stem,rawExitCode=t['rawExitCode'],declaredDependencies=len(deps),argvReconstructedExactly=True,retainedStreamsEmpty=True,reviewerReranCompiler=False))
check(dependency_union == {r['declared']['path'] for r in declared})
model = json.loads((OWNER/'model-results.json').read_bytes())
check(len(model['cases']) == 12 and model['checks'] == 89 and all(r['passed'] for r in model['cases']))
check(sum(r['checks'] for r in model['cases']) + 1 == model['checks'])
for file in OWNER.glob('*.py'):
    ast.parse(file.read_bytes())
    checks += 1
timer = (OWNER/'afterimages/builtins/web/timers.cpp').read_text()
loop = (OWNER/'afterimages/runtime/event_loop.cpp').read_text()
check('RefPtr<api::AsyncTask>' in timer and 'iter.get().value()->trace(trc)' in timer)
check(timer.index('const auto owned = std::exchange(handle_, INVALID_POLLABLE_HANDLE)') < timer.index('host_api::MonotonicClock::unsubscribe(owned)'))
check(timer.index('retired_ = true;') < timer.index('drop_pollable();\n    auto entry'))
check('~TimerTask() override { drop_pollable(); }' in timer)
check('retire();\n      JS_ReportOutOfMemory(cx);' in timer and 'retire();\n      return false;' in timer)
check('if (retired_) return true; // clearTimeout/clearInterval during callback' in timer)
check(timer.index('ENGINE->queue_async_task(timer);') < timer.index('timer->subscribe();') < timer.index('++TIMERS_MAP->next_timer_id;'))
check('incr_event_loop_interest' not in timer and 'decr_event_loop_interest' not in timer)
check('JS::Rooted<TracedAsyncTask> retiring' in loop and 'JS::Rooted<TracedAsyncTask> running' in loop)
check(loop.index('retiring.get().task = task;') < loop.index('tasks->erase(it);') < loop.index('retiring.get().task->cancel(engine)'))
check(loop.index('running.get().task = tasks->at(task_idx);') < loop.index('tasks->erase(tasks->begin() + task_idx);') < loop.index('running.get().task->run(engine)'))
seams = json.loads((OWNER/'api-seams.json').read_bytes())
check({r['id'] for r in seams['unresolved']} >= {'GLOBAL_FALLIBLE_QUEUE','RESET_UNSUPPORTED','HOST_TRAPS_AND_HANDLE_FAILURE','NATIVE_RUNTIME_VALIDATION'})
check(seams['productionApplied'] is False and seams['rootPhase'] is None and seams['runtimeValidation'] is None)
# Retained SDK declarations establish the actual generic rooting/allocation APIs.
sdk = Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build/spidermonkey-dist-release/include/js')
check('tp->trace(trc)' in (sdk/'GCPolicyAPI.h').read_text())
check('registerWithRootLists(rootLists(cx));' in (sdk/'RootingAPI.h').read_text())
check('class SystemAllocPolicy : public AllocPolicyBase' in (sdk/'AllocPolicy.h').read_text())
for item in list(seen.values()):
    checked(item['declared'])
value = dict(schemaVersion=1,state='INDEPENDENT_RESOURCE_OWNERSHIP_SOURCE_DATA_CHECKS_PASSED',checks=checks,inputDescriptors=list(seen.values()),ownerMembers=25,preparationRows=1075,exactDerivations=derivations,patchReconstructionExact=True,frontendEvidence=frontends,declaredDependencies=1028,cppAfterimageDependencies=2,otherHeaderDependencies=1026,authorModelCasesAuthenticated=12,authorModelChecksAuthenticated=89,authorModelRerun=False,compilerInvokedByReviewer=False,sourceOrCppApplied=False,runtimeOrHelperInvoked=False)
with(HERE/'data-results.json').open('x')as out:json.dump(value,out,indent=2);out.write('\n')
print(json.dumps(dict(checks=checks,uniqueLexicalInputs=len(seen),sourceOnly=True,ownerActionsInvoked=False)))
