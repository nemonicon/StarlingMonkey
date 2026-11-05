"""Explicitly permitted pinned Node --check only. No source module evaluation."""
from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parent
TOOL=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
GUEST=P.parent/'ownership-gc-candidate-v1/guest.GC.UNEXECUTED.mjs'
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
tool=row(TOOL);source=row(GUEST)
assert tool['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0' and tool['bytes']==108619024
assert source['sha256']=='4c84a07c2b9992bb9a4874181f081c5c50dc97eab720ad652f9c3c4f6ed10713' and source['bytes']==14177
argv=[str(TOOL),'--check',str(GUEST)]
r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={'PATH':'/usr/bin:/bin'},timeout=30)
(P/'guest-syntax.stdout').write_bytes(r.stdout);(P/'guest-syntax.stderr').write_bytes(r.stderr)
(P/'syntax-terminal.json').write_text(json.dumps(dict(schemaVersion=1,argv=argv,rawExitCode=r.returncode,stdout=row(P/'guest-syntax.stdout'),stderr=row(P/'guest-syntax.stderr'),tool=tool,guestSource=source,timeoutSeconds=30,parseOnly=True,moduleImported=False,moduleEvaluated=False,ownerHelpersOrGuestKeyCryptoGcActionsInvoked=False),indent=2)+'\n')
assert r.returncode==0 and not r.stdout and not r.stderr
assert row(TOOL)==tool and row(GUEST)==source
print(json.dumps(dict(pinnedNodeCheckPassed=True,parseOnly=True,moduleImportedOrEvaluated=False)))
