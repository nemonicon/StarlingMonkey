"""Read-only full retained construction output observation. No guest/tool calls."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
S = HERE.parent


def row(path):
    path = Path(path)
    before = path.stat(); h = hashlib.sha256()
    assert path.is_file() and not any(v.is_symlink() for v in [path, *path.parents])
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    assert __debug__
    reports = []
    for fixture, sha in [('pure', '952d10daac2de6e9118b7de8fdbd29dfd77b11eba95607ed6f280dbd69587634'), ('resource', '41a2901e62c05b5531ccac4bd05b41d0210f3d15742de619d7eb03d5da9cee56')]:
        descriptor = row(S / ('resource-component-' + fixture + '-v1-root-results.json'))
        assert descriptor['sha256'] == sha
        report = json.loads(Path(descriptor['path']).read_bytes())
        assert report['cleanOwnedTermination'] is True
        for value in report['actualOutputInventory']['files']:
            assert row(value['path']) == value
        for key in ['externalTerminal', 'stdout', 'stderr', 'rootAuthority', 'config']:
            assert row(report[key]['path']) == report[key]
        output_root = Path('/private/tmp/starling-node-compat/scheduler-resource-component-v1-' + fixture)
        assert {str(v) for v in output_root.rglob('*') if v.is_file()} == {v['path'] for v in report['actualOutputInventory']['files']}
        worker = output_root / 'worker'
        wit = (worker / 'emitted.wit').read_text()
        imports = sorted(re.findall(r'^  import ([^;]+);$', wit, re.M))
        captured = json.loads((worker / 'pre-final-interface-audit.json').read_bytes())
        component = row(worker / 'component.wasm')
        assert component == dict(captured['component'], path=str(worker / captured['component']['path']))
        if fixture == 'pure':
            assert report['rawExitCode'] == 0 and report['constructionRawZeroObserved'] is True and imports == []
            audit = json.loads((worker / 'interface-audit.json').read_bytes())
            assert audit['emittedImports'] == [] and audit['componentSha256'] == component['sha256']
        else:
            assert report['rawExitCode'] == 1 and report['constructionRawZeroObserved'] is False
            failure = json.loads((worker / 'failure.json').read_bytes())
            assert failure['stage'] == 'selected-componentize-or-final-interface-audit' and failure['componentCaptured'] is True and failure['constructionAdmissionPassed'] is False
            assert imports == sorted(['wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10', 'wasi:io/streams@0.2.10', 'wasi:cli/stderr@0.2.10', 'wasi:clocks/monotonic-clock@0.2.10', 'wasi:clocks/wall-clock@0.2.10'])
        reports.append(dict(fixture=fixture, rootObservation=descriptor, emittedWit=row(worker / 'emitted.wit'), component=component, emittedRootImports=imports, actualOutputInventory=report['actualOutputInventory'], externalTerminal=report['externalTerminal'], ordinaryExportsInvoked=False, generatedModuleImported=False))
    result = dict(schemaVersion=1, state='ROOT_AUDITED_RESOURCE_COMPONENT_STRICT_IMPORT_POLICY_REJECTION_V1', observations=reports, selectedTimerInterfaces=['wasi:clocks/monotonic-clock@0.2.10', 'wasi:io/poll@0.2.10'], sourceIndexSha256='74413aa9d1520139dc2ac4d8e43f0d99bab06477b8d8eb6e9d2db6bb58580055', sourcePolicyWidened=False, candidateComponentInstantiated=False, ordinaryExportsInvoked=False, timerRuntimeInvoked=False, generatedModuleImported=False, exactOpaqueThrownErrorCauseProved=False, typeOnlyVersusCallableImportGraphReviewed=False, independentArtifactOrFailureReview=None, operationalAdmission=False, runtimeAcceptanceClaim=False, nextRequiredWork='Review actual core/adapter/type graph and pinned guest clock/stdio pruning. Keep the strict policy; prepare a separate source successor before any new clock construction or runtime action.')
    write('results.json', result)
    members = [dict(row(path), path=path.name) for path in sorted(HERE.iterdir()) if path.is_file()]
    write('index.json', dict(schemaVersion=1, state='RESOURCE_CLOCK_POLICY_FAILURE_OBSERVATION_FILES_V1', files=members))
    print(json.dumps(dict(index=row(HERE / 'index.json'), result=row(HERE / 'results.json'))))


if __name__ == '__main__':
    main()
