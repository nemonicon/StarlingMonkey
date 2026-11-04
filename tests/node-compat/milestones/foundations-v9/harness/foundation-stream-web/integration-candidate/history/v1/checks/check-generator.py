"""Dependency-free generation, exact Node inventory and failure-path checks."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'source'
DIRECTORY = SOURCE / 'builtins/node-compat'
NODE = '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
digest = lambda data: hashlib.sha256(data).hexdigest()
existing = {p.name: digest(p.read_bytes()) for p in DIRECTORY.glob('*factories.generated.h') if p.name != 'stream-web-factories.generated.h'}
command = [NODE, str(DIRECTORY / 'generate-factories.mjs'), '--check']
main = subprocess.run(command, capture_output=True, text=True)
assert main.returncode == 0, main.stderr
assert existing == {p.name: digest(p.read_bytes()) for p in DIRECTORY.glob('*factories.generated.h') if p.name != 'stream-web-factories.generated.h'}
workspace = Path(tempfile.mkdtemp(prefix='stream-web-generator-', dir='/tmp/starling-node-compat'))
cases = []
def mutate(label, callback, expected):
    directory = workspace / label
    shutil.copytree(DIRECTORY, directory)
    callback(directory)
    header = directory / 'stream-web-factories.generated.h'
    before = digest(header.read_bytes())
    command = [NODE, str(directory / 'generate-stream-web-factory.mjs'), '--check']
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0 and expected in result.stderr, (label, result.stderr)
    assert digest(header.read_bytes()) == before
    cases.append({'name': label, 'command': command, 'exitCode': result.returncode, 'expected': expected, 'stderr': result.stderr, 'headerUnchanged': True})
def change_manifest(directory, operation):
    path = directory / 'export-manifest.stream-web.node-v22.14.0.json'
    manifest = json.loads(path.read_text())
    operation(manifest['modules']['node:stream/web'])
    path.write_text(json.dumps(manifest, indent=2) + '\n')
mutate('invented-export', lambda d: change_manifest(d, lambda module: module['exports'].append('inventedExport')), 'exact pinned Node22')
mutate('wrong-alias', lambda d: change_manifest(d, lambda module: module.update(aliases=['stream'])), 'Unexpected stream/web surface')
def edit(directory, name, old, new):
    path = directory / name
    source = path.read_text()
    assert old in source
    path.write_text(source.replace(old, new, 1))
mutate('missing-esm-declaration', lambda d: edit(d, 'stream-web-namespace.template.mjs', 'export const CompressionStream=moduleRecord.CompressionStream;\n', ''), 'Finite ESM bindings differ')
mutate('noncallable-record', lambda d: edit(d, 'stream-web-codecs.mjs', 'CountQueuingStrategy,TextEncoderStream,TextDecoderStream,CompressionStream,DecompressionStream};', 'CountQueuingStrategy,TextEncoderStream:undefined,TextDecoderStream,CompressionStream,DecompressionStream};'), 'Invalid named/default identity TextEncoderStream')
mutate('changed-default-identity', lambda d: edit(d, 'stream-web.mjs', '  return module;', '  module.default.TextEncoderStream=function changed(){};return module;'), 'Invalid named/default identity TextEncoderStream')
mutate('wrong-factory-arity', lambda d: edit(d, 'stream-web.mjs', 'createStreamWebModule(record)', 'createStreamWebModule(record,extra)'), 'exactly one private native-record argument')
version_command = [NODE, '--input-type=module', '-e', "Object.defineProperty(process,'version',{value:'v22.15.0'}); await import(" + json.dumps((DIRECTORY / 'generate-stream-web-factory.mjs').as_uri()) + ');']
version = subprocess.run(version_command, capture_output=True, text=True)
assert version.returncode != 0 and 'exact Node v22.14.0' in version.stderr
report = {'scope': 'Node22 build-host source/header/namespace validation only; no guest engine or native stream entry',
          'nodePath': NODE, 'nodeSha256': digest(Path(NODE).read_bytes()), 'mainCommand': command,
          'main': {'exitCode': main.returncode, 'stdout': main.stdout, 'stderr': main.stderr},
          'existingHeaderDigestsUnchanged': existing, 'negativeCases': cases,
          'versionPinRejection': {'exitCode': version.returncode, 'stderr': version.stderr}, 'engineBuilt': False}
(HERE / 'generator-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'headersPassed': 8, 'negativeCases': len(cases), 'versionPinRejects': True, 'engineBuilt': False}))
