"""Pure finite wire/scope models. No phase, process, clock or filesystem call."""
import datetime
import json
import re

TIMING_OUT = '/private/tmp/starling-node-compat/zlib-cost-timing-v5'
EXTERNAL_OUT = TIMING_OUT + '-external-root'
SOURCE_SHA = 'e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321'
PILOT_SHA = 'b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1'
DECISION = '3cf4eb748d9fcf1e985eddfbdfd49544e507e83300056336fc8665fff22c546e'
PEER_STATE = 'INDEPENDENT_ZLIB_COST_TIMING_V5_CONTROLLER_SOURCE_REVIEW_PASSED_V1'


def need(value, message):
    if not value:
        raise ValueError(message)


def strict_json(raw):
    def pairs(values):
        out = {}
        for key, value in values:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def nonfinite(_value):
        raise ValueError('nonfinite JSON constant')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def integer(value, minimum, maximum):
    need(type(value) is int and minimum <= value <= maximum, 'finite integer')
    return value


def timing_jobs():
    names = set()
    for comparison, arms in [('provider', ['native-on', 'fflate-on']), ('profile', ['fflate-on', 'fflate-off'])]:
        for case in range(30):
            for repetition in range(3):
                for arm in arms:
                    names.add('timing-' + comparison + '-c' + str(case) + '-r' + str(repetition) + '-' + arm)
    need(len(names) == 360, 'complete original timing schedule')
    return names


