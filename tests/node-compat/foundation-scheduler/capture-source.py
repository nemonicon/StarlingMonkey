#!/usr/bin/env python3
"""Read-only source/ancestry pin. No engine, component, compiler or fault test."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ARTIFACTS = Path('/tmp/starling-node-compat/improved-build/artifacts')
METADATA = next(ARTIFACTS.glob('*OFF.*foundations-v10.wasm.build.json'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def pin(path, label=None):
    path = Path(path)
    return {'path': label or str(path), 'sha256': sha(path), 'bytes': path.stat().st_size}

metadata = json.loads(METADATA.read_text())
assert metadata['auditedBaseRevision'] == '54b3329b3ce818fd1f244e871e9c259b63667cda'
assert len(metadata['sourceManifest']) == 304
assert len({item['path'] for item in metadata['sourceManifest']}) == 304
for item in metadata['sourceManifest']:
    assert sha(REPO / item['path']) == item['sha256'], item['path']
assert sha(metadata['enginePath']) == metadata['engineSha256']
embedding = None
for command in metadata['actualEmbeddingCompileCommands']:
    for argument in shlex.split(command):
        if argument.endswith('/embedding/embedding.cpp'):
            embedding = Path(argument)
assert embedding is not None
assert sha(embedding) == next(item['sha256'] for item in metadata['componentizeSourceManifest']
                              if item['path'] == 'embedding/embedding.cpp')
native_files = [
    'runtime/event_loop.cpp', 'runtime/event_loop.h', 'runtime/engine.cpp',
    'runtime/js.cpp', 'runtime/script_loader.cpp', 'include/extension-api.h',
    'CMakeLists.txt', 'cmake/builtins.cmake', 'cmake/add_builtin.cmake',
    'builtins/node-compat/register.cpp', 'builtins/web/queue-microtask.cpp',
    'builtins/web/timers.cpp', 'builtins/web/fetch/fetch_event.cpp',
    'builtins/web/fetch/request-response.cpp', 'builtins/web/streams/buf-reader.cpp',
    'host-apis/wasi-0.2.0/host_api.cpp',
]
evidence = [
    'tests/node-compat/foundation-stream/README.md',
    'tests/node-compat/foundation-stream/reference-results.json',
    'tests/node-compat/foundation-stream/scheduler-probe.cjs',
    'tests/node-compat/foundation-stream/source-audit.json',
    'tests/node-compat/async-context/source-audit.json',
    'tests/node-compat/async-context/resource-model-v3.cpp',
    'tests/node-compat/async-context/resource-model.md',
    'tests/node-compat/async-context/resource-model-results.json',
]
headers = Path('/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include')
header_names = ['js/Array.h', 'js/CallAndConstruct.h', 'js/ColumnNumber.h',
                'js/ErrorReport.h', 'js/GCPolicyAPI.h', 'js/GCVector.h',
                'js/Promise.h', 'js/Realm.h', 'js/ValueArray.h', 'jsfriendapi.h']
record = {
    'schemaVersion': 1, 'status': 'source-audit-only',
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
    'engineReceipt': pin(METADATA), 'engineSha256': metadata['engineSha256'],
    'engineBytes': metadata['engineBytes'],
    'auditedBaseRevision': metadata['auditedBaseRevision'],
    'componentizeJsRevision': metadata['componentizeJsRevision'],
    'buildRecipeSha256': metadata['buildRecipeSha256'],
    'actualSourceCount': 304, 'allCurrentSourceHashesMatchReceipt': True,
    'sourceManifest': metadata['sourceManifest'],
    'sourceInputManifestSha256': metadata['sourceInputManifestSha256'],
    'observedCMakeOptions': metadata['observedCMakeOptions'],
    'componentizeSource': pin(embedding),
    'componentizeSourceManifest': metadata['componentizeSourceManifest'],
    'actualTaskAndCheckpointFiles': [pin(REPO / path, path) for path in native_files],
    'priorEvidenceReusedWithoutExecutionOrMutation': [pin(REPO / path, path) for path in evidence],
    'spiderMonkey': {'revision': '9dab3d6f643e926a340c391ea30968e940390dec',
                    'releaseArchiveSha256': metadata['archivePins']['spiderMonkeySha256'],
                    'headers': [pin(headers / path) for path in header_names],
                    'cachedJSContextSource': pin('/tmp/starling-node-compat/async-context/source/JSContext.cpp')},
    'nodeSource': {'release': 'v22.14.0',
                   'url': 'https://github.com/nodejs/node/blob/v22.14.0/lib/internal/process/task_queues.js',
                   'extraction': "process.binding('natives')['internal/process/task_queues'] from exact Node binary",
                   **pin(HERE / 'node-source/task_queues.node-v22.14.0.js', 'node-source/task_queues.node-v22.14.0.js')},
    'proposalFiles': [pin(path, str(path.relative_to(HERE))) for path in sorted(HERE.rglob('*'))
                      if path.is_file() and path.name not in {'source-audit.json'} and '__pycache__' not in path.parts],
    'productionSourceChanged': False, 'templateCompiled': False, 'guestExecuted': False,
    'scope': 'Exact current m0.10 native ancestry plus previous ALS/Node evidence; source/template review and small Node host oracles only.',
}
(HERE / 'source-audit.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'sourceCount': 304, 'allHashesMatch': True,
                  'engineSha256': record['engineSha256'], 'templateCompiled': False, 'guestExecuted': False}))
