"""Seal a finite SOURCE-only review; no helper/native action."""
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent


def row(path):
    path = Path(path)
    before = path.stat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=after.st_size)


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    assert __debug__
    audit = json.loads((HERE / 'audit.json').read_bytes())
    need = audit['checks'] == 257314 and audit['uniqueInputs'] == 24312 and audit['independentPureCases'] == 24
    assert need and (HERE / 'attempt2.stderr.log').stat().st_size == 0
    source = audit['sourceIndex']
    assert row(source['path']) == source
    source_root = Path(source['path']).parent
    index = json.loads(Path(source['path']).read_bytes())
    for value in index['files']:
        assert row(source_root / value['path']) == dict(value, path=str(source_root / value['path']))
    assert len(index['files']) == 26
    assert {p.relative_to(source_root).as_posix() for p in source_root.rglob('*') if p.is_file()} == {'index.json'} | {r['path'] for r in index['files']}
    inputs = json.loads((HERE / 'input-hashes.json').read_bytes())['files']
    assert len(inputs) == 24312
    for value in inputs:
        assert row(value['path']) == value
    contract = json.loads((source_root / 'source-contract.json').read_bytes())
    write('attempt2.terminal.json', dict(exitCode=0, scope='finite source read/hash/AST and isolated pure predicates', ownerActionsInvoked=False))
    result = dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_SECRET_FREEZER_SOURCE_REVIEW_PASSED_V1', sourceIndexSha256=source['sha256'], sourceIndex=source, nativeSourceIndexSha256=contract['nativeSourceIndex']['sha256'], actualBuildReviewIndexSha256=contract['actualBuildReview']['index']['sha256'], sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, hostActionsInvoked=False, nativeFreezeActionsInvoked=False, checks=audit['checks'], uniqueInputs=len(inputs), lexicalBuildRows=25594, stagedPairs=1424, normalFrozenMembers=1391, normalOriginalReferences=1387, exactCommonFunctions=12, reversibleEdits=26, independentPureCases=24, pythonAstSources=7, actualBuildReview=contract['actualBuildReview'], actualBuildContract=contract['actualBuildContract'], buildReferenceLedger=contract['buildReferenceLedger'], audit=row(HERE / 'audit.json'), inputHashes=row(HERE / 'input-hashes.json'), actualFreezeReceipt=None, independentFrozenArtifactReview=None, reviewedNativePins=None, runtimeAuthority=None, grantsAnyActionAuthority=False, operationalAdmission=False, runtimeAcceptanceClaim=False, qualifications=['This is a SOURCE verdict; actual raw helper calls, copy/freezer output, full immutable artifact review and separate tooling remain unverified.', 'The BUILD ledger verifies references which are not all copied; original contexts and raw metadata paths remain unchanged.', 'Frozen-only verifier/export/pin/bootstrap modules are absent; copied provenance cannot be executed as relocated tooling.', 'No engine, guest, entropy/ECC, allocation-failure, wipe-completeness, GC, reset/reuse, ALS, security or performance acceptance.'])
    write('results.json', result)
    write('result-contract.json', {k: result[k] for k in ['schemaVersion', 'state', 'sourceIndexSha256', 'nativeSourceIndexSha256', 'actualBuildReviewIndexSha256', 'sourceOnly', 'sourceReviewPassed', 'ownerActionsInvoked', 'hostActionsInvoked', 'nativeFreezeActionsInvoked', 'grantsAnyActionAuthority']})
    write('receipt.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_SECRET_FREEZER_SOURCE_REVIEW_V1', sourceIndex=source, result=row(HERE / 'results.json'), resultContract=row(HERE / 'result-contract.json'), actionAuthoritiesIssued=False))
    members = [dict(row(path), path=path.relative_to(HERE).as_posix()) for path in sorted(HERE.rglob('*')) if path.is_file()]
    write('index.json', dict(schemaVersion=1, state='INDEPENDENT_SECRET_FREEZER_SOURCE_REVIEW_FILES_V1', files=members))
    print(json.dumps(dict(index=row(HERE / 'index.json'), result=row(HERE / 'results.json'), contract=row(HERE / 'result-contract.json'), members=len(members))))


if __name__ == '__main__':
    main()
