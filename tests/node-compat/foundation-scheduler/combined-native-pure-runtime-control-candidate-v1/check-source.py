"""Finite current Source/DATA/hash/AST checks only, never an operational import."""
from pathlib import Path
import ast,hashlib,json,os,stat
OWN=Path(__file__).resolve().parent;seen={};ids={};families={};checks=0
def need(v,m):
 global checks
 checks+=1
 if not v:raise AssertionError(m)
def check(r):
 p=Path(r['path']);s=p.lstat();key=(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_nlink,s.st_mtime_ns,s.st_ctime_ns)
 need(p.is_absolute()and stat.S_ISREG(s.st_mode)and s.st_size==r['bytes'],'ordinary input')
 simple={k:r[k]for k in ['path','sha256','bytes']}
 if str(p)in seen:need(seen[str(p)]==simple and ids[str(p)]==key,'unchanged duplicate');return
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.lstat();need(h.hexdigest()==r['sha256']and key==(z.st_dev,z.st_ino,z.st_size,z.st_mode,z.st_nlink,z.st_mtime_ns,z.st_ctime_ns),'full stable input hash')
 seen[str(p)]=simple;ids[str(p)]=key
def read(r):check(r);return json.loads(Path(r['path']).read_bytes())
def family(ix):
 if ix['path']in families:need(families[ix['path']]==ix,'same family');return
 v=read(ix);base=Path(ix['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique relative family member');names.add(n);check(dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']))
 need(not any(p.is_symlink()for p in base.rglob('*'))and {p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'whole exact family');families[ix['path']]=ix
refs=json.loads((OWN/'references.json').read_bytes());inputs=json.loads((OWN/'source-inputs.json').read_bytes())
for r in inputs['files']:check(r)
for ix in inputs['families']:family(ix)
proof=read(refs['actualPureReview']['result']);contract=read(refs['actualPureContract'])
need(contract['requiredReviewState']==proof['state'],'exact actual artifact contract state')
for k,v in contract['requiredFixedValues'].items():need(proof[k]==v and type(proof[k])is type(v),'actual fixed artifact value '+k)
need(proof['publicAbiSignatures']==[{'name':'run','params':[],'result':'string'}],'actual scalar signature')
art=proof['artifacts'];ix=read(art['constructionIndex']);base=Path(art['constructionIndex']['path']).parent;actual_names={'index.json','completion.json'}
need(len(ix['files'])==18,'actual per-pure producer18 indexed')
for r in ix['files']:
 actual_names.add(r['path']);check(dict(path=str(base/r['path']),sha256=r['sha256'],bytes=r['bytes']));z=(base/r['path']).lstat();need(stat.S_IMODE(z.st_mode)==0o600 and z.st_nlink==1,'actual private artifact file')
check(art['constructionCompletion']);need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==actual_names,'current exact original publication')
for d in [base]+[p for p in base.rglob('*')if p.is_dir()]:need(not d.is_symlink()and stat.S_IMODE(d.lstat().st_mode)==0o700,'actual artifact directory mode')
boundary=read(inputs['parentOnlyBoundary'])
for r in boundary['files']:check(r)
for ix in boundary['families']:family(ix)
for b in boundary['boundaries']:
 v=read(b['manifest']);need(len(v[b['field']])==b['expectedRows'],'finite parent boundary')
 for r in v[b['field']]:check(r)
 for ix in v.get(b['familyField'],[]):family(ix)
inventory=read(refs['packageInventory'])['package'];root=Path(inventory['root']);need(len(inventory['files'])==4889 and len(inventory['links'])==21,'full package roles')
names=set();links={r['path']:r for r in inventory['links']}
for r in inventory['files']:
 check(r);p=Path(r['path']);need(p==root/r['relativePath']and stat.S_IMODE(p.lstat().st_mode)==r['mode']and p.lstat().st_nlink==1,'package role/mode');names.add(r['relativePath'])
actual=set()
for p in root.rglob('*'):
 n=p.relative_to(root).as_posix()
 if p.is_symlink():
  r=links[n];need(os.readlink(p)==r['target']and str(p.resolve(strict=True))==r['resolvedPath']and p.resolve(strict=True).is_relative_to(root),'package alias');actual.add(n)
 elif p.is_file():need(n in names,'package file');actual.add(n)
need(actual==names|set(links),'package complete membership')
entry=(OWN/'entry.mjs').read_text();body=(OWN/'body.mjs').read_text();worker=(OWN/'worker.mjs').read_text();external=(OWN/'external.py').read_text();capture=(OWN/'capture.mjs').read_text()
need("const ORIGINAL='"+str(OWN)+"'"in entry and "OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-pure-runtime-control-candidate-v1'"in external,'actual own constants')
need(entry.index("const f=await authenticate(configDescriptor,'parent')")<entry.index('const api=await import('),'full own guard before custom imports')
need('record=await api.combinedNativeBootstrapPreflight({configDescriptor:f.refs.readOnlyConfig})'in entry and entry.count('record=await api.combinedNativeBootstrapPreflight')==1,'one genuine parent API call site')
child=entry.split('export async function runPureChild',1)[1];need('combinedNativeBootstrapPreflight('not in child,'no child native API')
need('await boundary(c,inputs.parentOnlyBoundary)'in entry and 'if(role===\'parent\')'in entry,'explicit child versus full-parent auth')
need("model.nativeRecordModel(record,f.refs,metadata,data.bootstrap,data)"in entry and 'try{await record.recheck();}'in entry,'whole full80 record and fresh own recheck')
need('await registerPartial(out,mode)'in body and body.index('await registerPartial(out,mode)')<body.index('terminalModel(t)'),'partial registry before terminal assertions')
need('await mkdir(join(out.root,\'processes\'),{mode:0o700})'in body and 'await mkdir(join(out.root,\'sessions\'),{mode:0o700})'in body,'real donor directory preconditions')
need("['run','--invoke','run()',f.refs.component.path]"in body and 'timeoutMs:60000'in body,'actual pinned CLI and child deadline')
need('ordinaryPureRunInvoked:true'in body and 'allSixFixtureGateComplete:false'in body and 'fullSeventeenGateComplete:false'in body,'preliminary pure only')
need('Object.entries(contract.requiredFixedValues??{})'in entry and 'Exact actual zero-argument string scalar ABI'in entry,'executable complete artifact contract')
need('await publication(c,p.artifacts.constructionIndex' in entry and 'Artifact directory identity/mode unchanged'in entry,'before/final exact artifact modes/identities/membership')
need('value=invoke()'in capture and capture.index("await write('raw/")<capture.index("need(typeof value==='string'"),'typed raw before string assertions')
need('if(thrown)throw value;throw captureError;'in capture,'combined throw+write failure preserves original')
need('const ns=await import('in worker and 'namespaceModel(ns' in worker and 'childNativeApiInvocations:0'in worker,'real original ESM import; no counterfeit child native frame')
need('loadToolchain('not in entry+body+worker and 'componentize('not in entry+body+worker and 'transpile('not in entry+body+worker,'no build/map/package action')
need('monitor.monitor(argv,str(REPO),env,output,1200,root_row)'in external and external.index('recheck();output=Path')<external.index('terminal=monitor.monitor'),'real six-argument original monitor')
need((OWN/'wave.mjs').read_bytes()==Path(refs['waveDonor']['path']).read_bytes(),'actual WAVE module exact bytes')
py=0
for p in OWN.glob('*.py'):ast.parse(p.read_text(),filename=str(p));py+=1
for p,i in ids.items():
 z=Path(p).lstat();need(i==(z.st_dev,z.st_ino,z.st_size,z.st_mode,z.st_nlink,z.st_mtime_ns,z.st_ctime_ns),'final current input identity')
for p in [Path(refs['outputRoot']),Path(refs['outputRoot']+'-external-root')]:need(not p.exists()and not p.is_symlink(),'future output roots absent')
report={'schemaVersion':1,'passed':True,'checks':checks,'fullHashFiles':len(seen),'logicalBytes':sum(r['bytes']for r in seen.values()),'families':len(families),'parentBoundary':inputs['parentOnlyBoundary'],'childDirectFiles':len(inputs['files']),'packageFiles':4889,'packageAliases':21,'pythonAstChecks':py,'nativeApiOrOwnedWorkloadOrFixtureInvoked':False}
(OWN/'source-check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
