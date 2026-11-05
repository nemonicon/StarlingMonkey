"""Capture one finite own SOURCE checker; never calls an operational entry."""
import hashlib,json,subprocess,sys
from pathlib import Path
OWN=Path(__file__).resolve().parent
def desc(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def main():
 out=OWN/'evidence/final';assert not out.exists();out.mkdir(parents=True)
 argv=[sys.executable,'-B','-I',str(OWN/'check-source.py')]
 result=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=900,check=False)
 for name,b in[('stdout.json',result.stdout),('stderr.log',result.stderr)]:
  with(out/name).open('xb')as f:f.write(b)
 terminal=dict(schemaVersion=1,argv=argv,rawExitCode=result.returncode,pidNotRetained=True,stdout=desc(out/'stdout.json'),stderr=desc(out/'stderr.log'),sourceCheckOnly=True,operationalHelperOrChildInvoked=False,engineExecuted=False)
 with(out/'terminal.json').open('x')as f:json.dump(terminal,f,indent=2);f.write('\n')
 assert result.returncode==0 and result.stderr==b''
 value=json.loads(result.stdout);assert value['sourceOnly']and value['freezerInvoked']is False and value['engineExecuted']is False
 with(out/'results.json').open('x')as f:json.dump(value,f,indent=2);f.write('\n')
 print(json.dumps(dict(terminal=desc(out/'terminal.json'),result=desc(out/'results.json'))))
if __name__=='__main__':main()
