"""Only authorized pure Node checks, parse checks and Python source/hash checks."""
from pathlib import Path
import ast,hashlib,json,subprocess
P=Path(__file__).resolve().parent
E=P/'evidence';E.mkdir(mode=0o700,exist_ok=False)
node=json.loads((P/'references.json').read_bytes())['node'];raw=Path(node['path']).read_bytes();assert len(raw)==node['bytes']and hashlib.sha256(raw).hexdigest()==node['sha256']
records=[]
def desc(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(P)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
for name,argv in [('pure',[node['path'],str(P/'test-pure.mjs')]),('source',['python3',str(P/'check-source.py')])]+[(p.name,[node['path'],'--check',str(p)])for p in sorted(P.glob('*.mjs'))]:
 r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
 stdout=E/(name+'.stdout.log');stderr=E/(name+'.stderr.log');stdout.write_bytes(r.stdout);stderr.write_bytes(r.stderr)
 records.append(dict(name=name,argv=argv,rawExitCode=r.returncode,stdout=desc(stdout),stderr=desc(stderr),sourceOnly=True))
 (E/'terminals.json').write_text(json.dumps(dict(schemaVersion=1,records=records,wasmtimeProcessGuestCryptoActionsInvoked=False),indent=2)+'\n')
 assert r.returncode==0 and r.stderr==b'',(name,r.returncode,r.stderr.decode())
python=[]
for p in P.glob('*.py'):ast.parse(p.read_text(),filename=str(p));python.append(p.name)
(E/'python-ast.json').write_text(json.dumps(dict(schemaVersion=1,files=sorted(python),passed=True,noImports=True),indent=2)+'\n')
print(json.dumps(dict(pure=json.loads((E/'pure.stdout.log').read_bytes()),source=json.loads((E/'source.stdout.log').read_bytes()),parseCommands=len(records)-2,pythonAstFiles=len(python))))
