"""Capture only this independent read/hash/JSON audit; no owner helper/action."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = HERE / 'reader-evidence'
out.mkdir(exist_ok=False)
argv = [sys.executable, '-I', str(HERE / 'reader.py')]
completed = subprocess.run(argv, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
streams = {}
for name, data in [('stdout.log', completed.stdout), ('stderr.log', completed.stderr)]:
    (out / name).write_bytes(data)
    streams[name] = dict(path=str(out / name), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
(out / 'terminal.json').write_text(json.dumps(dict(schemaVersion=1, argv=argv, cwd=str(HERE),
    rawExitCode=completed.returncode, streams=streams, independentDataReaderOnly=True,
    ownerHelpersOrForeignToolsOrRuntimeActionsInvoked=False), indent=2) + '\n')
print(json.dumps(dict(rawExitCode=completed.returncode, evidence=str(out))))
raise SystemExit(completed.returncode)
