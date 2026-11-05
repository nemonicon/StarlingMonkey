"""Own pure/DATA tests and pinned Node --check only. No operational entrypoint."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
D=Path(__file__).resolve().parent
assert not(D/'index.json').exists()
refs=json.loads((D/'references.json').read_bytes());node=refs['node'];p=Path(node['path']);h=hashlib.sha256()
with p.open('rb')as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
assert h.hexdigest()==node['sha256']and p.stat().st_size==node['bytes']
for k in('NODE_OPTIONS','NODE_PATH','LD_PRELOAD','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH'):assert not os.environ.get(k)
E=D/'evidence';E.mkdir()
def row(p):
 b=Path(p).read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def run(name,args):
 before=row(args[-1]);r=subprocess.run(args,cwd=D,capture_output=True,timeout=30);assert row(args[-1])==before
 (E/(name+'.stdout.json')).write_bytes(r.stdout);(E/(name+'.stderr.log')).write_bytes(r.stderr)
 terminal=dict(schemaVersion=1,argv=args,source=before,rawExitCode=r.returncode,stdoutBytes=len(r.stdout),stderrBytes=len(r.stderr),operationalEntrypointCalled=False,preflightWorkerLoaderGuestOrMeasurementCalled=False)
 (E/(name+'.terminal.json')).write_text(json.dumps(terminal,indent=2)+'\n');assert r.returncode==0 and not r.stderr
 return r
pure=json.loads(run('pure',[node['path'],str(D/'test-models.mjs')]).stdout)
data=json.loads(run('actual-data',[node['path'],str(D/'test-actual-data.mjs')]).stdout)
grammar=[]
for i,p in enumerate(sorted(D.glob('*.mjs'))):
 r=run('parse-'+str(i),[node['path'],'--check',str(p)]);assert not r.stdout;grammar.append(str(p))
summary=dict(schemaVersion=1,state='V5_SOURCE_PURE_DATA_AND_GRAMMAR_PASSED',pureChecks=pure['checks'],actualCalibrationCases=data['comparisonCases'],actualMatchedRows=data['recomputedMatchedRows'],actualPilotIndexRows=data['actualPilotIndexRows'],parserOnlyFiles=len(grammar),node=node,operationalEntrypointsCalled=False,preflightWorkerLoaderGuestOrMeasurementCalled=False)
(E/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
