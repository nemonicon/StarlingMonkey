"""Read-only exact current passed ordinary Release corpus inventory; never reruns it."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import stat
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ROOT = Path('/tmp/starling-node-compat/foundation-scheduler-v4/ordinary-release-components-v1')
REPORT = ROOT / 'results.json'
VERIFICATION = REPO / 'tests/node-compat/foundation-scheduler/ordinary-release-verification-v1/results.json'


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


assert sha(REPORT) == 'c865931b5e5573f036d9386517d8b3720224ab80baf27b521cda87860e056161'
report = json.loads(REPORT.read_bytes())
verification = json.loads(VERIFICATION.read_bytes())
assert report['state'] == 'private-diagnostic-ordinary-components-passed'
assert verification['state'] == 'INDEPENDENT_READ_ONLY_ORDINARY_RELEASE_DIAGNOSTIC_VERIFICATION_PASSED'
assert verification['sourceReportSha256'] == sha(REPORT)
assert verification['gcStress'] is False and verification['oomTesting'] is False
assert len(report['artifacts']) == len(verification['artifacts']) == 10
verified = {row['name']: row for row in verification['artifacts']}
selected = {}
for artifact in report['artifacts']:
    component = Path(artifact['componentPath'])
    module = Path(artifact['modulePath'])
    assert component.parent == module.parent == ROOT
    assert not component.is_symlink() and not module.is_symlink()
    assert sha(component) == artifact['componentSha256'] == verified[artifact['name']]['componentSha256']
    assert artifact['interfaceAudit']['emittedImports'] == []
    assert hashlib.sha256(artifact['emittedWit'].encode()).hexdigest() == verified[artifact['name']]['recordedWitSha256']
    expected_wit = ('package root:component; world root { export inspect-result: func() -> string; export api: interface { run: func() -> string; } }'
                    if artifact['name'] == 'late' else 'package root:component; world root { export run: func() -> string; }')
    assert re.sub(r'\s+', ' ', artifact['emittedWit']).strip() == expected_wit
    source = Path(artifact['sourcePath'])
    assert sha(source) == artifact['sourceSha256']
    selected[str(component)] = {'kind': 'passed reported component', 'artifactName': artifact['name'],
                                'componentSha256': artifact['componentSha256']}
    js = module.read_text()
    dependencies = re.findall(r"new URL\(['\"](\./[^'\"]+\.core\d*\.wasm)['\"],\s*import\.meta\.url\)", js)
    assert len(dependencies) == len(set(dependencies)) == 1
    for relative in dependencies:
        core = ROOT / relative[2:]
        assert core.parent == ROOT and not core.is_symlink()
        selected[str(core)] = {'kind': 'transpiled core directly referenced by reported Jco module',
                              'artifactName': artifact['name'], 'componentPath': str(component),
                              'componentSha256': artifact['componentSha256'],
                              'modulePath': str(module), 'moduleSha256': sha(module)}
assert len(selected) == 20
rows = []
for name, proof in sorted(selected.items()):
    path = Path(name)
    before = path.lstat()
    assert path.parent == ROOT and stat.S_ISREG(before.st_mode) and not path.is_symlink()
    assert before.st_flags == 0 and before.st_nlink == 1 and before.st_blocks * 512 > 4 * 1024**2
    digest = sha(path)
    attrs = {}
    for key in subprocess.check_output(['/usr/bin/xattr', str(path)], text=True).splitlines():
        attrs[key] = hashlib.sha256(bytes.fromhex(subprocess.check_output(['/usr/bin/xattr', '-p', '-x', key, str(path)], text=True))).hexdigest()
    acl = subprocess.check_output(['/bin/ls', '-led', str(path)], text=True).splitlines()[1:]
    after = path.lstat()
    assert (after.st_ino, after.st_size, after.st_mtime_ns, after.st_flags, after.st_nlink) == (before.st_ino, before.st_size, before.st_mtime_ns, before.st_flags, before.st_nlink)
    rows.append({'path': name, 'root': str(ROOT), 'sha256': digest, 'device': before.st_dev,
                 'inode': before.st_ino, 'logicalBytes': before.st_size, 'allocatedBytes': before.st_blocks * 512,
                 'mode': stat.S_IMODE(before.st_mode), 'uid': before.st_uid, 'gid': before.st_gid,
                 'mtimeNs': before.st_mtime_ns, 'flags': before.st_flags, 'nlink': before.st_nlink,
                 'xattrDigests': attrs, 'acl': acl, 'binding': proof})
lsof = subprocess.run(['/usr/sbin/lsof', '-nP', '--', *sorted(selected)], capture_output=True, text=True)
assert lsof.returncode in [0, 1]
ps = subprocess.run(['ps', '-axo', 'pid=,ppid=,pgid=,etime=,stat=,args='], capture_output=True, text=True)
assert ps.returncode == 0
task = []
for line in ps.stdout.splitlines():
    parts = line.strip().split(None, 5)
    if len(parts) != 6 or int(parts[0]) in [os.getpid(), os.getppid()]:
        continue
    command = parts[5]
    exe = Path(command.split(None, 1)[0]).name
    if ('starling-node-compat' in command or '/StarlingMonkey/tests/node-compat/' in command) and exe in ['ninja', 'cmake', 'clang', 'clang++', 'cargo', 'rustc', 'wasmtime', 'wash', 'wizer', 'node', 'python3', 'bash', 'zsh']:
        task.append({'pid': int(parts[0]), 'executable': exe, 'command': command})
result = {'state': 'READ_ONLY_EXACT_PASSED_CURRENT_ORDINARY_RELEASE_CORPUS_CAPACITY_AUDIT',
          'atUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sourceReport': {'path': str(REPORT), 'sha256': sha(REPORT)},
          'independentVerification': {'path': str(VERIFICATION), 'sha256': sha(VERIFICATION)},
          'scope': 'Exactly the newly authorized ten passed ordinary Release typed-string artifacts and their ten directly referenced Jco cores; not any other/private-old/debug/OOM/unsafe corpus.',
          'artifactCount': 10, 'coreDependencyCount': 10, 'files': rows,
          'allocatedBytes': sum(row['allocatedBytes'] for row in rows), 'logicalBytes': sum(row['logicalBytes'] for row in rows),
          'largestOneFileTemporaryLogicalBytes': max(row['logicalBytes'] for row in rows),
          'lsof': {'status': lsof.returncode, 'stdout': lsof.stdout, 'stderr': lsof.stderr,
                   'exactPaths': 20, 'noOpensObserved': lsof.returncode == 1 and not lsof.stdout and not lsof.stderr},
          'ps': {'status': ps.returncode, 'stderr': ps.stderr, 'taskTaggedProcesses': task},
          'compressionRecoveryMeasured': False, 'compatibilityPromotionClaim': False,
          'binaryReadAsDataOnly': True, 'compressionDeletionBuildGuestOrCorpusRerunExecuted': False}
with (HERE / 'results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
with (HERE / 'index.json').open('x') as stream:
    json.dump({'state': 'READ_ONLY_CURRENT_RELEASE_CORPUS_INVENTORY_FROZEN',
               'files': [{'path': name, 'sha256': sha(HERE / name), 'bytes': (HERE / name).stat().st_size}
                         for name in ['audit.py', 'results.json']],
               'compressionDeletionBuildOrGuestExecuted': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'reportSha256': sha(HERE / 'results.json'), 'indexSha256': sha(HERE / 'index.json'),
                  'files': len(rows), 'allocatedBytes': result['allocatedBytes'],
                  'lsofStatus': lsof.returncode, 'lsofStderr': lsof.stderr, 'taskMatches': task}))
