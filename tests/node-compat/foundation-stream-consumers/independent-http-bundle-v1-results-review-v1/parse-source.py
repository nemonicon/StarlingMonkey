"""Only a pinned host parser reads source text; no bundle/owner import."""
from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
node=dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes=108619024)
assert row(node['path'])==node
argv=[node['path'],str(P/'parse-code.mjs')]
r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,env={'PATH':'/usr/bin:/bin'})
(P/'parser.stdout.json').write_bytes(r.stdout);(P/'parser.stderr.txt').write_bytes(r.stderr)
(P/'parser-terminal.json').write_text(json.dumps(dict(schemaVersion=1,argv=argv,executable=node,parserSource=row(P/'parse-code.mjs'),rawExitCode=r.returncode,timeoutSeconds=60,stdout=row(P/'parser.stdout.json'),stderr=row(P/'parser.stderr.txt'),hostParserOnly=True,generatedBundleImported=False,ownerHelpersGuestOrHostInvoked=False),indent=2)+'\n')
assert r.returncode==0 and r.stderr==b'',(r.returncode,r.stderr.decode())
print(json.dumps(dict(hostParsePassed=True,sourceNotExecuted=True)))
