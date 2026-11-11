"""Retain finite raw logs, observations and Source needed for offline review."""
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-lifecycle-compiler-recovery-v1-first')
RUNTIME = Path('/private/tmp/starling-node-compat/next-lifecycle-runtime-v1-first')
PACKET = HERE / 'raw-records'


def main():
    selected = {}
    def add(source, destination):
        if destination in selected:
            raise RuntimeError('Duplicate destination')
        selected[destination] = source
    for source in sorted((WORK / 'commands').rglob('*')):
        if source.is_file():
            add(source, 'commands/' + source.relative_to(WORK / 'commands').as_posix())
    for source in sorted(RUNTIME.iterdir()):
        if source.is_file():
            add(source, 'runtime/' + source.name)
    for label, source in [
        ('context-v1', '/private/tmp/starling-node-compat/web-stream-context-candidate-v1-node-first/result.json'),
        ('context-v2', '/private/tmp/starling-node-compat/web-stream-context-candidate-v2-node-first/result.json'),
        ('clone', '/private/tmp/starling-node-compat/response-clone-cancel-candidate-v1-node-first/result.json')]:
        add(Path(source), 'oracles/' + label + '.json')
    for name in ('options.json', 'result.json', 'returned-imports.json', 'returned-own-shape.json', 'final-preopens.json'):
        add(WORK / 'lifecycle-component-first' / name, 'construction/' + name)
    for name in ('source-materialization.json',):
        add(WORK / name, 'compiler/' + name)
    for name in ('package.json', 'package-lock.json'):
        add(WORK / 'toolchain' / name, 'compiler/' + name)
    for name in ('construction-review.json', 'differential-result.json', 'runtime-request.json',
                 'npm-lock-relocation.json', 'optional-restoration.json'):
        add(HERE / name, 'review/' + name)
    for source in sorted(HERE.glob('*peer*.json')):
        add(source, 'review/' + source.name)
    for name in ('check-saved.py', 'compare-results.mjs', 'run-wasmtime.py', 'run-command.py', 'retain.py'):
        add(HERE / name, 'sources/' + name)
    for family in ('web-stream-context-candidate-v1', 'web-stream-context-candidate-v2',
                   'response-clone-cancel-candidate-v1', 'web-stream-context-component-v1',
                   'next-lifecycle-construction-v1', 'compiler-recovery-v1'):
        for source in sorted((HERE.parent / family).rglob('*')):
            if source.is_file():
                add(source, 'sources/' + family + '/' + source.relative_to(HERE.parent / family).as_posix())
    payloads = []
    for destination, source in sorted(selected.items()):
        if source.is_symlink() or source.stat().st_size > 16 * 1024**2:
            raise RuntimeError('Finite regular source required: ' + str(source))
        before = source.stat()
        raw = source.read_bytes()
        after = source.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise RuntimeError('Input changed during capture')
        payloads.append((destination, source, raw))
    if sum(len(raw) for _, _, raw in payloads) > 32 * 1024**2:
        raise RuntimeError('Packet exceeds 32 MiB')
    PACKET.mkdir(mode=0o700)
    rows = []
    for destination, source, raw in payloads:
        target = PACKET / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        if target.read_bytes() != raw or source.read_bytes() != raw:
            raise RuntimeError('Retention readback or source bookend differs')
        rows.append(dict(path=destination, sourcePath=str(source), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)))
    index = dict(schemaVersion=1, state='LIFECYCLE_RAW_RECORDS_V1', files=rows,
                 payloadBytes=sum(row['bytes'] for row in rows),
                 componentAndEngineBinariesIncluded=False, compilerDependencyPayloadsIncluded=False)
    with (PACKET / 'index.json').open('x') as handle:
        json.dump(index, handle, indent=2); handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    print(json.dumps(dict(payloads=len(rows), payloadBytes=index['payloadBytes'])))


if __name__ == '__main__':
    main()
