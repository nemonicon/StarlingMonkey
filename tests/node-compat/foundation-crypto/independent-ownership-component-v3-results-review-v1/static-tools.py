"""Only host JS source parsing and static component-WIT binary decoding."""
import hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
node=dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes=108619024)
tool=dict(path='/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools',sha256='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d',bytes=17556208)
assert desc(node['path'])==node and desc(tool['path'])==tool
commands=[('glue-ast',[node['path'],str(P/'glue-ast-review.mjs')]),('component-wit',[tool['path'],'component','wit','/private/tmp/starling-node-compat/crypto-owner355-component-v3/worker/crypto-owner.component.wasm'])]
records=[]
for name,argv in commands:
 r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,env={'PATH':'/usr/bin:/bin'},cwd=P)
 for stream,raw in [('stdout',r.stdout),('stderr',r.stderr)]: (P/(name+'.'+stream+'.txt')).write_bytes(raw)
 records.append(dict(name=name,argv=argv,exitCode=r.returncode,stdout=desc(P/(name+'.stdout.txt')),stderr=desc(P/(name+'.stderr.txt')),
  timeoutSeconds=60,staticOnly=True,generatedModuleImported=False,guestOrKeyCalled=False))
 (P/'static-tool-terminals.json').write_text(json.dumps(dict(schemaVersion=1,node=node,wasmTools=tool,privateParserSource=desc(P/'glue-ast-review.mjs'),records=records,ownerHelpersInvoked=False),indent=2)+'\n')
 assert r.returncode==0 and r.stderr==b'',(name,r.returncode,r.stderr.decode())
assert (P/'component-wit.stdout.txt').read_bytes()==Path('/private/tmp/starling-node-compat/crypto-owner355-component-v3/worker/emitted.wit').read_bytes()
ast=json.loads((P/'glue-ast.stdout.txt').read_bytes());assert ast['generatedModuleImported']is False
print(json.dumps(dict(staticParserAndWitDecodePassed=True,staticCommands=len(records),freshWitEqualsRetainedBytes=True)))
