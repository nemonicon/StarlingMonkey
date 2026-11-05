"""Independent read/hash/derivation audit; no owner or host action imports."""
from pathlib import Path
import ast
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-gc-wasmtime-candidate-v1'
checks = 0
inputs = {}


def need(value):
    global checks
    assert value
    checks += 1


def row(path):
    path = Path(path)
    physical = path.resolve(strict=True)
    before = physical.stat()
    digest = hashlib.sha256()
    with physical.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = physical.stat()
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns))
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=after.st_size)


def checked(value):
    need(row(value['path']) == value)
    inputs[value['path']] = value


def read(path):
    value = row(path)
    inputs[value['path']] = value
    return json.loads(Path(path).read_bytes())


def write(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


source_index = row(SOURCE / 'index.json')
need(source_index['sha256'] == 'c5d3ea491e81db5fad6c02e244bcc0cf784c8135a6ab1d5e552326f4f2e1ec35')
index = read(SOURCE / 'index.json')
names = set()
for member in index['files']:
    name = member['path']
    need(name not in names and not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')))
    names.add(name)
    checked(dict(member, path=str(SOURCE / name)))
need(len(names) == 60)
need({p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file()} == names | {'index.json'})
need(not any(p.is_symlink() for p in SOURCE.rglob('*')))
freeze = read(SOURCE / 'input-freeze.json')
need(len(freeze['files']) == len({r['path'] for r in freeze['files']}) == 11279)
for value in freeze['files']:
    need(os.path.isabs(value['path']) and os.path.normpath(value['path']) == value['path'] and '\\' not in value['path'] and '\0' not in value['path'])
    checked(value)
derivations = read(SOURCE / 'wasmtime-derivations.json')
for item in derivations['derived']:
    checked(item['donor'])
    original = Path(item['donor']['path']).read_text()
    text = original
    for edit in item['changes']:
        need(text.count(edit['before']) == edit.get('count', 1))
        text = text.replace(edit['before'], edit['after'])
    need(text == (SOURCE / item['file']).read_text())
    for edit in reversed(item['changes']):
        need(text.count(edit['after']) == edit.get('count', 1))
        text = text.replace(edit['after'], edit['before'])
    need(text == original)
refs = read(SOURCE / 'references.json')
need(refs['gcRuntimeSourceIndex']['sha256'] == '5abe5ed812b93676bff2f09cff57099bff6d23d7ada6e5e63bbbe8152d0a0959')
need(refs['artifactReview']['index']['sha256'] == 'f812eeec5fc53a3b289f970add2f3d1a9a52df71462f18767baeac81b090a195')
need(refs['wasmtime']['sha256'] == 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c')
for value in refs['artifacts'].values():
    checked(value)
checked(refs['node'])
checked(refs['wasmtime'])
run = (SOURCE / 'run.mjs').read_text()
guard = (SOURCE / 'guard.mjs').read_text()
protocol = (SOURCE / 'protocol.mjs').read_text()
need(run.index('checkOwnedTerminal(terminal)') < run.index('parseScalarStringOutput({'))
need(run.index("name+'-decoded-string.json'") < run.index('checkWholeRecord(record'))
need("value===frame.jcoWrapper.value" in run)
need('finally{try{await frame.recheck();}finally{await out.close();}}' in run)
need("for(let ordinal=1;ordinal<=3;ordinal++)" in run and 'new Set(sessions.map(s=>s.pid)).size===3' in run)
need("['run','--invoke','validate()',row.path]" in protocol)
need("rawDurablyRetained:true" in run and 'maxOutputBytes:frame.maxPipeBytes' in run)
need('freeze.files.map(descriptor)' in guard and 'await streamHash(refs.wasmtime)' in guard)
need("wrapperRow.path===join(dirname(jcoIx.path),'wrapper/raw/001.json')" in guard)
need("jcoGcReview" in guard and 'requiredCoverage' in guard and 'requiredExactDescriptors' in guard)
template = read(SOURCE / 'future-root-authority.template.json')
need(template['state'] is None and template['wasmtimeValidateAllowed'] is False and template['jcoGcReview'] is None and template['jcoGcContract'] is None)
need(template['nodeOracleAllowed'] is False and template['generatedJsAllowed'] is False and template['timingAllowed'] is False)
for path in SOURCE.glob('*.py'):
    ast.parse(path.read_bytes(), str(path))
for value in list(inputs.values()):
    checked(value)
write('data-results.json', dict(schemaVersion=1, sourceIndex=source_index, checks=checks, uniqueInputs=len(inputs),
                                members=60, canonicalInputRows=11279, exactProtocolEdits=6, exactRunEdits=8,
                                sourceOnly=True, ownerActionsInvoked=False))
write('rehashed-inputs.json', dict(schemaVersion=1, files=sorted(inputs.values(), key=lambda r: r['path'])))
print(json.dumps(dict(checks=checks, uniqueInputs=len(inputs), sourceOnly=True)))