def scopes(root, phase, quiet, refs, now_ms):
    need(root['schemaVersion'] == 1 and root['state'] == 'ROOT_REVIEWED_ZLIB_COST_PILOT_TIMING_PHASE_V1', 'genuine V5 Root wire')
    need(root['phase'] == 'timing' and root['sourceIndexSha256'] == SOURCE_SHA and root['actionAllowed'] is True, 'new timing-only source authority')
    need(root['preparedPlan'] == refs['preparedPlan'] and root['sourceIndependentReview'] == refs['sourcePeer'], 'actual V5 plan/source peer')
    need(root['independentPreparedPlanReview'] == refs['planReview'], 'actual fresh V5 plan peer')
    need(root['calibrationSourceIndex'] == refs['originalCalibrationSource'] and root['calibrationSourceIndex']['sha256'] == PILOT_SHA, 'original B5 calibration source')
    need(root['warmNPlan'] == refs['pilotReview'] and root['warmNMatchedPlan'] == refs['matchedPlan'] and root['calibrationDecisionSha256'] == DECISION, 'actual B5 review/matched plan')
    need(root['outputRoot'] == TIMING_OUT and root['externalOutputRoot'] == EXTERNAL_OUT and root['externalParentDeadlineSeconds'] == 7200, 'fresh fixed outputs and external cap')
    need(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', root['runId']) is not None, 'finite run id')
    budget = integer(root['globalBudgetMs'], 1, 5400000)
    for key in ['operationalAdmission', 'runtimeAcceptanceClaim', 'metadataProjection', 'controlSubtraction', 'sourcePromotionAllowed']:
        need(root[key] is False, 'closed scope ' + key)
    need(phase['schemaVersion'] == 1 and phase['state'] == 'ROOT_APPROVED_BOUNDED_CODEC_MEASUREMENT_PHASE_V1' and phase['actionAllowed'] is True, 'separate new Root phase')
    for key in ['sourceIndexSha256', 'phase', 'runId', 'globalBudgetMs', 'calibrationSourceIndex', 'preparedPlan', 'quietWindowAuthority', 'warmNPlan', 'warmNMatchedPlan']:
        need(phase[key] == root[key], 'phase cross-binding ' + key)
    need(quiet['schemaVersion'] == 1 and quiet['state'] == 'ROOT_COORDINATED_CODEC_MEASUREMENT_QUIET_WINDOW_V1' and quiet['exclusiveMeasurementApproved'] is True, 'separate Root-coordinated quiet window')
    for key in ['sourceIndexSha256', 'phase', 'runId']:
        need(quiet[key] == root[key], 'quiet-window cross-binding ' + key)
    need(quiet['competingAgentWorkStopped'] is True and quiet['rootOtherBuildRuntimeOrHashAuditsStopped'] is True, 'Root explicitly confirms task idle coordination')
    need(quiet['backgroundDesktopAndSystemActivityControlled'] is False, 'no background-system isolation claim')
    def instant(text):
        need(isinstance(text, str) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z', text), 'canonical millisecond UTC')
        value = datetime.datetime.fromisoformat(text[:-1] + '+00:00')
        delta = value - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
        return delta.days * 86400000 + delta.seconds * 1000 + delta.microseconds // 1000
    start, end = instant(quiet['startsAtUtc']), instant(quiet['expiresAtUtc'])
    need(start <= now_ms < end and 0 < end - start <= 86400000 and end - now_ms >= budget, 'active window fits full selected phase budget')
    return True


def clean_terminal(value):
    need(value['rawExitCode'] == 0 and type(value['rawExitCode']) is int, 'actual parent raw zero')
    need(value['parentOwnedGroupGone'] is value['allObservedOwnedGroupsGone'] is True, 'all observed owned groups gone')
    need(value['timeout'] is value['forcedCleanup'] is False, 'no timeout or forced-cleanup acceptance')
    for key in ['signals', 'errors', 'interruptedSignals', 'remainingObservedPids']:
        need(value[key] == [], 'clean terminal ' + key)
    need(value['finalGroups'] and all(g['alive'] is False for g in value['finalGroups']), 'all final groups gone')
    return True


def publication_lines(raw):
    need(type(raw) is bytes and len(raw) <= 8 * 1024 * 1024, 'bounded full parent stdout; never clip')
    need(raw.endswith(b'\n'), 'complete JSONL terminator')
    lines = raw.decode('utf8', errors='strict').splitlines()
    need(0 < len(lines) <= 10000 and all(0 < len(line.encode('utf8')) <= 65536 for line in lines), 'finite complete JSONL records')
    values = [strict_json(line) for line in lines]
    final = values[-1]
    need(type(final) is dict and set(final) == {'index', 'completion'}, 'one final relative publication record')
    for key, name in [('index', 'index.json'), ('completion', 'completion.json')]:
        r = final[key]
        need(type(r) is dict and set(r) == {'path', 'sha256', 'bytes'} and r['path'] == name, 'exact original relative publication row')
        need(type(r['sha256']) is str and re.fullmatch('[a-f0-9]{64}', r['sha256']), 'publication digest')
        integer(r['bytes'], 1, 32 * 1024 * 1024)
    for value in values[:-1]:
        need(type(value) is dict and set(value) == {'event', 'name', 'elapsedMs', 'stdoutBytes', 'stderrBytes', 'partialObservationOnly'}, 'only actual operational heartbeat prefix')
        need(value['event'] == 'codec-phase-operational-heartbeat' and value['name'] in timing_jobs() and value['partialObservationOnly'] is True, 'heartbeat is not workload acceptance')
        for key in ['elapsedMs', 'stdoutBytes', 'stderrBytes']:
            integer(value[key], 0, 7200000 if key == 'elapsedMs' else 1048576)
    return values[:-1], final


def environment(source):
    blocked = {'PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH'}
    result = {k: v for k, v in source.items() if not k.startswith(('NODE_COMPAT_', 'NAPI_RS_', 'DYLD_')) and k not in blocked}
    result.update(PYTHONDONTWRITEBYTECODE='1', BINARYEN_CORES='1', RAYON_NUM_THREADS='1', CARGO_BUILD_JOBS='1', NODE_COMPAT_TOOLCHAIN='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain', NODE_COMPAT_COMPONENTIZE_MODULE='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/packager/src/componentize.js')
    return result
