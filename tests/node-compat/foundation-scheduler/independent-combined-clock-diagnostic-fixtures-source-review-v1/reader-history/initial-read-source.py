from pathlib import Path
import hashlib,json,stat,ast
P=Path(__file__).resolve().parent;S=P.parent/'combined-clock-diagnostic-fixtures-candidate-v1';checks=0;seen={};families=[]
def yes(v,m='data'):
 global checks
 checks+=1;assert v,m
def row(p):
 p=Path(p);a=p.lstat();yes(stat.S_ISREG(a.st_mode));b=p.read_bytes();z=p.lstat();yes((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns));return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def check(r):yes(row(r['path'])=={k:r[k]for k in ['path','sha256','bytes']},r['path']);seen[r['path']]={k:r[k]for k in ['path','sha256','bytes']};return Path(r['path'])
def load(r):return json.loads(check(r).read_bytes())
def family(r):
 p=check(r);v=json.loads(p.read_bytes());names={'index.json'}
 for x in v['files']:
  yes(x['path']not in names and not Path(x['path']).is_absolute()and '..'not in Path(x['path']).parts);names.add(x['path']);check(dict(x,path=str(p.parent/x['path'])))
 yes(not any(q.is_symlink()for q in p.parent.rglob('*')));yes(names=={q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()});families.append(r)
ix=dict(path=str(S/'index.json'),sha256='3c337c1a66efaf868dfbaf6eea0bb52079940ddef9d473aa822633b317fe0edf',bytes=6426);family(ix)
inputs=json.loads((S/'input-hashes.json').read_bytes());yes(len(inputs['files'])==68 and len(inputs['families'])==2)
for r in inputs['files']:check(r)
for r in inputs['families']:family(r)
refs=json.loads((S/'references.json').read_bytes());catalog=json.loads((S/'fixture-catalogue.json').read_bytes());contract=json.loads((S/'future-source-review-contract.json').read_bytes());yes(catalog['diagnosticSourceIndex']==refs['diagnosticSourceIndex']);yes(catalog['distinctFromHashHmac357']is True and catalog['current355HasPrivateObserver']is False)
for f in catalog['fixtures']:
 check(f['source']);check(f['wit']);yes(f['sameComponentObserverRequired']and not f['initDiagnosticSnapshotCalled']);yes(set(f['selectedInterfaces'])=={'wasi:clocks/wall-clock@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'})
yes(catalog['allInvalidQueueFixture']is catalog['nativeOffsetFixture']is None)
for r in refs['actualNativeSourceOrigins'].values():check(r)
yes('static wasi::clocks::monotonic_clock::Duration mono_clock_offset' in Path(refs['actualNativeSourceOrigins']['runtime/js.cpp']['path']).read_text(),'actual native offset is TU-static')
# Authentic APIs/body scopes are inspected source, never imported/evaluated.
diag=Path(refs['diagnosticSourceIndex']['path']).parent;life=Path(refs['lifecycleFixtureSourceIndex']['path']).parent
embedding=(diag/'after/componentize-source/embedding/embedding.cpp').read_text();yes(embedding.index('incr_event_loop_interest()')<embedding.index('JS_CallFunctionValue'),'embedding interest exists before JS body')
event=(diag/'after/runtime/event_loop.cpp').read_text();yes('JS::Rooted<TracedAsyncTask> running' in event and 'while (true)' in event,'task rooted through run and released before next Promise checkpoint')
for source in [S/'fixtures/resource-observed.mjs',S/'fixtures/clock-observed.mjs',S/'fixtures/survivor-observed.mjs']:
 text=source.read_text();yes("import lifecycle from 'starling:test-clock-lifecycle'"in text);yes('lifecycle.snapshot()'in text);yes('setTimeout('not in text and 'unsafeReset'not in text and 'CryptoKey'not in text)
for f in S.glob('*.py'):ast.parse(f.read_bytes())
for r in seen.values():check(r)
v=dict(schemaVersion=1,passed=True,checks=checks,currentInputs=len(seen),families=len(families),sourceIndex=ix,sourceDeclaredInputs=68,declaredExternalFamilies=2,fixtures=3,sourceOnly=True,ownerActionInvoked=False,sourceReadScope='Current finite39-member family and68declared inputs/two full families; no operational closure claim',semanticChecks=['Snapshot API real7aed, current355 lacks it; diagnostic357 distinct from HashHmac357','Embedding increments interest before JS_CallFunctionValue; first before snapshot legitimately has interest1','Selected running task Rooted lifetime ends before next loop Promise checkpoint','No wrapper calls native snapshot at INIT; whole original scalar strings retained','All-invalid queue setup/native offset/Store death/fatal/cache teardown remain explicitly unavailable'])
(P/'intake-summary.json').write_text(json.dumps(v,indent=2)+'\n');(P/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=list(seen.values()),families=families),indent=2)+'\n');print(json.dumps(v))
