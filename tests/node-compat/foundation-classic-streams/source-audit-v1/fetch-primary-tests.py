#!/usr/bin/env python3
"""Fetch two exact Node22 primary test sources for reading, never run them."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

here = Path(__file__).resolve().parent
output = Path('/tmp/starling-node-compat/classic-streams-source-audit-v1/upstream-tests')
output.mkdir(parents=True, exist_ok=True)
rows = []
for name in ['test-stream-pipeline.js', 'test-stream-consumers.js']:
    url = 'https://raw.githubusercontent.com/nodejs/node/v22.14.0/test/parallel/' + name
    data = urlopen(url, timeout=20).read()
    path = output/name
    if path.exists():
        assert path.read_bytes() == data
    else:
        path.write_bytes(data)
    rows.append({'url': url, 'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'executed': False})
(here/'primary-tests.json').write_text(json.dumps({'state':'SOURCE_INSPECTION_ONLY', 'files': rows}, indent=2)+'\n')
print(json.dumps({'files': len(rows), 'bytes': sum(row['bytes'] for row in rows)}))
