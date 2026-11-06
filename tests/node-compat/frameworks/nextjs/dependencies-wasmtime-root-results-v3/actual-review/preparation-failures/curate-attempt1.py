"""Retain existing DATA only. No process, host, component or guest invocation.

Authoring-only: refuses an already-indexed destination; do not rerun held.
"""
from pathlib import Path
import gzip, hashlib, json
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
BASE = Path('/private/tmp/starling-node-compat')
assert not (HERE/'index.json').exists()
COPIES = []
BEFORE = {}
RUNS = [
    ('als-oracle-failure', 'next-dependencies-wasmtime-v3-enginec2bff940-first3',
     'b69c7f57ac252fc9ecb62ba693b6e85a3c2e97b16b6c922b2bbc953b7e26b2ab', 4692, 1),
    ('wrapped-eof-failure', 'next-dependencies-wasmtime-v4-enginec2bff940-profile2-first',
     '27fd90203221b18b107069dcf97e4cf25cbe7dc7db0d222060c8b19f0244ebe5', 11622, 1),
    ('normal-eof-pass', 'next-dependencies-wasmtime-v4-enginec2bff940-profile3-first',
     'a90c6533e52c8fbcadaea07cf9456f7fe8aeac77abb36a94f8cb7e146d0def30', 13799, 0),
]
def descriptor(path, raw=None):
    if raw is None:
        raw = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
def checked(row):
    path = Path(row['path'])
    raw = path.read_bytes()
    assert descriptor(path, raw) == row, str(path)
    BEFORE[str(path)] = row
    return raw
def copy(path, relative):
    path = Path(path)
    row = descriptor(path)
    raw = checked(row)
    target = HERE/relative
    target.parent.mkdir(exist_ok=True, parents=True)
    assert not target.exists()
    compressed = relative.endswith('.gz')
    target.write_bytes(gzip.compress(raw, mtime=0) if compressed else raw)
    COPIES.append(dict(original=row, copy=relative,
                       compression='gzip' if compressed else 'none'))
    return relative
