"""Seal only this independent DATA review; no operational imports or actions."""
from pathlib import Path
import ast, hashlib, json

HERE = Path(__file__).resolve().parent
K = HERE.parent
SOURCE = K / 'ownership-secret-artifact-tooling-candidate-v3'

def load(path):
    return json.loads(Path(path).read_bytes())

def row(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    b = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))

def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')

root_row = row(K / 'ownership-secret-artifact-export-v3-root-results.json')
assert root_row['sha256'] == '2295d612fd9cf585077f011090b44de719fb32f4fe5ec77d30a1d012969c621a'
root = load(root_row['path'])
refs = load(SOURCE / 'references.json')
audit = load(HERE / 'audit-results.json')
checks = load(HERE / 'checks.json')
terminal = load(HERE / 'evidence/reader-attempt1/terminal.json')
assert terminal['rawExitCode'] == 0 and terminal['stderr']['bytes'] == 0
assert audit['rootObservation'] == root_row and audit['checks'] == checks['checks'] == 31979
assert audit['rehashedLexicalPaths'] == 27962
assert audit['allSourceOriginalAndFrozenInputsCurrent'] is True
assert audit['typedWholeCandidateMatch'] is True
assert audit['noConcreteActualEvidenceBlockerFound'] is True
for key in ['stdout', 'stderr']:
    assert row(terminal[key]['path']) == terminal[key]
for name in ['reader.py', 'seal-review.py']:
    ast.parse((HERE / name).read_bytes())

result = load(SOURCE / 'future-export-review-contract.json')
assert result['schemaVersion'] == 3
assert result['state'] == 'INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_PIN_EXPORT_REVIEW_PASSED_V3'
assert {k for k, v in result.items() if v is None} == {
    'toolingSourceIndexSha256', 'candidate', 'actualProof', 'rootAuthority',
    'config', 'controllerObservation', 'externalTerminal', 'wholeVerifierFrame'}
result.update(
    toolingSourceIndexSha256=root['sourceIndex']['sha256'],
    candidate=root['candidate'], actualProof=row(HERE / 'audit-results.json'),
    rootAuthority=root['rootAuthority'], config=root['config'],
    controllerObservation=root['controllerObservation'],
    externalTerminal=root['innerTerminal'], wholeVerifierFrame=root['wholeVerifierFrame'])
result.update(
    toolingSourceIndex=root['sourceIndex'], toolingSourceReview=root['sourceReview'],
    rootObservation=root_row, rootObserverHistory=root['rootObserverHistory'],
    outerRootObservation=root['outerRootObservation'], outerTerminal=root['outerTerminal'],
    innerTerminal=root['innerTerminal'], outerRawStdout=root['outerRawStdout'],
    outerRawStderr=root['outerRawStderr'], innerRawStdout=root['innerRawStdout'],
    innerRawStderr=root['innerRawStderr'],
    historicalWholeVerifierFrame=refs['actualVerifierWholeFrame'],
    actualFrozenArtifactReview=refs['actualArtifactReview'],
    originalConfiguredSourceRoot=refs['configuredSourceRoot'],
    frozenSourceRoot=refs['frozenSourceRoot'], frozenRoot=refs['frozenRoot'],
    originalVerifierToolingRoot=refs['verifierOriginalToolingRoot'],
    inputClosure=row(HERE / 'input-hashes.json'),
    checks=row(HERE / 'checks.json'), readerTerminal=row(HERE / 'evidence/reader-attempt1/terminal.json'),
    coverage=audit['coverage'], rehashedLexicalPaths=audit['rehashedLexicalPaths'],
    logicalBytes=audit['logicalBytes'], sourceAndOriginalProtectionRechecked=True,
    wholeHelperFrameUnchanged=True, completeMetadataFields=75,
    completeSelectedManifests=11, sourceSupportedCompleteVerifierCalls=1,
    outerParentPid=86546, helperWorkerPid=86731,
    ownerActionsInvoked=False, hostActionsInvoked=False,
    exportOrBootstrapActionsInvoked=False, readHashJsonAstDataOnly=True,
    operationalEntrypointsImportedOrInvoked=False,
    actualExporterAndCompleteHelperPreviouslyExecutedByRoot=True,
    otherVariantLabels=['normal-runtime', 'gc-off', 'disabled-off'],
    reviewedPins=None, actualBootstrap=None,
    grantsBootstrapAuthority=False, grantsRuntimeAuthority=False,
    limitations=[
        'Actual export result review only. The unchanged candidate still has unreviewed state and reviewRequired:true.',
        'A later Root decision must derive reviewed validation-only pins, authenticate this proof, and issue a distinct bootstrap authority.',
        'Full metadata and manifest values remain in their original retained frame; no selected/core/module manifest projection or source-context rewriting was performed.',
        'One complete helper invocation is supported by authenticated source and one observed helper worker; this review did not instrument or rerun the helper.',
        'Cleanup findings concern all retained observed identities and groups; process sampling is not proof about unobserved processes.',
        'The enclosing Root tool exit is recorded in the Root report. No additional raw Root-tool stdout file is invented; retained outer-monitor JSONL and inner-worker JSON are independently decoded.',
        'Whole frozen payload and original/configured protections are verified separately. Referenced SDK, compiler, and library inputs are not all copied into the frozen payload.',
        'This review executes no engine, module, component, guest, key, cryptography, GC, bootstrap, exporter, monitor, or original verifier helper.'
    ])

