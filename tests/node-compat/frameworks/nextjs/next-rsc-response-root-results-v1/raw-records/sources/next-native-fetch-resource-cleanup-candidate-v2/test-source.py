"""Exact retained Source/failure checks only; no C++ compiler or target API."""
from pathlib import Path
import ast
import importlib.util
import json
import re

HERE = Path(__file__).resolve().parent

def main():
    checks = 0
    def need(value, label):
        nonlocal checks
        if value is not True: raise AssertionError(label)
        checks += 1
    spec = importlib.util.spec_from_file_location('pure_nodiscard_source_renderer', HERE/'prepare.py')
    prepare = importlib.util.module_from_spec(spec); spec.loader.exec_module(prepare)
    manifest, rendered, patch = prepare.render()
    before = prepare.checked(manifest['before']); after = prepare.checked(manifest['after'])
    need(rendered == after and patch == (HERE/'nodiscard.patch').read_text(), 'exact afterimage/patch reproduction')
    need(after.replace('(void)cancel(engine);', 'cancel(engine);') == before, 'only the three explicit casts differ')
    need(after.count('(void)cancel(engine);') == 3 and before.count('(void)cancel(engine);') == 0, 'exact three new discards')
    need(len(after.encode()) - len(before.encode()) == 18, 'six bytes per cast')
    need(manifest['before']['sha256'] == manifest['parentAfterimage']['sha256'] == '01f9e8696836277d6ede8479f7e4407c3ac6e32b4edd5631986c250e3e913722', 'exact parent afterimage before')
    need(manifest['parentSourceIndex']['sha256'].startswith('f52274f3'), 'held parent source family')
    need(len(manifest['inheritedAfterimages']) == 5 and
         len({item['relativePath'] for item in manifest['inheritedAfterimages']}) == 5, 'five distinct inherited afterimages')
    need(all(item['relativePath'] != manifest['relativePath'] for item in manifest['inheritedAfterimages']), 'no duplicate replacement role')
    need(manifest['relativePath'] == 'builtins/web/fetch/request-response.cpp' and
         len(list((HERE/'before').rglob('*.cpp'))) == len(list((HERE/'after').rglob('*.cpp'))) == 1, 'only one physical CPP before/after')
    cancel_before = before.split('bool ResponseFutureTask::cancel(api::Engine*) {', 1)[1].split('\n}', 1)[0]
    cancel_after = after.split('bool ResponseFutureTask::cancel(api::Engine*) {', 1)[1].split('\n}', 1)[0]
    need(cancel_before == cancel_after and cancel_after.count('return true;') == 1 and
         'return false;' not in cancel_after, 'unconditional true cancellation implementation unchanged')
    need('auto owned = std::move(future_);' in cancel_after and 'if (owned) owned->close();' in cancel_after,
         'unique-owner retirement unchanged')
    need(after.count('return cancel(engine);') == before.count('return cancel(engine);') == 1, 'final returned result preserved')
    need('if (!engine->cancel_async_task(keep_alive)) (void)cancel(engine);' in after, 'original queued cancellation conditional preserved')
    need(after.index('(void)cancel(engine);\n    api::throw_error') < after.index('return RejectPromiseWithPendingError(cx, response_promise);', after.index('(void)cancel(engine);\n    api::throw_error')), 'error rejection remains after retirement')
    need(after.index('(void)cancel(engine); // Received response') < after.index('RootedObject response_obj(cx, Response::create_incoming', after.index('(void)cancel(engine); // Received response')), 'response construction remains after retirement')
    header = next(item for item in manifest['inheritedAfterimages'] if item['relativePath'].endswith('request-response.h'))
    need('[[nodiscard]] bool cancel(api::Engine *engine) override;' in prepare.checked(header['after']), 'nodiscard contract retained')
    for key in ['actualMaterialization','actualFrontendCheck','actualFullBuild','actualComponent','actualGuest']:
        need(manifest[key] is None, 'no fabricated V2 actual: '+key)
    need(manifest['publicApiAdded'] is False and manifest['newLifecycleOrCleanupPath'] is False and manifest['actionsAllowed'] is False, 'no scope expansion/permission')
    need(manifest['selectedCountsUnchanged'] == dict(native=435,support=387,embedding=3,total=825), 'selection counts unchanged intended')
    proof = json.loads((HERE/'failure-provenance.json').read_text())
    need(proof['rawExitCodes'] == [0,0,1] and len(proof['commands']) == 3, 'failed parent command denominator')
    need(prepare.checked(proof['actualFailedSource']) == before, 'actual failed frontend consumed exact parent afterimage')
    need(prepare.checked(proof['commands'][2]['stderr']) == (HERE/'actual-failure.stderr.log').read_text(), 'actual exact retained diagnostic')
    stderr = (HERE/'actual-failure.stderr.log').read_text()
    need([int(n) for n in re.findall(r':(\d+):\d+: error: ignoring return value', stderr)] == [3355,3368,3406], 'all three genuine nodiscard locations')
    need(stderr.count('[-Werror,-Wunused-result]') == 3 and stderr.endswith('3 errors generated.\n'), 'complete exact compiler diagnostic')
    result = json.loads(prepare.checked(proof['result']))
    need(result['passed'] is False and result['rawExitCodes'] == [0,0,1] and result['completedCommands'] == 3, 'parent frontend failure remains failed')
    need(result['authority'] == proof['authority'], 'Root authority join')
    for command in proof['commands']:
        start = json.loads(prepare.checked(command['started'])); terminal = json.loads(prepare.checked(command['terminal']))
        need(start['pid'] == terminal['pid'] == command['pid'] and start['timeoutSeconds'] == 180, 'original per-command PID/bound')
        need(terminal['rawExitCode'] == command['rawExitCode'] and terminal['authority'] == proof['authority'], 'original per-command raw/authority')
        need(terminal['stdout'] == command['stdout'] and terminal['stderr'] == command['stderr'], 'original stream descriptors')
        prepare.checked(command['stdout']); prepare.checked(command['stderr'])
    for path in HERE.glob('*.py'):
        tree = ast.parse(path.read_text())
        need(not any(isinstance(node,(ast.Import,ast.ImportFrom)) and any(item.name in ['subprocess','socket'] for item in node.names) for node in ast.walk(tree)), 'no actor imports '+path.name)
    print(json.dumps(dict(sourceOnly=True, passed=True, checks=checks, changedFiles=1,
        explicitDiscardCalls=3, addedBytes=18, inheritedAfterimages=5,
        parentFrontendRawExitCodes=[0,0,1], candidateCppCompiled=False,
        compilerOrWasiOrGuestOrProcessOwnerExecuted=False)))

if __name__ == '__main__': main()
