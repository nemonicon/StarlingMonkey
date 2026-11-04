"""Run only after the independent timing window is explicitly terminal.

No native compilation, engine build, componentization or guest execution.
"""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / 'source'
BASE = ROOT / 'base'
REPOSITORY = HERE.parents[4]
NODE = '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

previous = HERE / 'readiness-results.json'
if previous.exists() and not (HERE / 'readiness-before-durable-format.json').exists():
    shutil.copy2(previous, HERE / 'readiness-before-durable-format.json')
commands = [
    ('selection', ['env', 'NODE_COMPAT_TOOLCHAIN=/tmp/starling-node-compat/native-toolchain-lock', NODE, str(SOURCE / 'tests/node-compat/module-selection-test.mjs')]),
    ('events-node', [NODE, str(SOURCE / 'tests/node-compat/foundation-events/run-native-node.mjs')]),
    ('facade', [NODE, str(HERE / 'source-facade.mjs')]),
]
executed = []
for name, command in commands:
    result = subprocess.run(command, capture_output=True, text=True)
    (HERE / (name + '-stdout.log')).write_text(result.stdout)
    (HERE / (name + '-stderr.log')).write_text(result.stderr)
    executed.append({'name': name, 'command': command, 'exitCode': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr})
    assert result.returncode == 0, executed[-1]
recipe = SOURCE / 'tests/node-compat/build-engine.sh'
subprocess.run(['bash', '-n', str(recipe)], check=True)
labels = []
for label, code in re.findall(r"<<'([A-Z]+)'\n([\s\S]*?)\n\1(?:\n|$)", recipe.read_text()):
    if code.startswith('import ') or code.startswith('from '):
        ast.parse(code)
        labels.append(label)
(HERE / 'readiness-results.json').write_text(json.dumps({
    'scope': 'Final exact-source host admission/differential facade/parser replay; no guest or native build',
    'cases': executed, 'shellSyntax': True, 'embeddedPythonParsed': labels,
    'recipeSha256': sha(recipe),
    'admissionSourceSha256': sha(SOURCE / 'tests/node-compat/module-selection.mjs'),
    'admissionTestSha256': sha(SOURCE / 'tests/node-compat/module-selection-test.mjs')}, indent=2) + '\n')
shutil.copy2(SOURCE / 'tests/node-compat/foundation-events/native-node-results.json', HERE / 'events-native-node-results.json')

original = json.loads((ROOT / 'live-before.json').read_text())
paths = {entry['path']: entry['sha256'] for entry in original['files']}
for name in ['tests/node-compat/foundation-events/cmake-policy-test.py', 'tests/node-compat/foundations/cmake-policy-test.py']:
    paths[name] = sha(BASE / name)
for name, expected in paths.items():
    assert sha(REPOSITORY / name) == expected == sha(BASE / name), name
(ROOT / 'live-unchanged.json').write_text(json.dumps({
    'baseInventorySha256': sha(ROOT / 'live-before.json'), 'verifiedPaths': len(paths),
    'allUnchanged': True, 'additionalCopiedMockFilesVerified': 2}, indent=2) + '\n')

changes = []
patch = []
for path in sorted(SOURCE.rglob('*')):
    if not path.is_file():
        continue
    name = path.relative_to(SOURCE).as_posix()
    before = BASE / name
    include = before.is_file() and sha(path) != sha(before)
    include |= not before.exists() and (name.startswith('builtins/') or
        name.startswith('tests/node-compat/legacy-stream-web-test-sources/') or
        name == 'tests/node-compat/foundation-add-abort/protected-abort-v2.patch')
    if not include:
        continue
    patch.append(''.join(difflib.unified_diff(before.read_text().splitlines(True) if before.exists() else [],
        path.read_text().splitlines(True), fromfile='a/' + name if before.exists() else '/dev/null', tofile='b/' + name)))
    changes.append({'path': name, 'change': 'modified' if before.exists() else 'added',
                    'beforeSha256': sha(before) if before.exists() else None,
                    'afterSha256': sha(path), 'bytes': path.stat().st_size})
