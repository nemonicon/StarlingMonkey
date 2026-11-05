"""Pure mocked wire/source/caller tests only. No owned child or phase is run."""
from pathlib import Path
import ast
import copy
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pure_timing_v5_models_only', HERE / 'models.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
refs = json.loads((HERE / 'references.json').read_bytes())
checks = []


def passed(name, call):
    assert call() is True
    checks.append(dict(name=name, passed=True))


def denied(name, call):
    try:
        call()
    except (ValueError, KeyError, TypeError, UnicodeError):
        checks.append(dict(name=name, refused=True))
    else:
        raise AssertionError(name)


root = dict(schemaVersion=1, state='ROOT_REVIEWED_ZLIB_COST_PILOT_TIMING_PHASE_V1', phase='timing', sourceIndexSha256=M.SOURCE_SHA, actionAllowed=True, sourceIndependentReview=refs['sourcePeer'], independentPreparedPlanReview=refs['planReview'], preparedPlan=refs['preparedPlan'], calibrationSourceIndex=refs['originalCalibrationSource'], warmNPlan=refs['pilotReview'], warmNMatchedPlan=refs['matchedPlan'], calibrationDecisionSha256=M.DECISION, outputRoot=M.TIMING_OUT, externalOutputRoot=M.EXTERNAL_OUT, externalParentDeadlineSeconds=7200, runId='SYNTHETIC_MODEL_ONLY', globalBudgetMs=5400000, phaseAuthority=dict(path='/synthetic/phase.json', sha256='a' * 64, bytes=1), quietWindowAuthority=dict(path='/synthetic/quiet.json', sha256='b' * 64, bytes=1), operationalAdmission=False, runtimeAcceptanceClaim=False, metadataProjection=False, controlSubtraction=False, sourcePromotionAllowed=False)
phase = {k: copy.deepcopy(root[k]) for k in ['sourceIndexSha256', 'phase', 'runId', 'globalBudgetMs', 'calibrationSourceIndex', 'preparedPlan', 'quietWindowAuthority', 'warmNPlan', 'warmNMatchedPlan']}
phase.update(schemaVersion=1, state='ROOT_APPROVED_BOUNDED_CODEC_MEASUREMENT_PHASE_V1', actionAllowed=True)
quiet = dict(schemaVersion=1, state='ROOT_COORDINATED_CODEC_MEASUREMENT_QUIET_WINDOW_V1', exclusiveMeasurementApproved=True, sourceIndexSha256=M.SOURCE_SHA, phase='timing', runId=root['runId'], competingAgentWorkStopped=True, rootOtherBuildRuntimeOrHashAuditsStopped=True, backgroundDesktopAndSystemActivityControlled=False, startsAtUtc='2030-01-01T00:00:00.000Z', expiresAtUtc='2030-01-01T02:00:00.000Z')
now = 1893456000000
passed('synthetic timing-only wire with actual distinct source/plan/calibration descriptors', lambda: M.scopes(root, phase, quiet, refs, now))
for key, value in [('phase', 'pilot-candidate'), ('sourceIndexSha256', M.PILOT_SHA), ('actionAllowed', False), ('globalBudgetMs', 5400001), ('globalBudgetMs', True), ('globalBudgetMs', 0), ('globalBudgetMs', 1.5), ('externalParentDeadlineSeconds', 7201), ('outputRoot', '/tmp/other'), ('runId', '../bad'), ('operationalAdmission', True), ('metadataProjection', True), ('controlSubtraction', True), ('sourcePromotionAllowed', True)]:
    v = copy.deepcopy(root)
    v[key] = value
    denied('Root scope refusal ' + key + '=' + str(value), lambda v=v: M.scopes(v, phase, quiet, refs, now))
for key in ['preparedPlan', 'calibrationSourceIndex', 'warmNMatchedPlan']:
    v = copy.deepcopy(root)
    v[key]['sha256'] = 'f' * 64
    denied('Root exact descriptor drift ' + key, lambda v=v: M.scopes(v, phase, quiet, refs, now))
for key in ['sourceIndexSha256', 'runId', 'phase', 'globalBudgetMs', 'calibrationSourceIndex', 'preparedPlan', 'quietWindowAuthority', 'warmNPlan', 'warmNMatchedPlan']:
    v = copy.deepcopy(phase)
    v[key] = None
    denied('phase cross-binding ' + key, lambda v=v: M.scopes(root, v, quiet, refs, now))
for key, value in [('competingAgentWorkStopped', False), ('rootOtherBuildRuntimeOrHashAuditsStopped', False), ('backgroundDesktopAndSystemActivityControlled', True), ('exclusiveMeasurementApproved', False), ('phase', 'pilot-candidate'), ('expiresAtUtc', '2030-01-01T00:01:00.000Z'), ('startsAtUtc', '2030-01-01T00:00:00Z')]:
    v = copy.deepcopy(quiet)
    v[key] = value
    denied('quiet-window refusal ' + key, lambda v=v: M.scopes(root, phase, v, refs, now))
denied('expired window', lambda: M.scopes(root, phase, quiet, refs, now + 7200000))

