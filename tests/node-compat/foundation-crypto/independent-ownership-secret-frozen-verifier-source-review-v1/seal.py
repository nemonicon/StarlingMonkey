"""Seal the bounded verifier SOURCE review after full input rechecks."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def row(path):
    path = Path(path); a = path.stat(); h = hashlib.sha256()
    assert path.is_file() and not path.is_symlink()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    b = path.stat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns, b.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=b.st_size)


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    assert __debug__ and (HERE / 'attempt2.stderr.log').stat().st_size == 0
    audit = json.loads((HERE / 'audit.json').read_bytes())
    source = audit['sourceIndex']; assert row(source['path']) == source
    root = Path(source['path']).parent; index = json.loads(Path(source['path']).read_bytes())
    for value in index['files']:
        assert row(root / value['path']) == dict(value, path=str(root / value['path']))
    assert len(index['files']) == 18 and {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == {'index.json'} | {r['path'] for r in index['files']}
    inputs = json.loads((HERE / 'input-hashes.json').read_bytes())['files']
    assert len(inputs) == audit['uniqueInputs'] == 26276
    for value in inputs:
        assert row(value['path']) == value
    boundary = json.loads((HERE / 'ast-open-mode-recheck.json').read_bytes())
    assert row(boundary['source']['path']) == boundary['source'] and boundary['pathOpenModeArgumentIndex'] == 0 and all(v['mode'] == 'rb' for v in boundary['allExplicitOpenModes'])
    contract = json.loads((root / 'source-contract.json').read_bytes())
    write('attempt2.terminal.json', dict(exitCode=0, scope='finite source/DATA/AST and isolated predicates', completeVerifierInvoked=False))
    result = dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_SECRET_FROZEN_VERIFIER_SOURCE_REVIEW_PASSED_V1', verifierSourceIndexSha256=source['sha256'], nativeSourceIndexSha256=contract['nativeSourceIndex']['sha256'], freezerSourceIndexSha256=contract['freezerSourceIndex']['sha256'], actualArtifactReviewIndexSha256=contract['actualArtifactReview']['index']['sha256'], sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, verifierHelpersInvoked=False, exportOrBootstrapInvoked=False, checks=audit['checks'], uniqueInputs=len(inputs), independentPredicateCases=audit['independentPredicateCases'], pythonAstSources=5, exactPureFunctions=4, metadataPredicateEdits=4, frozenCopies=1902, originalReferences=1899, frozenMembership=1903, sourceIndex=source, actualArtifactReview=contract['actualArtifactReview'], audit=row(HERE / 'audit.json'), inputHashes=row(HERE / 'input-hashes.json'), explicitOpenModeAudit=row(HERE / 'ast-open-mode-recheck.json'), completeVerifierInvoked=False, exporterImplemented=False, pinModelImplemented=False, bootstrapImplemented=False, actualVerifierRun=None, rootAuthority=None, grantsAnyActionAuthority=False, operationalAdmission=False, runtimeAcceptanceClaim=False, qualifications=['SOURCE verdict only; complete frozen helper and future callers remain unexecuted.', 'Original references/inode provenance and full uncopied SDK/archive semantics remain separate historical artifact proof scope.', 'New authenticated read-only caller, complete verifier observation and missing export/pin/bootstrap work remain required.'])
    write('results.json', result)
    write('result-contract.json', {k: result[k] for k in ['schemaVersion', 'state', 'verifierSourceIndexSha256', 'nativeSourceIndexSha256', 'freezerSourceIndexSha256', 'actualArtifactReviewIndexSha256', 'sourceOnly', 'sourceReviewPassed', 'ownerActionsInvoked', 'verifierHelpersInvoked', 'exportOrBootstrapInvoked', 'grantsAnyActionAuthority']})
    write('receipt.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_SECRET_FROZEN_VERIFIER_SOURCE_REVIEW_V1', sourceIndex=source, result=row(HERE / 'results.json'), resultContract=row(HERE / 'result-contract.json'), actionAuthoritiesIssued=False))
    members = [dict(row(path), path=path.name) for path in sorted(HERE.iterdir()) if path.is_file()]
    write('index.json', dict(schemaVersion=1, state='INDEPENDENT_SECRET_FROZEN_VERIFIER_SOURCE_REVIEW_FILES_V1', files=members))
    print(json.dumps(dict(index=row(HERE / 'index.json'), result=row(HERE / 'results.json'), members=len(members))))


if __name__ == '__main__':
    main()