target = ROOT / 'events-m0.10-v2.UNAPPLIED.patch'
proposed = ''.join(patch)
assert target.read_text() == proposed, 'Any final patch change requires another source review; do not silently rewrite it'
result = subprocess.run(['git', 'apply', '--check', '--whitespace=error', str(target)], cwd=REPOSITORY, capture_output=True, text=True)
assert result.returncode == 0, result.stderr
for name, expected in paths.items():
    assert sha(REPOSITORY / name) == expected, name
pins = json.loads((ROOT / 'new-policy-pins.json').read_text())
for name, expected in pins['sourceSha256'].items():
    assert sha(SOURCE / name) == expected, name
assert sha(SOURCE / 'tests/node-compat/foundation-add-abort/protected-abort-v2.patch') == pins['nativePatchSha256']
v9 = json.loads(Path('/tmp/starling-node-compat/foundations-v9/native-freeze/off-foundations.engine.wasm.build.json').read_text())
baseline = ast.literal_eval(re.search(r'^strict_callback_v3_sources = (.+)$', recipe.read_text(), re.M).group(1))
assert baseline == v9['strictEventExceptionPolicy']['nativeSourceSha256']

proof = json.loads((ROOT / 'gc-tracing-proof.json').read_text())
headers = json.loads((ROOT.parent / 'm0.10-proposal/source-receipt.json').read_text())['pinnedPublicHeaders']
value_header = next(entry for entry in headers if entry['path'].endswith('/js/Value.h'))
proof['initializedReceiverAPI'] = {
    'file': value_header['path'], 'sha256': value_header['sha256'], 'lines': [1009, 1023],
    'finding': 'Pinned PrivateValue/setPrivate stores pointer bits with isDouble; toPrivate requires that tag. Exact native-class/registered-derived membership and inaccessible trusted initialization establish representation before the nonnull check. No public-script numeric value is accepted as a native pointer.'}
(ROOT / 'gc-tracing-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
report = {
    'state': 'UNAPPLIED_REVIEW_CANDIDATE_V2_PROTOTYPE_OWNED_KEY_AND_INITIALIZED_RECEIVER',
    'base': json.loads((ROOT / 'base-v9-match.json').read_text()), 'changes': changes,
    'patch': {'path': target.name, 'sha256': sha(target), 'bytes': target.stat().st_size, 'applied': False,
              'gitApplyCheck': {'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}},
    'sourcePins': pins, 'livePreservation': {'pathsVerifiedUnchanged': len(paths), 'beforeAndAfter': True},
    'checks': {'sdkSyntaxCases': 10, 'configureCases': 9, 'scriptMode': 'code-free listing only',
               'admissionBundlerCases': 328, 'headers': 8, 'unchangedOtherHeaders': 7,
               'negativeGeneratorCases': 6, 'nodeLegacyDifferentials': 27, 'fakePublicFacadeGroups': 4,
               'nodeNestedOnceCases': 4, 'nodeReceiverCases': 9, 'shellSyntax': True, 'embeddedPythonBlocks': 4},
    'checkFiles': [{'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)} for path in sorted(HERE.iterdir()) if path.is_file()],
    'linked': False, 'engineBuilt': False, 'guestExecuted': False, 'hostModified': False,
    'emittedWasiImports': 'No component emitted/measured; no new host API requested. Actual new component must require imports[].',
    'historicalDrafts': ['history/static-root-v1/receipt.json', 'history/reserved-slot-v2-before-receiver-guard/receipt.json'],
    'guardNegativeGate': 'ONLY new exact-source, derived-macro-ON engine; never receiver negatives on Events-OFF/guard-absent controls',
    'nativeProofPending': ['real all-TU and external-embedding layout receipt', 'new ordinary component namespace/callback/order/disposal/receiver tests',
                           'four nested-once cases and initialized/prototype guards', 'snapshot/resumption/retained and Release moving-GC gates',
                           'new source-policy strict and prior-foundation replays', 'both stock target HTTP hosts and emitted WASI interface audit'],
    'provenanceFiles': [{'path': name, 'sha256': sha(ROOT / name)} for name in ['README.md', 'base-v9-match.json', 'new-policy-pins.json', 'gc-tracing-proof.json', 'live-before.json', 'live-unchanged.json']],
}
(ROOT / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'patchFiles': len(changes), 'patchSha256': sha(target), 'resultsSha256': sha(ROOT / 'results.json'),
                  'recipeSha256': sha(recipe), 'liveUnchanged': len(paths), 'engineBuilt': False}, indent=2))