reviews = []
for ident, name, sha, size, exit_code in RUNS:
    root = BASE/name
    monitor = BASE/(name+'-external-root')
    row = dict(path=str(root/'result.json'), sha256=sha, bytes=size)
    result = json.loads(checked(row))
    terminal = json.loads((monitor/'terminal.json').read_bytes())
    observation = json.loads((monitor/'observation.json').read_bytes())
    assert observation['result'] == row and observation['rawExitCode'] == exit_code
    assert observation['authority'] == result['authority']
    checked(observation['terminal'])
    assert terminal['rawExitCode'] == exit_code
    for key in ('timeout', 'forcedCleanup'):
        assert terminal[key] is False
    for key in ('signals', 'interruptedSignals', 'remainingObservedPids', 'errors'):
        assert terminal[key] == []
    assert terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True
    assert observation['finalProtectionErrors'] == []
    assert observation['originalApplicationModesAndInodesPreserved'] is True
    assert observation['allOwnedClean'] is (exit_code == 0)
    assert observation['capSeconds'] == 180
    started = json.loads((monitor/'started.json').read_bytes())
    assert started['argv'] == observation['argv'] and started['timeoutSeconds'] == 180
    assert started['pid'] == terminal['pid']
    for key in ('stdout', 'stderr'):
        checked(terminal[key]); checked(result['server'][key])
    publication = [json.loads(line) for line in (monitor/'stdout.log').read_text().splitlines()]
    assert len(publication) == 1
    p = publication[0]
    assert p['state'] == result['state'] and p['passed'] == result['passed']
    assert p['requests'] == len(result['requests']) and p['errors'] == result['errors']
    server = result['server']
    assert server['exit'] == dict(code=0, signal=None, error=None)
    assert server['forcedCleanup'] is False and server['shutdownRequested'] is True and server['sigintSent'] is True
    assert result['originalInputsPreserved'] is True and result['readonlyCopyPreserved'] is True
    assert result['sameInstanceIdentityProved'] is False and result['adoption'] is False
    assert result['fullNextApplicationServed'] is False
    authority = json.loads(checked(result['authority']))
    construction = json.loads(checked(result['constructionResult']))
    assert authority['component'] == result['component'] == construction['artifacts']['component']
    for key in ('componentAudit', 'constructionResult'):
        assert authority[key] == result[key]
    plan = json.loads(checked(observation['plan']))
    for key in ('inputEntry', 'inputSourceIndex'):
        old_key = 'dependencyEntry' if key == 'inputEntry' else key
        assert (authority[key] if key in authority else plan[old_key]) == result[key]
    assert construction['artifacts']['inputEntry'] == result['inputEntry']
    assert construction['artifacts']['inputSourceIndex'] == result['inputSourceIndex']
    assert authority['engine'] == construction['artifacts']['engine']
    assert authority['nativeMetadata'] == construction['artifacts']['nativeMetadata']
    for key in ('component', 'engine', 'nativeMetadata'):
        checked(authority[key])  # authenticate originals; never copy binaries
    audit = json.loads(checked(result['componentAudit']))
    assert audit['passed'] is True and audit['component'] == result['component']
    checked(result['inputEntry']); checked(result['inputSourceIndex'])
    checked(observation['plan']); checked(observation['sourceIndex'])
    copy(root/'result.json', ident+'/result.json')
    copy(Path(result['authority']['path']), ident+'/root-authority.json')
    copy(Path(result['constructionResult']['path']), ident+'/construction-result.json')
    copy(Path(result['componentAudit']['path']), ident+'/component-audit.json')
    copy(Path(result['inputEntry']['path']), ident+'/input-entry.mjs')
    for path in sorted(monitor.iterdir()):
        assert path.is_file() and not path.is_symlink()
        copy(path, ident+'/monitor/'+path.name)
    for key in ('stdout', 'stderr'):
        copy(Path(server[key]['path']), ident+'/wasmtime.'+key+'.log')
    for request in result['requests']:
        checked(request['rawBody'])
        copy(Path(request['rawBody']['path']), ident+'/response-'+str(request['ordinal'])+'.body')
    reviews.append(dict(id=ident, originalResult=row,
                        resultCopy=ident+'/result.json', monitorCopy=ident+'/monitor',
                        sourceIndex=result['inputSourceIndex'], engine=authority['engine'],
                        component=result['component'], rawMonitorExit=exit_code,
                        statuses=[r['status'] for r in result['requests']],
                        originalMonitorGroupsGone=True, originalHostSigintExit=0,
                        sourceProtection='Retained executed runner/final monitor bookends; this curator did not repeat whole application/source-tree guards.'))
oracle = REPO/'tests/node-compat/frameworks/nextjs/next-component-candidate-v2/profile-model-results.json'
copy(oracle, 'inputs/default-node-als-profile-models.json')
copy(oracle.with_name('als-store-contract.mjs'), 'inputs/corrected-als-store-contract.mjs')
copy(REPO/'tests/node-compat/frameworks/nextjs/next-component-candidate-v3/checks.json', 'inputs/wrapped-error-source-host-checks.json')
copy(REPO/'tests/node-compat/frameworks/nextjs/next-component-candidate-v3/adapter-descendant.mjs', 'inputs/corrected-wasi-adapter.mjs')
for path, row in BEFORE.items():
    checked(row)
(HERE/'copy-map.json').write_text(json.dumps(dict(schemaVersion=1, originalsBeforeFinalUnchanged=True, files=COPIES), indent=2)+'\n')
summary = dict(schemaVersion=1, state='RETAINED_NEXT_NATIVE_DEPENDENCY_CONTROLS_REVIEW_PASSED_V1',
               readOnlyWorkloadReview=True, reviewAuthorAlsoAuthoredRunnerAndAdapter=True,
               checkedExistingDataOnly=True, reviewerWorkloadExecutions=False,
               acceptedBaseline='normal-eof-pass', canonicalControls=16, acceptedResponses=3,
               acceptedRecords=48, runs=reviews, earlierFailuresRemainUnaccepted=True,
               fullNextAccepted=False, sameInstanceIdentityProved=False,
               snapshotResetOrGcProof=False, publicAdoption=False,
               originalFilesCheckedBeforeAndFinal=len(BEFORE), binaryCopies=0,
               fullApplicationCopies=0)
(HERE/'review.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(dict(retainedCopies=len(COPIES), checkedOriginals=len(BEFORE), writesConfinedTo=str(HERE))))
