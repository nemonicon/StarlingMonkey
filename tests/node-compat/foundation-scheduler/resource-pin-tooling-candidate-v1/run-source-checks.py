"""Only preparation read/hash, extracted DATA tests and grammar. Fresh output required."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys,time
OWN=Path(__file__).resolve().parent
def record(path):
 raw=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def run(output):
 assert output.is_absolute()and str(output)==str(output.resolve())
 assert not(OWN/'index.json').exists()or not output.is_relative_to(OWN),'Sealed source must not receive evidence writes'
 output.mkdir(parents=True,exist_ok=False);refs=json.loads((OWN/'references.json').read_bytes())
 for key in('node','python'):
  assert record(Path(refs[key]['path']))==refs[key]
 commands=[('source',[refs['python']['path'],'-B',str(OWN/'check-source.py'),str(output/'source-results.json')]),('descriptor-pure',[refs['node']['path'],str(OWN/'test-descriptor-pure.mjs')])]
 for name in('bootstrap.mjs','test-descriptor-pure.mjs'):commands.append(('grammar-'+name,[refs['node']['path'],'--check',str(OWN/name)]))
 terminals=[]
 for name,argv in commands:
  start=time.monotonic();child=subprocess.run(argv,cwd=str(OWN.parents[3]),capture_output=True,timeout=120)
  rows=[]
  for suffix,raw in(('stdout',child.stdout),('stderr',child.stderr)):
   path=output/(name+'.'+suffix+'.log');path.write_bytes(raw);rows.append(record(path))
  terminal=dict(schemaVersion=1,name=name,command=argv,exitCode=child.returncode,seconds=time.monotonic()-start,streams=rows,scope='source/read-hash/extracted-DATA/grammar only')
  (output/(name+'.terminal.json')).write_text(json.dumps(terminal,indent=2)+'\n');terminals.append(terminal)
 ast_files=[]
 for path in sorted(OWN.glob('*.py')):ast.parse(path.read_bytes(),filename=str(path));ast_files.append(record(path))
 result=dict(schemaVersion=1,state='RESOURCE342_PIN_TOOLING_PREPARATION_CHECKS_PASSED_V1'if all(t['exitCode']==0 for t in terminals)else'RESOURCE342_PIN_TOOLING_PREPARATION_CHECKS_FAILED_V1',terminals=terminals,pythonAstFiles=ast_files,sourceOnly=True,ownerGuardOrActionOrVerifierImported=False,exportOrBootstrapActionsInvoked=False,engineComponentGuestKeyGcOrHostActionsInvoked=False)
 (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(state=result['state'],output=str(output),exitCodes=[t['exitCode']for t in terminals],pythonAstFiles=len(ast_files))))
 return 0 if all(t['exitCode']==0 for t in terminals)else 1
if __name__=='__main__':assert len(sys.argv)==2;raise SystemExit(run(Path(sys.argv[1])))
