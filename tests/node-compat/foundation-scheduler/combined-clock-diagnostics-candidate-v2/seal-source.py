"""Seal uncompiled Source and synthetic evidence only. No native entry imports."""
from pathlib import Path
import ast, hashlib, json

OWN = Path(__file__).resolve().parent
assert not (OWN / 'index.json').exists(), 'sealed families remain immutable'

def read(name):
    return json.loads((OWN / name).read_bytes())

def descriptor(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            digest.update(chunk)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=path.stat().st_size)

def save(name, value):
    (OWN / name).write_text(json.dumps(value, indent=2) + '\n')

checks = read('source-check-results.json')
inventory = read('proposed-source-inventory.json')
derivations = read('derivations.json')
refs = read('references.json')
assert checks['state'] == 'PRIVATE_DIAGNOSTIC_V2_SOURCE_DATA_MODELS_PASSED'
assert checks['pureModels']['checks'] == 72 and checks['hostCommands'] == 4
for role in ['models', 'collector-grammar', 'models-grammar', 'fixture-grammar']:
    terminal = read('evidence/' + role + '.terminal.json')
    assert terminal['rawExitCode'] == 0 and terminal['stderr']['bytes'] == 0
    for name in ['stdout', 'stderr']:
        assert descriptor(terminal[name]['path']) == terminal[name]
for row in read('input-hashes.json')['files']:
    assert descriptor(row['path']) == row
for row in derivations['files']:
    assert descriptor(row['before']['path']) == row['before']
    assert descriptor(row['after']['path']) == row['after']
for path in OWN.glob('*.py'):
    ast.parse(path.read_bytes(), filename=str(path))
assert inventory['proposedNativeFiles'] == 357
assert inventory['retainedParentNativeFiles'] == 349
assert inventory['nativeAfterimages'] == 6 and len(inventory['newNativePaths']) == 2
assert inventory['externalEmbeddingSources'] == 3 and inventory['externalAfterimages'] == 1
assert not inventory['compiled']
assert all(value is None for name, value in read('future-gates.json').items()
           if name not in ['schemaVersion', 'state'])

save('preparation-history.json', dict(
    schemaVersion=1, state='SEALED_UNCOMPILED_PRIVATE_DIAGNOSTIC_V2_SOURCE',
    parentDiagnosticIndex=refs['parentDiagnosticSourceIndex'],
    fixtureSourceIndex=refs['diagnosticFixtureSourceIndex'],
    fixtureSourcePeerIndex=refs['diagnosticFixtureSourcePeerIndex'],
    sourceCheck=descriptor(OWN / 'source-check-results.json'),
    compilerInvoked=False, nativeOrHelperOrFixtureOrClockAction=False,
    sourcePeer=None, rootAuthority=None, nativeBuild=None, runtime=None))