template = load(SOURCE / 'future-export-review-contract.json')
for key, value in template.items():
    if value is not None:
        assert result[key] == value
    else:
        assert result[key] is not None
assert result['engine'] == refs['engine'] and result['metadata'] == refs['metadata']
assert result['freezeReceipt'] == refs['freezeReceipt']
write('results.json', result)

descriptor_keys = [
    'toolingSourceIndex', 'candidate', 'actualProof', 'engine', 'metadata',
    'freezeReceipt', 'nativeSourceIndex', 'freezerSourceIndex', 'verifierSourceIndex',
    'rootAuthority', 'config', 'controllerObservation', 'externalTerminal',
    'wholeVerifierFrame', 'historicalWholeVerifierFrame', 'rootObservation',
    'rootObserverHistory', 'outerRootObservation', 'outerTerminal', 'innerTerminal',
    'outerRawStdout', 'outerRawStderr', 'innerRawStdout', 'innerRawStderr',
    'inputClosure', 'checks', 'readerTerminal']
fixed_keys = [
    'verifiedPassed', 'toolingSourceIndexSha256', 'variant', 'rawExporterExitCode',
    'nativeSourceFiles', 'externalEmbeddingSources', 'selectedManifestCount',
    'allObservedOwnedGroupsGone', 'wholeCandidateAndRawJSONEqual', 'otherVariantsNull',
    'engineExecuted', 'bootstrapExecuted', 'operationalAdmission', 'runtimeAcceptanceClaim',
    'sourceAndOriginalProtectionRechecked', 'wholeHelperFrameUnchanged',
    'completeMetadataFields', 'completeSelectedManifests',
    'ownerActionsInvoked', 'hostActionsInvoked', 'exportOrBootstrapActionsInvoked',
    'readHashJsonAstDataOnly', 'operationalEntrypointsImportedOrInvoked',
    'grantsBootstrapAuthority', 'grantsRuntimeAuthority']
write('result-contract.json', dict(
    schemaVersion=3, requiredReviewState=result['state'], requiredResultSchemaVersion=3,
    requiredFixedValues={k:result[k] for k in fixed_keys},
    requiredExactDescriptors={k:result[k] for k in descriptor_keys},
    requiredPairs={k:result[k] for k in ['actualVerifierReview', 'actualFrozenArtifactReview', 'toolingSourceReview']},
    requiredCoverage=result['coverage'],
    externalTerminalRole='Retained 600s owned helper-worker monitor terminal; enclosing 1800s parent monitor is separately outerTerminal.',
    futureContractSource=row(SOURCE / 'future-export-review-contract.json'),
    result=row(HERE / 'results.json'), grantsActionAuthority=False))

