"""Pinned static component decoder only. Does not instantiate a component."""
from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
d=json.loads((P/'data-results.json').read_bytes());root=json.loads(Path(d['rootResult']['path']).read_bytes());tool={k:root['clockDependency']['tool'][k]for k in ['path','sha256','bytes']}
assert row(tool['path'])==tool and row(root['component']['path'])==root['component']
records=[]
for name,args,expected in [('wit',['component','wit',root['component']['path']],root['emittedWit']),('typegraph',['component','wit','--json',root['component']['path']],root['typeGraph'])]:
 argv=[tool['path'],*args];r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,env={'PATH':'/usr/bin:/bin'})
 stdout=P/('fresh-'+name+'.stdout');stderr=P/('fresh-'+name+'.stderr');stdout.write_bytes(r.stdout);stderr.write_bytes(r.stderr)
 records.append(dict(name=name,argv=argv,rawExitCode=r.returncode,stdout=row(stdout),stderr=row(stderr),timeoutSeconds=60,staticOnly=True,componentInstantiated=False))
 (P/'static-decode-terminals.json').write_text(json.dumps(dict(schemaVersion=1,tool=tool,records=records,ownerHelpersGuestOrHostInvoked=False),indent=2)+'\n')
 assert r.returncode==0 and r.stderr==b'',(name,r.returncode,r.stderr.decode())
 retained=Path(expected['path']).read_bytes()
 if name=='wit':
  assert r.stdout[:len(retained)]==retained and r.stdout[len(retained):].startswith(b'package wasi:io@0.2.10 {'), 'fresh root WIT is not retained root world plus definitions'
 else:
  assert json.loads(r.stdout)==json.loads(retained), 'full fresh JSON type graph differs from retained data'
assert row(tool['path'])==tool and row(root['component']['path'])==root['component']
print(json.dumps(dict(freshStaticWitAndJsonTypeGraphPassed=True,actualNewComponentDecoded=True,rootWorldBytesMatch=True,fullTypeGraphValuesMatch=True,guestOrHostInvoked=False)))
