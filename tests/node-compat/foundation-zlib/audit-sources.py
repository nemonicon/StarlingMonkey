#!/usr/bin/env python3
"""Fetch a finite pinned primary-source ledger; no upstream suite execution."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import urllib.request

OUT = Path(os.environ.get('NODE_COMPAT_ZLIB_OUTPUT', '/tmp/starling-node-compat/zlib-template-v1')) / 'source-audit'
OUT.mkdir(parents=True, exist_ok=True)
NODE = '5d2feb257bcee090e57900eb51720171a6aa92f3'
JCO = '42cd21e0a31362dbb519f4749f3689bba0fbdb1d'
PATHS = {
    'node': ['lib/zlib.js', 'src/node_zlib.cc', 'deps/zlib/zlib.h', 'LICENSE'] + [
        'test/parallel/' + name for name in (
            'test-zlib-convenience-methods.js', 'test-zlib-empty-buffer.js',
            'test-zlib-from-concatenated-gzip.js', 'test-zlib-from-gzip-with-trailing-garbage.js',
            'test-zlib-maxOutputLength.js', 'test-zlib-truncated.js',
            'test-zlib-dictionary.js', 'test-zlib-crc32.js')],
    'jco': ['packages/jco/src/node-builtins/zlib.ts', 'packages/jco/test/node/zlib.js',
        'packages/jco/test/fixtures/componentize/node-zlib/component.js',
        'packages/jco/test/fixtures/componentize/node-zlib/wit/component.wit',
        'packages/jco-std/test/wasi/0.2.x/node/zlib/lifecycle.ts',
        'packages/jco-std/test/wasi/0.2.x/node/zlib/module.ts',
        'packages/jco-std/test/wasi/0.2.x/node/zlib/gzipSync.ts',
        'packages/jco-std/test/wasi/0.2.x/node/helpers/zlib.ts'],
}

def fetch(item):
    origin, path = item
    revision, repo = (NODE, 'nodejs/node') if origin == 'node' else (JCO, 'bytecodealliance/jco')
    url = f'https://raw.githubusercontent.com/{repo}/{revision}/{path}'
    destination = OUT / origin / path
    try:
        data = destination.read_bytes() if destination.exists() else urllib.request.urlopen(url, timeout=30).read()
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        return {'origin': origin, 'revision': revision, 'path': path, 'url': url,
            'localPath': str(destination), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    except Exception as error:
        return {'origin': origin, 'path': path, 'url': url, 'error': str(error)}

with ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(fetch, [(origin, path) for origin, paths in PATHS.items() for path in paths]))
errors = [record for record in records if 'error' in record]
report_path = OUT / ('source-fetch-errors.json' if errors else 'source-ledger.json')
assert not report_path.exists(), 'Preserve earlier ledger; choose a fresh output path'
report_path.write_text(json.dumps({'schema': 1,
    'state': 'fetch-errors' if errors else 'selected-source-ledger-not-execution',
    'scriptSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'files': records}, indent=2) + '\n')
print(json.dumps({'files': len(records), 'errors': errors, 'report': str(report_path)}))
raise SystemExit(bool(errors))