write('preparation-history.json', dict(
    schemaVersion=1,
    interruptions=['Reader source was saved unexecuted before the repository checkpoint and the separate Next.js experiment; resumed without changing owner artifacts.'],
    readerAttempts=[row(HERE / 'evidence/reader-attempt1/terminal.json')],
    failedReaderAttempts=[],
    retainedRootObserverHistory=root['rootObserverHistory'],
    rootObserverCorrection='Read-only variant-label assumption corrected; original candidate, operation, streams and source unchanged.',
    failuresOmitted=False, ownerActionsInvoked=False))

readme = '''The actual normal-OFF secret-owner artifact export passes this independent DATA review. The complete candidate equals both the raw helper-worker JSON and the authenticated pure pin model. All 75 original metadata fields and 11 full selected manifests remain unchanged. The saved helper frame is byte-identical to the previously reviewed complete verifier return.

The reader authenticated 27,962 lexical paths (2,025,315,554 logical bytes), including all 241 own declared inputs, the 27,729-row protection ledger, all 1,902 frozen copies and 1,899 corresponding original references. The frozen tree has exactly 1,903 files. The older normal tree's 1,391 files and 1,387 original entries were protected. Initial hashes, final identities, exact family membership, private output modes, and independent frozen inodes passed 31,979 checks.

The actual parent PID 86546 and helper-worker PID 86731 both returned zero with empty stderr, no timeout, no signals, no forced cleanup, and all observed groups gone. All 108 retained outer process observations and the inner observation are reconciled. The parent's two JSONL records preserve the initial PID record and final observation descriptor; the inner full JSON equals the saved candidate. `externalTerminal` in the V3 consumer contract names the 600-second helper-worker monitor; `outerTerminal` separately names the 1,800-second parent monitor. Root tool session 4382 is supported by the retained Root report, without inventing another raw Root-tool stdout file.

The candidate still has its original UNREVIEWED state and reviewRequired:true. Only normal-off is populated; normal-runtime, gc-off and disabled-off remain null. This review grants no pin derivation, bootstrap, engine, component, guest, key, cryptography, GC, runtime, or adoption authority. Root must make the separate validation-pin decision and issue a distinct bootstrap phase. The original e872 verifier, f894 DATA proof, d62 tooling, 522e source review, frozen metadata and context roles are preserved.

The reviewer used standard Python file hashing, strict JSON comparisons and AST extraction of the two pure candidate functions. No operational entrypoint or owner helper was imported or called, and no Node process, exporter, bootstrap, monitor, or engine was rerun. Source-supported invocation counts and observed-process cleanup are explicitly bounded; they are not instrumentation of unobserved processes or runtime behavior. `preparation-history.json` retains the interruption and Root's separate observation-reader correction.
'''
with (HERE / 'README.md').open('x') as stream:
    stream.write(readme)
write('review-receipt.json', dict(
    schemaVersion=3, state='INDEPENDENT_SECRET_OWNER355_EXPORT_DATA_REVIEW_SEALED',
    result=row(HERE / 'results.json'), contract=row(HERE / 'result-contract.json'),
    sourceIndex=root['sourceIndex'], actualRootResult=root_row,
    candidate=root['candidate'], wholeVerifierFrame=root['wholeVerifierFrame'],
    checkCount=audit['checks'], rehashedLexicalPaths=audit['rehashedLexicalPaths'],
    finalInputIdentityAndMembershipChecksPassed=True,
    readerRawExitCode=terminal['rawExitCode'],
    readHashJsonAstDataOnly=True, ownerActionsInvoked=False,
    grantsActionAuthority=False))

members=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():
        assert p.name != 'index.json'
        d=row(p);d['path']=p.relative_to(HERE).as_posix();members.append(d)
write('index.json', dict(schemaVersion=1,files=members))
index=load(HERE / 'index.json')
actual_names={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
assert actual_names == {'index.json'} | {r['path'] for r in members}
for d in index['files']:
    assert row(HERE / d['path']) == {**d, 'path':str(HERE / d['path'])}
for key in descriptor_keys:
    assert row(result[key]['path']) == result[key]
print(json.dumps(dict(index=row(HERE/'index.json'), result=row(HERE/'results.json'),
    contract=row(HERE/'result-contract.json'), receipt=row(HERE/'review-receipt.json'),
    indexedMembers=len(members), checks=audit['checks'],
    rehashedLexicalPaths=audit['rehashedLexicalPaths'], ownerActionsInvoked=False)))