terminal = dict(rawExitCode=0, parentOwnedGroupGone=True, allObservedOwnedGroupsGone=True, timeout=False, forcedCleanup=False, signals=[], errors=[], interruptedSignals=[], remainingObservedPids=[], finalGroups=[dict(pgid=1234, alive=False)])
passed('clean mocked actual-terminal wire', lambda: M.clean_terminal(terminal))
for key, value in [('rawExitCode', 1), ('rawExitCode', False), ('parentOwnedGroupGone', False), ('allObservedOwnedGroupsGone', False), ('timeout', True), ('forcedCleanup', True), ('signals', [9]), ('errors', ['x']), ('remainingObservedPids', [1]), ('finalGroups', [dict(pgid=1234, alive=True)])]:
    v = copy.deepcopy(terminal)
    v[key] = value
    denied('terminal refusal ' + key, lambda v=v: M.clean_terminal(v))

publication = dict(index=dict(path='index.json', sha256='c' * 64, bytes=123), completion=dict(path='completion.json', sha256='d' * 64, bytes=456))
heartbeat = dict(event='codec-phase-operational-heartbeat', name=sorted(M.timing_jobs())[0], elapsedMs=30000, stdoutBytes=0, stderrBytes=0, partialObservationOnly=True)
encode = lambda values: b''.join((json.dumps(v, separators=(',', ':')) + '\n').encode() for v in values)
for n in [0, 1, 2]:
    raw = encode([heartbeat] * n + [publication])
    prefix, final = M.publication_lines(raw)
    assert prefix == [heartbeat] * n and final == publication
    checks.append(dict(name='exact full JSONL prefix and original relative rows ' + str(n), passed=True))
for name, raw in [('missing final newline', encode([publication])[:-1]), ('prefix after publication', encode([publication, heartbeat])), ('duplicate final', encode([publication, publication])), ('prepared-plan stdout is wrong phase', encode([dict(publication, result=dict(path='prepared-plan.json', sha256='e' * 64, bytes=1))])), ('unknown prefix', encode([dict(heartbeat, event='other'), publication])), ('pilot prefix', encode([dict(heartbeat, name='pilot-provider-c0-n1-native-on'), publication])), ('negative prefix count', encode([dict(heartbeat, stdoutBytes=-1), publication])), ('duplicate key', b'{"index":0,"index":1}\n'), ('nonfinite', b'{"index":NaN}\n'), ('invalid utf8', b'\xff\n')]:
    denied('JSONL refusal ' + name, lambda raw=raw: M.publication_lines(raw))
v = copy.deepcopy(publication)
v['index']['path'] = '../index.json'
denied('relative publication traversal', lambda: M.publication_lines(encode([v])))
env = dict(HOME='/unchanged/user', CODEX_HOME='/unchanged/codex', PATH='/bin', NODE_OPTIONS='bad', NODE_COMPAT_FAKE='bad', NAPI_RS_FORCE_WASI='bad', DYLD_INSERT_LIBRARIES='bad', LD_PRELOAD='bad')
actual = M.environment(env)
assert actual['HOME'] == env['HOME'] and actual['CODEX_HOME'] == env['CODEX_HOME'] and actual['PATH'] == env['PATH']
assert all(k not in actual for k in ['NODE_OPTIONS', 'NODE_COMPAT_FAKE', 'NAPI_RS_FORCE_WASI', 'DYLD_INSERT_LIBRARIES', 'LD_PRELOAD'])
checks.append(dict(name='actual caller environment preserves home identities and removes loader overrides', passed=True))
assert len(M.timing_jobs()) == 360
checks.append(dict(name='360 exact original timing job names', passed=True))

controller = ast.parse((HERE / 'controller.py').read_text())
main = next(n for n in controller.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
calls = [n for n in ast.walk(main) if isinstance(n, ast.Call)]
monitor = next(n for n in calls if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'monitor' and n.func.attr == 'monitor')
assert len(monitor.args) == 6 and isinstance(monitor.args[4], ast.Constant) and monitor.args[4].value == 7200
text = (HERE / 'controller.py').read_text()
assert text.index('admitted = guard.authorize(') < text.index("spec = importlib.util.spec_from_file_location('genuine_0af") < text.index('terminal = monitor.monitor(')
assert text.index('external.mkdir(mode=0o700)') < text.index('terminal = monitor.monitor(')
assert "finally:" in text and "admitted['capture'].recheck()" in text
assert 'sys.path' not in ast.unparse(controller) and 'sys.modules' not in ast.unparse(controller)
checks.append(dict(name='genuine six-argument7200 API after authorize/fresh0700 directory plus final recheck', passed=True))
value = dict(schemaVersion=1, state='TIMING_V5_CONTROLLER_PURE_MODELS_PASSED', checks=len(checks), observations=checks, fixturesAreSyntheticUnissuedAuthorities=True, actualAuthorityWritten=False, processOrMonitorOrPreflightOrGuestOrCodecOrTimingInvoked=False)
(HERE / 'evidence' / 'pure-results.json').write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(value))
