"""Launch one separately declared extra-CDP-off sample, never the next sample."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
FRAMEWORK = HERE.parent
REPO = FRAMEWORK.parents[3]
STOCK = FRAMEWORK / 'browser-hydration-matched-host-candidate-v5'
MINIMUM = 1073741824
ORDER = ['off1', 'off2', 'off3']
PYTHON = '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'
UTILITY = dict(path=str(FRAMEWORK / 'next-browser-reliability-root-results-v1/launch-member.py'),
               sha256='e93fe0ec068c9a8e61ca69eb9f90dd9a53d5d8a52e0603f5d3fa72b163cfae9d', bytes=15760)
PINS = {
    str(STOCK / 'index.json'): ('de7f0b14e67cd7afa3a645d743da71d97024fdc733b53769d10e6232fae5b218', 5224),
    str(STOCK / 'plans.json'): ('a7a4c26b067fb38529b4e4257a0a371b038e867e584ada1e027284a0df8c59c3', 19976),
    str(STOCK / 'run-owned.py'): ('dc92276e9ec2a94e8f2a52fd298f108fc1e47b8c32d4704fc9a40ed8274346d2', 4846),
    str(STOCK / 'run-stock.mjs'): ('bbfddd06b8e96a7ce73125fdb1a4c497e5478f564c44ca906dc0202aa3ecc307', 16092),
    str(FRAMEWORK / 'browser-extra-cdp-off-candidate-v1/index.json'): ('f73c2434d426f0585b0e680a67533851a6727df2d28e83671ff408463f5940e9', 3413),
    UTILITY['path']: (UTILITY['sha256'], UTILITY['bytes']),
    PYTHON: ('4a81cbef89c3cded9c9435c2faf747823dfed9ca9a0da82df374834a18c70dc8', 102352),
}
PREREQUISITES = [
    dict(path=str(FRAMEWORK / 'next-browser-reliability-root-results-v1/cohort-review/index.json'),
         sha256='d9ffd359fab79c31f2666f953104901162a3aaf31cd24fc8a1de7790074b6290', bytes=2008),
    dict(path=str(FRAMEWORK / 'direct-standalone-control-root-results-v1/actual-review/index.json'),
         sha256='8b85ab6dd209488869ec9205074e8120a7804c9d7507ba2b05a812950d2ce049', bytes=1715),
]


def load_utility():
    # Authenticate the original inert utility before executing its definitions.
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B without -O, including read-only audits')
    path = Path(UTILITY['path'])
    assert path.resolve() == path and not any(p.is_symlink() for p in (path, *path.parents))
    assert path.is_file() and path.stat().st_nlink == 1
    data = path.read_bytes()
    assert len(data) == UTILITY['bytes'] and hashlib.sha256(data).hexdigest() == UTILITY['sha256']
    spec = importlib.util.spec_from_file_location('held_browser_cohort_utilities', path)
    utility = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utility)  # main is not called; no globals are rebound.
    return utility


def pin(path):
    sha, size = PINS[str(path)]
    return dict(path=str(path), sha256=sha, bytes=size)


def load_owner(utility):
    utility.family(pin(STOCK / 'index.json'))
    utility.verify(pin(STOCK / 'run-owned.py'))
    spec = importlib.util.spec_from_file_location('held_extra_cdp_stock_owner', STOCK / 'run-owned.py')
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)  # Only use its genuine pure derive_invocation.
    return owner


def member_layout(member, authority, plan, derive, utility):
    utility.safe_id(member['id'])
    utility.safe_id(member['runId'])
    assert member['arm'] == 'stock' and member['worldGuardReceipt'] is None
    assert type(authority['schemaVersion']) is int and authority['schemaVersion'] == 1
    assert authority['runId'] == member['runId'] and authority['rootLaunchMinimumFreeBytes'] == MINIMUM
    assert authority['sourceIndex'] == pin(STOCK / 'index.json') and authority['plans'] == pin(STOCK / 'plans.json')
    assert authority['localhostServerAllowed'] is authority['browserAllowed'] is True
    for key in ['compilerAllowed', 'nativeBuildAllowed', 'guestAllowed', 'engineAllowed', 'externalApplicationDeploymentAllowed']:
        assert authority[key] is False
    assert authority['unissued'] is False
    output, monitor, _ = derive(authority, plan, STOCK)
    assert member['cwd'] == str(REPO)
    assert member['argv'] == [PYTHON, '-I', '-B', str(STOCK / 'run-owned.py'), 'stock', member['authority']['path']]
    assert member['outputRoot'] == str(output) and member['monitorOutputRoot'] == str(monitor)
    assert member['observation'] == str(monitor / 'observation.json')
    for value in [str(output), str(monitor), member['observation']]:
        utility.canonical(value)


def validate_protocol(protocol, self_ref, utility, derive, fetch):
    assert protocol['state'] == 'ROOT_EXTRA_CDP_OFF_DIAGNOSTIC_DECLARED_V1'
    assert protocol['driver'] == self_ref and protocol['utility'] == UTILITY
    assert type(protocol['minimumFreeBytes']) is int and protocol['minimumFreeBytes'] == MINIMUM
    assert protocol['prerequisiteReviewIndexes'] == PREREQUISITES
    members = protocol['members']
    assert [m['id'] for m in members] == ORDER and all(m['arm'] == 'stock' for m in members)
    assert len({m['runId'] for m in members}) == 3
    shared = protocol['sharedInputs']
    assert len({r['path'] for r in shared}) == len(shared)
    for path in PINS:
        assert pin(path) in shared, 'Missing held actor/tool: ' + path
    destinations = []
    for member in members:
        authority = fetch(member['authority'])
        plan = fetch(authority['plans'])
        member_layout(member, authority, plan, derive, utility)
        destinations.extend([member['outputRoot'], member['monitorOutputRoot']])
    assert len(destinations) == len(set(destinations)), 'Sample namespaces overlap'
    return members


def protect(protocol_ref, self_ref, utility, derive):
    protocol = utility.read(protocol_ref)
    utility.verify(self_ref)
    members = validate_protocol(protocol, self_ref, utility, derive, utility.read)
    for ref in protocol['prerequisiteReviewIndexes']:
        utility.family(ref)  # The exact negative cohort is allowed, not relabeled.
    for ref in protocol['sharedInputs']:
        utility.verify(ref)
    utility.family(pin(STOCK / 'index.json'))
    utility.family(pin(FRAMEWORK / 'browser-extra-cdp-off-candidate-v1/index.json'))
    return members


def prior_cli_status(member, protocol_ref, self_ref, admission, completion, code):
    assert admission['state'] == 'EXTRA_CDP_OFF_SINGLE_MEMBER_ADMITTED_V1'
    assert admission['protocol'] == protocol_ref and admission['driver'] == self_ref and admission['utility'] == UTILITY
    assert admission['member'] == member and admission['oneCommandOnly'] is True and admission['automaticNextOrRetry'] is False
    assert completion['state'] == 'EXTRA_CDP_OFF_SINGLE_CLI_RETURN_CAPTURED_V1' and completion['memberId'] == member['id']
    assert completion['error'] is None and completion['registrySharedAndPriorRecordsPreserved'] is True
    assert completion['postProtectionError'] is None
    assert completion['automaticNextOrRetry'] is False and completion['functionalPassNotInferred'] is True
    assert type(completion['rawCliExitCode']) is int and completion['rawCliExitCode'] == code
    assert admission['originalCohortAcceptance'] is completion['originalCohortAcceptance'] is False


def prior_records(member, protocol_ref, self_ref, utility):
    refs = []
    def grab(path):
        ref = utility.row(path)
        refs.append(ref)
        return utility.read(ref)
    authority = utility.read(member['authority'])
    observation = grab(member['observation'])
    terminal = utility.read(observation['terminal'])
    result = utility.read(observation['result'])
    refs.extend([observation['terminal'], observation['result']])
    for key in ['stdout', 'stderr']:
        utility.verify(terminal[key])
        refs.append(terminal[key])
    assert observation['monitorOutputRoot'] == member['monitorOutputRoot']
    status = utility.prior_status(member, authority, observation, terminal, result, None)
    logs = HERE / (member['id'] + '-launcher')
    admission = grab(logs / 'admission.json')
    completion = grab(logs / 'cli-result.json')
    prior_cli_status(member, protocol_ref, self_ref, admission, completion, observation['rawExitCode'])
    for key, name in [('stdout', 'cli.stdout.log'), ('stderr', 'cli.stderr.log')]:
        assert completion[key]['path'] == str(logs / name)
        utility.verify(completion[key])
        refs.append(completion[key])
    return status, refs


def require_fresh(member, exists, free_bytes):
    paths = [member['outputRoot'], member['monitorOutputRoot'], str(HERE / (member['id'] + '-launcher'))]
    assert member['worldGuardReceipt'] is None
    assert not any(exists(path) for path in paths), 'Selected output/monitor/admission exists'
    assert free_bytes >= MINIMUM, 'At least 1 GiB free required before any launch write'
    return paths


def audit_completed(protocol_ref, through_id='off3'):
    """Read-only explicit final-member audit; never launches or writes anything."""
    utility = load_utility()
    self_ref = utility.row(Path(__file__).resolve())
    owner = load_owner(utility)
    members = protect(protocol_ref, self_ref, utility, owner.derive_invocation)
    end = ORDER.index(through_id)
    statuses, refs = [], []
    for member in members[:end + 1]:
        status, found = prior_records(member, protocol_ref, self_ref, utility)
        statuses.append(status)
        refs.extend(found)
    protect(protocol_ref, self_ref, utility, owner.derive_invocation)
    for ref in refs:
        utility.verify(ref)
    return statuses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--member', choices=ORDER, required=True)
    args = parser.parse_args()
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        parser.error('Use Python -I -B without -O')
    utility = load_utility()
    protocol_ref = utility.row(utility.canonical(args.protocol))
    assert protocol_ref['sha256'] == args.sha256
    self_ref = utility.row(Path(__file__).resolve())
    owner = load_owner(utility)
    members = protect(protocol_ref, self_ref, utility, owner.derive_invocation)
    selected = next(m for m in members if m['id'] == args.member)
    priors, prior_refs = [], []
    for member in members[:members.index(selected)]:
        status, refs = prior_records(member, protocol_ref, self_ref, utility)
        priors.append(status)
        prior_refs.extend(refs)
    for ref in prior_refs:
        utility.verify(ref)
    free = shutil.disk_usage(Path(selected['outputRoot']).parent).free
    require_fresh(selected, lambda value: Path(value).exists() or Path(value).is_symlink(), free)
    logs = HERE / (selected['id'] + '-launcher')
    logs.mkdir(mode=0o700)
    assert logs.stat().st_uid == os.getuid() and logs.stat().st_mode & 0o777 == 0o700
    utility.durable(logs / 'admission.json', dict(schemaVersion=1, state='EXTRA_CDP_OFF_SINGLE_MEMBER_ADMITTED_V1',
        protocol=protocol_ref, driver=self_ref, utility=UTILITY, member=selected, preceding=priors,
        precedingRecords=prior_refs, freeBytesAtAdmission=free, minimumFreeBytes=MINIMUM,
        oneCommandOnly=True, automaticNextOrRetry=False, originalCohortAcceptance=False))
    code, error, preserved = None, None, False
    out_path, err_path = logs / 'cli.stdout.log', logs / 'cli.stderr.log'
    with os.fdopen(os.open(out_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as out, \
         os.fdopen(os.open(err_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as err:
        try:
            code = subprocess.run(selected['argv'], cwd=selected['cwd'], stdout=out, stderr=err, check=False).returncode
        except BaseException as caught:
            error = dict(type=type(caught).__name__, message=str(caught))
        finally:
            out.flush(); err.flush(); os.fsync(out.fileno()); os.fsync(err.fileno())
    post_error = None
    try:
        protect(protocol_ref, self_ref, utility, owner.derive_invocation)
        for ref in prior_refs:
            utility.verify(ref)
        preserved = True
    except BaseException as caught:
        post_error = dict(type=type(caught).__name__, message=str(caught))
        error = error or post_error
    record = dict(schemaVersion=1, state='EXTRA_CDP_OFF_SINGLE_CLI_RETURN_CAPTURED_V1', memberId=selected['id'],
        rawCliExitCode=code, error=error, postProtectionError=post_error, registrySharedAndPriorRecordsPreserved=preserved,
        stdout=utility.row(out_path), stderr=utility.row(err_path), functionalPassNotInferred=True,
        automaticNextOrRetry=False, originalCohortAcceptance=False, finalMemberRequiresExplicitAudit=True)
    utility.durable(logs / 'cli-result.json', record)
    print(json.dumps(record), flush=True)
    return code if type(code) is int and code in (0, 1) and error is None and preserved else 1


if __name__ == '__main__':
    raise SystemExit(main())
