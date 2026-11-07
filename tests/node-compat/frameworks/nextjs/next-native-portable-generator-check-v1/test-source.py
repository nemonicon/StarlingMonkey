"""Inert DATA and actual AST functions only; no generator/monitor/main/copy."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
text = (HERE / 'run.py').read_text()
tree = ast.parse(text)
names = ['canonical', 'command_argv', 'clean', 'layout', 'native_descriptors', 'collect']
nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
constants = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'COMMANDS' for t in n.targets))
scope = dict(Path=Path, re=__import__('re'), hashlib=hashlib, json=json)
exec(compile(ast.Module(body=[constants, *nodes], type_ignores=[]), '<actual inert functions>', 'exec'), scope)
plan = json.loads((HERE / 'plan.json').read_text())
commands = scope['command_argv'](plan, plan['sourceRoot'])
donor = ast.parse(Path(plan['commandDonor']['path']).read_text())
old = next(n.value for n in donor.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'commands' for t in n.targets))
old_commands = eval(compile(ast.Expression(old), '<actual old command list>', 'eval'), dict(source=Path(plan['sourceRoot'])))
expected = [[plan['node']['path'], str(Path(plan['sourceRoot']) / 'builtins/node-compat' / c[0]), *c[1:], '--check'] for c in old_commands]
assert commands == expected and len(commands) == 10
checks = 1
admission_source = Path(plan['portableAdmission']['module']['path']).read_bytes()
assert hashlib.sha256(admission_source).hexdigest() == plan['portableAdmission']['module']['sha256']
admission_tree = ast.parse(admission_source)
pure_nodes = [n for n in admission_tree.body if isinstance(n, ast.FunctionDef) and n.name in ['require', 'relative', 'generator_argv', 'role_copies']]
pure = {'Path': Path}
exec(compile(ast.Module(body=pure_nodes, type_ignores=[]), '<held consumer pure functions>', 'exec'), pure)
policy = json.loads(Path(plan['portableAdmission']['plan']['path']).read_text())['portableSourcePolicy']
selection_path = Path('/private/tmp/starling-node-compat/next-native-portable-build-preparation-v1-first/portable-selection.json')
selection_data = selection_path.read_bytes()
assert hashlib.sha256(selection_data).hexdigest() == 'b209cf8f80fb779b0c5074157675b0c050edb548c2afd7b021613a9717480e37'
selection = json.loads(selection_data)  # Retained metadata only; not an admit/generator invocation.
assert commands == pure['generator_argv'](policy, selection['sourceRoot'], plan['node'])
assert scope['native_descriptors'](selection) == [r['source'] for r in pure['role_copies'](selection, 'native-policy-source')]
checks += 2
base = dict(schemaVersion=1, state='ROOT_PORTABLE_NEXT_GENERATORS_AUTHORIZED_V1', unissued=False,
    runId='portable-generators-test', generatorChecksAllowed=True, nodeHostSourceOnly=True)
for key in ['nativeBuildAllowed', 'compilerAllowed', 'cmakeAllowed', 'cargoAllowed', 'engineAllowed', 'guestAllowed', 'networkAllowed', 'copySourceAllowed']:
    base[key] = False
out, outer = scope['layout'](base, plan)
assert str(outer) == str(out) + '-external-root'
checks += 1
for mutate in [lambda a: a.update(runId='x\n'), lambda a: a.update(runId='../x'), lambda a: a.update(runId='A'),
    lambda a: a.update(runId='x'*49), lambda a: a.update(generatorChecksAllowed=None),
    lambda a: a.update(nodeHostSourceOnly=False), lambda a: a.update(guestAllowed=True),
    lambda a: a.update(unissued=True), lambda a: a.update(argv=[]), lambda a: a.update(outputRoot='/elsewhere')]:
    a = deepcopy(base)
    mutate(a)
    try:
        scope['layout'](a, plan)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Unsafe authority accepted')
for key, value in [('outputPrefix', '/arbitrary'), ('perCommandSeconds', 31), ('outerSeconds', 901),
                   ('minimumFreeBytes', 0), ('maxAcceptedRawStreamBytes', 0), ('maxAcceptedOutputBytes', 0)]:
    p = deepcopy(plan)
    p[key] = value
    try:
        scope['layout'](base, p)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Changed finite policy accepted')
terminal = dict(rawExitCode=0, parentOwnedGroupGone=True, allObservedOwnedGroupsGone=True,
    timeout=False, forcedCleanup=False, errors=[], signals=[], interruptedSignals=[], remainingObservedPids=[])
assert scope['clean'](terminal) is True
assert scope['clean'](dict(terminal, rawExitCode=1)) is True  # Cleanup is distinct from acceptance.
checks += 2
for key, value in [('timeout', True), ('forcedCleanup', True), ('errors', [{}]), ('signals', [{}]),
    ('interruptedSignals', [2]), ('remainingObservedPids', [17]), ('parentOwnedGroupGone', False), ('allObservedOwnedGroupsGone', False)]:
    assert scope['clean'](dict(terminal, **{key: value})) is False
    checks += 1


class InertPath:
    def __init__(self, value): self.value = str(value)
    def __str__(self): return self.value
    def __truediv__(self, value): return InertPath(self.value + '/' + str(value))
    @property
    def parent(self): return InertPath(self.value.rsplit('/', 1)[0])
    def exists(self): return self.value.endswith(('stdout.log', 'stderr.log', 'started.json', 'terminal.json'))
    def is_symlink(self): return False
    def mkdir(self, **kwargs): pass


selected = dict(sourceRoot='/inert/source', composition={'inert': 'composition'}, sourceMaterialization={'inert': 'summary'},
    roleContentSha256='inert', physicalRecords=[dict(path='/inert/' + str(i), ino=i) for i in range(825)], directoryRecords=[dict(path='/inert')],
    files=[dict(role='native-policy-source', path='file-' + str(i).zfill(3) + '.cpp', sha256='0'*64, bytes=1) for i in range(435)])
for mode in ['success', 'raw1', 'interrupted', 'monitor-throws', 'prephase-refusal', 'final-refusal', 'tool-change']:
    durable_rows, monitor_calls, bootstrap_calls, tool_calls = [], [], [], []
    def bootstrap(_):
        bootstrap_calls.append(1)
        if (mode == 'prephase-refusal' and len(bootstrap_calls) == 3) or (mode == 'final-refusal' and len(bootstrap_calls) == 12):
            raise RuntimeError('inert protected input refusal')
        return dict(sourceIndex={}, plan={}), plan, {'inert': 'authority'}, InertPath('/inert/output'), InertPath('/inert/outer'), deepcopy(selected)
    class InertMonitor:
        def monitor(self, *args):
            monitor_calls.append(args)
            if mode == 'monitor-throws': raise RuntimeError('inert original monitor exception')
            t = deepcopy(terminal)
            t['rawExitCode'] = 1 if mode == 'raw1' else 0
            if mode == 'interrupted': t['interruptedSignals'] = [2]
            t.update(stdout=dict(path='/inert/stdout', sha256=hashlib.sha256(b'').hexdigest(), bytes=0),
                     stderr=dict(path='/inert/stderr', sha256=hashlib.sha256(b'').hexdigest(), bytes=0))
            return t
    def tool_snapshot(_):
        tool_calls.append(1)
        return [{'nodeIdentity': 2 if mode == 'tool-change' and len(tool_calls) == 2 else 1}]
    # Compile the actual collector with passive dependencies; no actual globals rebound.
    environment = dict(scope, bootstrap=bootstrap, load=lambda *_: InertMonitor(),
        durable=lambda p, value: durable_rows.append((str(p), deepcopy(value))),
        row=lambda p: dict(path='/inert/stdout' if str(p).endswith('stdout.log') else '/inert/stderr' if str(p).endswith('stderr.log') else str(p), sha256=hashlib.sha256(b'').hexdigest(), bytes=0), diagnostic=lambda e: dict(message=str(e)),
        total_bytes=lambda _: 0, os=SimpleNamespace(umask=lambda _: None), environment=lambda _: {'inert': 'environment'},
        shutil=SimpleNamespace(disk_usage=lambda _: SimpleNamespace(free=plan['minimumFreeBytes'])),
        tool_snapshot=tool_snapshot,
        print=lambda *a, **k: None)
    node = next(n for n in nodes if n.name == 'collect')
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<actual collector inert dependencies>', 'exec'), environment)
    code = environment['collect']('/inert/authority')
    body = durable_rows[-1][1]
    assert durable_rows[-1][0].endswith('/body-result.json')
    assert code == (0 if mode == 'success' else 1) and body['passed'] is (mode == 'success')
    assert body['portableInputsPreserved'] is (mode != 'final-refusal')
    assert len(monitor_calls) == (10 if mode in ['success', 'final-refusal', 'tool-change'] else 1)
    assert all(c[4] == 30 and c[1] == '/inert/source' for c in monitor_calls)
    if mode == 'raw1': assert body['commands'][0]['rawExitCode'] == 1 and body['commands'][0]['ownedGroupsClean'] is True
    if mode == 'monitor-throws': assert body['primaryError'] and body['sourceAfter'] == body['sourceBefore']
    if mode == 'final-refusal': assert body['finalProtectionError'] and body['passed'] is False
    if mode == 'tool-change': assert body['toolProtectionError'] and body['toolInputsPreserved'] is False
    checks += 1
assert 'os.O_EXCL' in text and 'os.fsync' in text and 'os.fchmod' in text
assert text.count('monitor.monitor(') == 2 and 'subprocess' not in text
assert text.index('free >=') < text.index('outer.mkdir(mode=0o700)')
checks += 3
print(json.dumps(dict(sourceOnly=True, checks=checks, exactTenDonorArgv=True, genuineCollectorAstWithInertDependencies=True,
    failureFinallyAndFullRaw1BeforeAssertions=True, generatorsMonitorsMainCopiesOrRuntimeInvoked=False)))
