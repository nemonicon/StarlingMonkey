"""Run only the independent static/data reader and retain its raw outcome."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
out=HERE/'reader-evidence'
out.mkdir(exist_ok=False)
argv=[sys.executable,'-I',str(HERE/'audit.py')]
result=subprocess.run(argv,cwd=HERE,capture_output=True,timeout=300)
streams={}
for name,data in [('stdout.log',result.stdout),('stderr.log',result.stderr)]:
    (out/name).write_bytes(data)
    streams[name]=dict(path=str(out/name),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
(out/'terminal.json').write_text(json.dumps(dict(schemaVersion=1,argv=argv,cwd=str(HERE),rawExitCode=result.returncode,
    streams=streams,sourceDataAndMemoryModelsOnly=True,ownerHelperOrRuntimeActionsInvoked=False),indent=2)+'\n')
print(json.dumps(dict(rawExitCode=result.returncode,evidence=str(out))))
raise SystemExit(result.returncode)
