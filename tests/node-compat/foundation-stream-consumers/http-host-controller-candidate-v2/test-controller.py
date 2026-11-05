"""Pure identity counterexamples and benign Python child lifecycle tests only."""
from pathlib import Path
import importlib.util
import json
import os
import tempfile
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('root_http_controller_source', HERE / 'controller.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


def row(pid, ppid, pgid, birth='Thu Nov  5 12:00:00 2026'):
    return dict(pid=pid, ppid=ppid, pgid=pgid, birth=birth, command='/benign/python')


rows = {100: row(100, 1, 100), 101: row(101, 100, 101), 102: row(102, 101, 101), 103: row(103, 1, 103)}
known = {}
check(len(module.discover(rows, known, 100)) == 3)
check(set(known) == {100, 101, 102})
groups = module.group_model(rows, known, 100)
check({g['pgid'] for g in groups} == {100, 101})
check(all(g['signalAllowed'] for g in groups))
changed = {pid: dict(value) for pid, value in rows.items()}
changed[101]['birth'] = 'Thu Nov  5 12:00:01 2026'
changed[102]['birth'] = 'Thu Nov  5 12:00:02 2026'
check(next(g for g in module.group_model(changed, known, 100) if g['pgid'] == 101)['signalAllowed'] is False)
changed[100]['command'] = '/unrelated/reused-pid'
check(next(g for g in module.group_model(changed, known, 100) if g['pgid'] == 100)['signalAllowed'] is False)
check(all(not g['alive'] for g in module.group_model({}, known, 100)))
check(module.parse_snapshot('100 1 100 Thu Nov 5 12:00:00 2026 /benign/python\n')[100]['birth'] == 'Thu Nov 5 12:00:00 2026')
check(len(module.snapshot()) > 0)
# M1: an observed nonleader must not vanish with its unobserved group leader.
leaderless_known={100:row(100,1,100),102:row(102,100,101)}
leaderless_current={102:row(102,1,101)}
accounted=module.group_model(leaderless_current,leaderless_known,100)
check({r['pgid'] for r in accounted}=={100,101})
check(next(r for r in accounted if r['pgid']==101)['alive'] is True)
check(next(r for r in accounted if r['pgid']==101)['signalAllowed'] is False)
check(any(r['alive'] for r in accounted))
# M1: current PGID migration is accounted for, without silently adopting it.
migration_known={100:row(100,1,100),102:row(102,100,100)}
migration_current={102:row(102,1,102)}
accounted=module.group_model(migration_current,migration_known,100)
check({r['pgid'] for r in accounted}=={100,102})
check(next(r for r in accounted if r['pgid']==102)['alive'] is True)
check(next(r for r in accounted if r['pgid']==102)['signalAllowed'] is False)
check(any(r['alive'] for r in accounted))
# A PID reused in another group remains an accounted unknown, never signallable.
reused={102:row(102,1,777,birth='Thu Nov 5 12:00:01 2026')}
accounted=module.group_model(reused,migration_known,100)
check(next(r for r in accounted if r['pgid']==777)['alive'] is True)
check(next(r for r in accounted if r['pgid']==777)['signalAllowed'] is False)

scratch = Path(tempfile.mkdtemp(prefix='consumers355-http-controller-benign-v1-', dir='/private/tmp/starling-node-compat'))
source = scratch / 'fixture.py'
source.write_text('import sys,time\nprint("benign Python stdout",flush=True)\nprint("benign Python stderr",file=sys.stderr,flush=True)\nif len(sys.argv)>1: time.sleep(30)\n')
environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
records = []
for name, arguments, timeout in [('normal', [], 10), ('bounded-timeout', ['wait'], 0.5)]:
    output = scratch / name
    output.mkdir(mode=0o700)
    result = module.monitor([sys.executable, str(source), *arguments], str(scratch), environment, output, timeout, {'benignFixtureOnly':True}, parent_grace_seconds=1, sample_seconds=0.05)
    records.append(dict(name=name, terminal=module.descriptor(output / 'terminal.json')))
    check(result['parentOwnedGroupGone'] is True)
    check(result['allObservedOwnedGroupsGone'] is True)
    check(not result['errors'])
    check((output/'stdout.log').read_text() == 'benign Python stdout\n')
    check((output/'stderr.log').read_text() == 'benign Python stderr\n')
    if name == 'normal':
        check(result['rawExitCode'] == 0 and result['forcedCleanup'] is False and result['timeout'] is False)
    else:
        check(result['rawExitCode'] < 0 and result['forcedCleanup'] is True and result['timeout'] is True)

descendant_source = scratch / 'descendant.py'
descendant_source.write_text('import subprocess,sys,time\nchild=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\nprint(child.pid,flush=True)\ntime.sleep(0.5)\n')
output = scratch / 'parent-exit-owned-descendant'
output.mkdir(mode=0o700)
result = module.monitor([sys.executable,str(descendant_source)],str(scratch),environment,output,10,{'benignFixtureOnly':True},parent_grace_seconds=1,sample_seconds=0.05)
records.append(dict(name='parent-exit-owned-descendant',terminal=module.descriptor(output/'terminal.json')))
descendant_pid = int((output/'stdout.log').read_text())
check(descendant_pid in {r['pid'] for r in result['observedProcesses']})
check(result['rawExitCode'] == 0 and result['forcedCleanup'] is True and result['timeout'] is False)
check(result['parentOwnedGroupGone'] is True and result['allObservedOwnedGroupsGone'] is True and not result['errors'])
check(any(r['pgid'] == descendant_pid for r in result['signals']))

value = dict(schemaVersion=1, checks=checks, benignOwnedSessions=records, scratchRoot=str(scratch), ownerHostOrPreflightOrGuestOrNativeActionsInvoked=False)
print(json.dumps(value))
