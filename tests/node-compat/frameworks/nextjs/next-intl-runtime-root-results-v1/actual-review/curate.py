"""Retain completed ordinary runtime evidence; never launch a component."""
from pathlib import Path
import hashlib, io, json, tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TMP = Path('/private/tmp/starling-node-compat')
RUNS = {
    'unicode': ('regexp-intl-wasmtime-probe-enginee7baa5a9-strict-first3', 0),
    'stack': ('stacktrace-intl-wasmtime-probe-enginee7baa5a9-strict-first3', 1),
    'dependencies': ('next-intl-dependencies-wasmtime-enginee7baa5a9-strict-first3', 0),
    'next': ('next-wasmtime-deployment-enginee7baa5a9-intl-stack-v1', 1),
    'diagnostic': ('next-wasmtime-deployment-enginee7baa5a9-causes-v1', 1),
}

def row(path, data=None):
    path = Path(path)
    data = path.read_bytes() if data is None else data
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))

def main():
    records = []
    payloads = {}
    runs = {}
    def retain(path, destination):
        path = Path(path)
        assert path.is_file() and not path.is_symlink()
        data = path.read_bytes()
        data.decode('utf-8')
        assert destination not in payloads
        payloads[destination] = data
        records.append(dict(original=row(path, data), retained=destination))
    for key, (name, raw) in RUNS.items():
        output = TMP / name
        outer = TMP / (name + '-external-root')
        result = json.loads((output/'result.json').read_text())
        terminal = json.loads((outer/'terminal.json').read_text())
        assert terminal['rawExitCode'] == raw
        assert terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
        assert not terminal['timeout'] and not terminal['forcedCleanup']
        assert all(terminal[k] == [] for k in ('errors','signals','interruptedSignals','remainingObservedPids'))
        for directory, label in ((output, 'runtime'), (outer, 'outer')):
            for path in sorted(directory.rglob('*')):
                rel = path.relative_to(directory)
                if rel.parts[0] in ('app','cache','xdg-cache','xdg-config','xdg-data','tmp'):
                    continue
                if path.is_file():
                    retain(path, key+'/'+label+'/'+rel.as_posix())
        for descriptor in (result.get('rootAuthority') or result.get('authority'), result['sourceIndex'] if 'sourceIndex' in result else None):
            if descriptor and not any(x['original'] == descriptor for x in records):
                retain(descriptor['path'], key+'/inputs/'+Path(descriptor['path']).name)
        runs[key] = dict(outputRoot=str(output), rawExitCode=raw,
                         result=key+'/runtime/result.json', terminal=key+'/outer/terminal.json')
    # These pinned Node observations are an independent semantic baseline.
    for key, folder in (('unicode','regexp-unicode-probe-root-results-v1'),('stack','stacktrace-probe-root-results-v1')):
        for name in ('stdout.log','terminal.json'):
            retain(ROOT/folder/'node-owned'/name, key+'/oracle/'+name)
    ledger = dict(schemaVersion=1, runs=runs, files=records,
                  exclusions=['identical read-only application copies','application cache bytes','ephemeral XDG state'],
                  noGuestExecutedByCurator=True)
    with (HERE/'ledger.json').open('x') as stream:
        json.dump(ledger, stream, indent=2); stream.write('\n')
    with tarfile.open(HERE/'data.tar.gz', 'x:gz') as archive:
        for name, data in sorted(payloads.items()):
            info = tarfile.TarInfo(name); info.size = len(data); info.mode = 0o600; info.mtime = 0
            archive.addfile(info, io.BytesIO(data))
    # Verify every original after publication; do not turn mutation into success.
    assert all(row(x['original']['path']) == x['original'] for x in records)
    print(json.dumps(dict(retainedTextFiles=len(records), retainedBytes=sum(len(v) for v in payloads.values()), originalInputsPreserved=True)))

if __name__ == '__main__':
    main()
