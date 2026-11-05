"""Capture this read-only source audit only; no owner helper is invoked."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
out=HERE/'reader-evidence';out.mkdir(exist_ok=False)
argv=[sys.executable,'-I',str(HERE/'audit.py')]
r=subprocess.run(argv,cwd=HERE,capture_output=True,timeout=120)
streams={}
for name,b in [('stdout.log',r.stdout),('stderr.log',r.stderr)]:
    (out/name).write_bytes(b);streams[name]=dict(path=str(out/name),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
(out/'terminal.json').write_text(json.dumps(dict(schemaVersion=1,argv=argv,rawExitCode=r.returncode,streams=streams,
    sourceHashDataOnly=True,ownerHelpersOrRuntimeActionsInvoked=False),indent=2)+'\n')
print(json.dumps(dict(rawExitCode=r.returncode,evidence=str(out))))
raise SystemExit(r.returncode)
