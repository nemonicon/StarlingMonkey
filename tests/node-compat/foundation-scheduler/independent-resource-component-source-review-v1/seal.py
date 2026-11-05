"""Seal independent SOURCE evidence after whole input stability rechecks."""
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
    audit = json.loads((HERE / 'source-audit.json').read_bytes())
    final = json.loads((HERE / 'source-attempt1.stdout.log').read_bytes())
    pure = json.loads((HERE / 'independent-pure.stdout.log').read_bytes())
    grammar = json.loads((HERE / 'pure-and-grammar-results.json').read_bytes())
    assert grammar['allRawZero'] and len(grammar['commands']) == 7
    assert pure['checks'] == 406 and final['checks'] == 82296 and audit['checks'] == 60272
    inputs = json.loads((HERE / 'input-hashes.json').read_bytes())['files']
    assert len(inputs) == audit['uniquePaths'] == 5506
    for value in inputs:
        assert row(value['path']) == value
    source = audit['sourceIndex']
    assert row(source['path']) == source
    source_root = Path(source['path']).parent
    index = json.loads(Path(source['path']).read_bytes())
    assert len(index['files']) == 99
    for value in index['files']:
        assert row(source_root / value['path']) == dict(value, path=str(source_root / value['path']))
    assert {p.relative_to(source_root).as_posix() for p in source_root.rglob('*') if p.is_file()} == {'index.json'} | {v['path'] for v in index['files']}
    result = dict(
        schemaVersion=1,
        state='INDEPENDENT_SCHEDULER_RESOURCE342_COMPONENT_SOURCE_REVIEW_PASSED_V1',
        sourceIndexSha256=source['sha256'], sourceIndex=source,
        sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False,
        sourceChecks=audit['checks'], finalReaderChecks=final['checks'],
        uniqueInputPaths=5506, inputRows=5399, sourceMembers=99,
        nativeSourceFiles=342, selectedManifests=9,
        packagingRegularFiles=4934, physicalToolLinks=22,
        independentPureCases=406, nodeSyntaxChecks=6, pythonAstSources=4,
        sourceAudit=row(HERE / 'source-audit.json'), inputHashes=row(HERE / 'input-hashes.json'),
        pureAndGrammar=row(HERE / 'pure-and-grammar-results.json'),
        constructionAllowed=False, ordinaryRuntimeAllowed=False,
        generatedModuleImported=False, nativeBuildInvoked=False,
        bootstrapInvoked=False, componentizerInvoked=False,
        engineInvoked=False, guestInvoked=False, timingInvoked=False,
        operationalAdmission=False, runtimeAcceptanceClaim=False,
        qualifications=[
            'Exact timer imports are monotonic-clock/io-poll@0.2.10; pure imports are empty. Coarse clock output may fail without policy widening.',
            'Full component bytes and WIT are captured before final audit; over-bound components fail without a full-retention claim.',
            'Actual construction, generated artifact/loading graph, async exports, timer resource behavior and both stock hosts remain separate gates.',
            'The original resource342 engine does not include the later selector fix; reset/reuse, fallible enqueue and ALS remain unresolved.',
            'A separately reviewed fixture-specific outer controller is required; this SOURCE review grants no actions.',
        ],
    )
    write('results.json', result)
    write('result-contract.json', dict(schemaVersion=1, state=result['state'], sourceIndexSha256=source['sha256'], result=row(HERE / 'results.json'), sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, grantsAnyActionAuthority=False))
    write('receipt.json', dict(schemaVersion=1, state='SEALED_INDEPENDENT_RESOURCE_COMPONENT_SOURCE_REVIEW_V1', sourceIndex=source, result=row(HERE / 'results.json'), actionAuthoritiesIssued=False))
    members = [dict(row(path), path=path.relative_to(HERE).as_posix()) for path in sorted(HERE.rglob('*')) if path.is_file()]
    write('index.json', dict(schemaVersion=1, state='INDEPENDENT_RESOURCE_COMPONENT_SOURCE_REVIEW_FILES_V1', files=members))
    print(json.dumps(dict(index=row(HERE / 'index.json'), result=row(HERE / 'results.json'), members=len(members))))


if __name__ == '__main__':
    main()
