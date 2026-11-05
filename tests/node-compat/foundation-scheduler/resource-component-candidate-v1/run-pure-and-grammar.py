"""Only own IO-free models and pinned Node --check. Never imports action code."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
OWN=Path(__file__).resolve().parent
assert OWN==Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/resource-component-candidate-v1')
assert not(OWN/'index.json').exists()
refs=json.loads((OWN/'references.json').read_bytes());node=refs['node'];p=Path(node['path']);h=hashlib.sha256()
with p.open('rb')as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
assert h.hexdigest()==node['sha256']and p.stat().st_size==node['bytes']
for k in('NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','LD_PRELOAD','LD_LIBRARY_PATH'):assert not os.environ.get(k)
root=OWN/'evidence';root.mkdir()
def run(label,args):
 source=Path(args[-1]);before=source.read_bytes();source_row=dict(path=str(source),sha256=hashlib.sha256(before).hexdigest(),bytes=len(before))
 r=subprocess.run(args,cwd=OWN,capture_output=True,timeout=30)
 assert source.read_bytes()==before
 (root/(label+'.stdout.log')).write_bytes(r.stdout);(root/(label+'.stderr.log')).write_bytes(r.stderr)
 value=dict(schemaVersion=1,argv=args,source=source_row,rawExitCode=r.returncode,stdoutBytes=len(r.stdout),stderrBytes=len(r.stderr),syntaxOrOwnPureModelsOnly=True,ownerHelpersOrBootstrapOrPackagerOrGuestInvoked=False)
 (root/(label+'.terminal.json')).write_text(json.dumps(value,indent=2)+'\n')
 assert r.returncode==0 and not r.stderr
 return r,value
r,pure=run('pure',[node['path'],str(OWN/'test-models.mjs')]);v=json.loads(r.stdout);assert v['state']=='PURE_RESOURCE_COMPONENT_MODELS_PASSED_V1'and v['syntheticOnly']is True
grammar=[]
for i,p in enumerate(sorted(OWN.rglob('*.mjs'))):
 r,terminal=run('parse-'+str(i),[node['path'],'--check',str(p)]);assert not r.stdout;grammar.append(terminal)
summary=dict(schemaVersion=1,state='RESOURCE_COMPONENT_PURE_AND_GRAMMAR_PASSED_V1',pureModelChecks=v['checks'],parseOnlyCommands=len(grammar),node=node,allRawExitCodesZero=True,stderrBytes=0,helperOrBootstrapOrJcoOrSplicerOrCompilerOrComponentOrGuestOrClockActionsInvoked=False)
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
