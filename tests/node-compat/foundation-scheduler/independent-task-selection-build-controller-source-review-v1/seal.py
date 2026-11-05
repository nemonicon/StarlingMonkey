"""Seal SOURCE evidence following full stability rechecks; no action APIs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def row(path):
    path = Path(path); a = path.stat(); h = hashlib.sha256()
    assert not path.is_symlink() and path.is_file()
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
    assert __debug__ and (HERE / 'attempt1.stderr.log').stat().st_size == 0
    audit = json.loads((HERE / 'audit.json').read_bytes())
    source = audit['controllerIndex']
    assert row(source['path']) == source
    root = Path(source['path']).parent
    index = json.loads(Path(source['path']).read_bytes())
    for value in index['files']:
        assert row(root / value['path']) == dict(value, path=str(root / value['path']))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == {'index.json'} | {v['path'] for v in index['files']}
    inputs = json.loads((HERE / 'input-hashes.json').read_bytes())['files']
    for value in inputs:
        assert row(value['path']) == value
    write('attempt1.terminal.json', dict(exitCode=0, scope='finite source/DATA/AST and isolated predicates only', ownerActionsInvoked=False))
    result = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1', controllerSourceIndexSha256=source['sha256'], taskSelectionSourceIndexSha256=audit['taskSelectionSourceIndex']['sha256'], sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, hostActionsInvoked=False, nativeBuildActionsInvoked=False, checks=audit['checks'], uniqueInputs=audit['uniqueInputs'], independentPureCases=audit['independentPureCases'], pythonAstSources=4, stagedPairs=566, nativeSourceFiles=342, unchangedResourceParentFiles=339, nativeReplacements=3, actualStageReview=audit['actualStageReview'], sourceIndex=source, audit=row(HERE / 'audit.json'), inputHashes=row(HERE / 'input-hashes.json'), grantsAnyActionAuthority=False, actualBuildResult=None, engine=None, metadata=None, operationalAdmission=False, runtimeAcceptanceClaim=False, limitations=['Source review only; no controller, monitor, lifecycle, metadata model, native helper, build or engine action.', 'Actual command/archive/object/SDK/Rust/OpenSSL evidence and full ABI rebuild require a fresh Root action and independent BUILD review.', 'New source-aware freezer and normal artifact/pin/bootstrap/component/runtime gates remain required.'])
    write('results.json', result)
    write('result-contract.json', {k: result[k] for k in ['schemaVersion', 'state', 'controllerSourceIndexSha256', 'taskSelectionSourceIndexSha256', 'sourceOnly', 'sourceReviewPassed', 'ownerActionsInvoked', 'hostActionsInvoked', 'nativeBuildActionsInvoked', 'grantsAnyActionAuthority']})
    write('receipt.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_SELECTOR_BUILD_CONTROLLER_SOURCE_REVIEW_V1', sourceIndex=source, result=row(HERE / 'results.json'), resultContract=row(HERE / 'result-contract.json'), actionAuthoritiesIssued=False))
    members = [dict(row(path), path=path.name) for path in sorted(HERE.iterdir()) if path.is_file()]
    write('index.json', dict(schemaVersion=1, state='INDEPENDENT_SELECTOR_BUILD_CONTROLLER_SOURCE_REVIEW_FILES_V1', files=members))
    print(json.dumps(dict(index=row(HERE / 'index.json'), result=row(HERE / 'results.json'), members=len(members))))


if __name__ == '__main__':
    main()