save('results.json', dict(
    schemaVersion=1, state='UNCOMPILED_COMBINED_CLOCK_DIAGNOSTICS_SOURCE_PREPARED_V2',
    sourceOnly=True, sourcePreparationPassed=True,
    parentDiagnosticSourceIndexSha256=refs['parentDiagnosticSourceIndex']['sha256'],
    parentNativeSourceFiles=inventory['parentNativeFiles'],
    proposedNativeSourceFiles=inventory['proposedNativeFiles'],
    retainedParentNativeFiles=inventory['retainedParentNativeFiles'],
    nativeAfterimages=inventory['nativeAfterimages'], newNativePaths=len(inventory['newNativePaths']),
    externalEmbeddingSources=inventory['externalEmbeddingSources'],
    externalEmbeddingAfterimages=inventory['externalAfterimages'],
    fullWholeParentSourcesAuthenticated=True, parentRawMetadataFieldCount=80,
    newMetadataProduced=False, proposedMetadataFieldCount=None,
    reversibleFileDerivations=len(derivations['files']),
    changedDerivations=sum(bool(row['edits']) for row in derivations['files']),
    sourceChecks=checks['checks'], syntheticCollectorChecks=checks['pureModels']['checks'],
    directOriginalInputs=checks['directOriginalInputs'], fullSourceFamilies=checks['fullSourceFamilies'],
    hostModelCommands=1, hostGrammarCommands=3,
    privateModule='starling:test-clock-lifecycle',
    privateMethods=['snapshot', 'clockStateV2', 'probeAllInvalidV2'],
    defaultOff=True, maxSelectorTasks=8, maxTimerLeaseRows=512,
    incompleteOrOverflowRejected=True,
    actualEngineQueueProbeImplementedInSource=True, selectorOnly=True,
    naturalEventLoopSettlementProved=False, hostPollableCreatedByProbe=False,
    sameTuOffsetAccessorImplementedInSource=True,
    sameTuPerformanceOriginAccessorImplementedInSource=True,
    embeddingObservationHooksImplementedInSource=True,
    nativeClockCallsAdded=0, clockTupleIsLastObservationNotCompleteTrace=True,
    strongGetterAndInlineStateLinkedIdentityProved=False,
    cppSyntaxChecked=False, nativeLinked=False, newProducerOrAdmissionImplemented=False,
    privateBundleOrComponentAdmissionImplemented=False,
    hostStoreDeathObserved=False, cachedImmediateTeardownObserved=False,
    fatalPostTrapCleanupObserved=False, fullLifecycleGateAccepted=False,
    ownerActionsInvoked=False, compilerInvoked=False, nativeProbeInvoked=False,
    nativeClockRead=False, fixtureOrGuestExecuted=False, engineExecuted=False,
    gcDebugOomFaultResetOrCryptoAction=False, publicProfilePromotion=False,
    independentSourceReview=None, rootAuthority=None, actualNativeArtifact=None,
    actualRuntimeProof=None,
    limitations=[
        'Uncompiled source: no ABI, link, shared inline-state, bundle or runtime proof.',
        'Synchronous actual-queue selector observation is separate from natural-loop settlement and interest teardown.',
        'Sentinels own no JS edges or pollables; destruction counts are not timer-resource or host Store accounting.',
        'Void enqueue remains an existing fatal allocation seam; no recoverable OOM or fault testing claim.',
        'Last native offset/wizen tuple and origin units do not establish a host epoch or cross-clock relationship.',
        'A future producer must propagate the diagnostic define to the separate embedding compilation.',
        'All seventeen lifecycle gates remain required; snapshot/host Store/fatal teardown cannot be inferred.',
    ]))
save('source-receipt.json', dict(
    schemaVersion=1, sourceOnly=True, result=descriptor(OWN / 'results.json'),
    inputHashes=descriptor(OWN / 'input-hashes.json'),
    sourceInventory=descriptor(OWN / 'proposed-source-inventory.json'),
    derivations=descriptor(OWN / 'derivations.json'),
    proposedPolicy=descriptor(OWN / 'proposed-policy.json'),
    references=descriptor(OWN / 'references.json'),
    sourceCheck=descriptor(OWN / 'source-check-results.json'),
    futureSourceContract=descriptor(OWN / 'future-source-review-contract.json'),
    compilerOrNativeOrGuestOrClockAction=False, independentSourceReview=None,
    scope='Finite source afterimages, full actual355+3 ancestry, three complete compact Source families, pure models and host grammar. No historical proof-tree copies.'))

rows = []
for path in sorted(OWN.rglob('*')):
    assert not path.is_symlink()
    if path.is_file():
        row = descriptor(path)
        row['path'] = path.relative_to(OWN).as_posix()
        rows.append(row)
save('index.json', dict(
    schemaVersion=1,
    state='SEALED_UNCOMPILED_PRIVATE_DIAGNOSTIC_SOURCE_NO_NATIVE_OR_ACTION_AUTHORITY_V2',
    files=rows))
assert {row['path'] for row in rows} | {'index.json'} == {
    path.relative_to(OWN).as_posix() for path in OWN.rglob('*') if path.is_file()}
for name in ['index.json', 'results.json', 'source-receipt.json']:
    print(json.dumps(descriptor(OWN / name)))
