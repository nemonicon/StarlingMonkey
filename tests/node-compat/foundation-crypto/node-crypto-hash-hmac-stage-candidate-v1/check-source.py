"""Whole current Source boundary/read/hash/AST only. No stage/authorize/Git."""
import ast,hashlib,json,os,stat
from pathlib import Path
OWN=Path(__file__).resolve().parent;assert not(OWN/'index.json').exists();checks=0

def ok(v,m):
 global checks
 assert v,m;checks+=1

def desc(path):
 p=Path(path);a=p.lstat();ok(stat.S_ISREG(a.st_mode),'regular typed input');h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.lstat();before=(a.st_dev,a.st_ino,a.st_mode,a.st_nlink,a.st_size,a.st_mtime_ns,a.st_ctime_ns);after=(z.st_dev,z.st_ino,z.st_mode,z.st_nlink,z.st_size,z.st_mtime_ns,z.st_ctime_ns);ok(before==after,'stable input')
 return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),after

v=json.loads((OWN/'input-hashes.json').read_bytes());refs=json.loads((OWN/'references.json').read_bytes());original={}
ok(len(v['files'])==refs['declaredCurrentInputRows']==2723,'exact current original boundary')
for r in v['files']:
 actual,identity=desc(r['path']);ok(actual==r,'declared hash/size');original[r['path']]=(r,identity)
for ix in v['families']:
 value=json.loads(Path(ix['path']).read_bytes());root=Path(ix['path']).parent;names={'index.json'}
 for row in value['files']:
  n=row['path'];ok(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'confined unique family');names.add(n)
  r=dict(row,path=str(root/n));ok(original[r['path']][0]==r,'indexed member authenticated')
 ok(not any(p.is_symlink()for p in root.rglob('*'))and{str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==names,'complete actual family')
source=Path(refs['integrationIndex']['path']).parent;p=json.loads((source/'stage-input-plan.json').read_bytes());ix=json.loads((source/'index.json').read_bytes())
source_rows=[refs['integrationIndex']]+[dict(r,path=str(source/r['path']))for r in ix['files']]
plan=json.loads((OWN/'stage-copy-plan.json').read_bytes());mapping={}
for row in p['files']:
 mapping[row['path']]=dict(path=row['path'],original=row['original'],sha256=row['sha256'],bytes=row['bytes'],sourceMode=stat.S_IMODE(Path(row['original']).stat().st_mode),targetMode=0o600,roles=sorted([row.get('role','GENUINE_DONOR_TOOL_DATA'),'EXACT_7C5A_STAGE_PLAN_ROW']))
for row in source_rows:
 name=str(Path(row['path']).relative_to(OWN.parents[3]));fresh=dict(path=name,original=row['path'],sha256=row['sha256'],bytes=row['bytes'],sourceMode=stat.S_IMODE(Path(row['path']).stat().st_mode),targetMode=0o600,roles=['SEALED_7C5A_FAMILY_STAGED_DATA_ACTIVE_PRODUCER_REMAINS_ORIGINAL'])
 if name in mapping:
  old=mapping[name];ok(all(old[k]==fresh[k]for k in['original','sha256','bytes','sourceMode','targetMode']),'only identical dedup');old['roles']=sorted(set(old['roles']+fresh['roles']))
 else:mapping[name]=fresh
ok(plan['files']==[mapping[k]for k in sorted(mapping)]and len(mapping)==1642,'actual unique destination union')
ok(len(plan['embeddingData'])==3 and plan['totalPhysicalCopies']==1645,'separate embedding DATA3')
for row in plan['files']+plan['embeddingData']:
 ok(original[row['original']][0]==dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']),'every actual copy origin authenticated')
 ok(row['targetMode']==0o600,'new target600 distinct original source mode')
for path in [refs[k]for k in['configuredSourceRoot','workRoot','freezeRoot','externalOutputRoot','stageJournal']]:ok(not os.path.lexists(path),'future root absent')
code=(OWN/'controller.py').read_text();tree=ast.parse(code);own_defs={x.name:ast.get_source_segment(code,x)for x in tree.body if isinstance(x,ast.FunctionDef)}
derive=json.loads((OWN/'generic-derivation.json').read_bytes());donor=Path(derive['donor']['path']).read_text();donor_defs={x.name:ast.get_source_segment(donor,x)for x in ast.parse(donor).body if isinstance(x,ast.FunctionDef)}
for row in derive['definitions']:
 ok(hashlib.sha256(donor_defs[row['name']].encode()).hexdigest()==row['beforeSha256'],'actual primitive donor bytes')
 ok(hashlib.sha256(own_defs[row['name']].encode()).hexdigest()==row['afterSha256'],'actual own primitive bytes')
ok(sum(x['unchanged']for x in derive['definitions'])==12 and len(derive['definitions'])==13,'twelve exact primitives and canonical checked variant')
body=(OWN/'stage-body.py.txt').read_text();ok(code.endswith(body),'whole actual own stage body')
for name in ['authorize','stage','main','root_model','source_peer_model','stage_peer_model','merge_rows','expected_plan','parse_tree','baseline_preimage','git_objects','recheck']:ok(name in own_defs,'concrete own API '+name)
ok("OWN=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v1'"in code,'genuine actual OWN')
ok("SOURCE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'"in code,'actual7c5a Source pin')
ok('BASE='+repr('54b3329b3ce818fd1f244e871e9c259b63667cda')in code,'genuine baseline54b')
ok('module.monitor(argv,str(REPO),'in code and ",OUT,TIMEOUT,frame['config']['rootAuthority'])"in code,'real original six-argument monitor API')
monitor=ast.parse(Path(refs['monitorEntry']['path']).read_text());fn=next(x for x in monitor.body if isinstance(x,ast.FunctionDef)and x.name=='monitor');ok(len(fn.args.args)==6,'actual monitor six arguments')
ok("for ix in inputs['families']"in own_defs['authorize']and"source_peer_model"in own_defs['authorize']and"stage_peer_model"in own_defs['authorize'],'own/native peer and family before phase')
ok(own_defs['main'].index('frame=authorize')<own_defs['main'].index('spec=importlib.util')<own_defs['main'].index('OUT.mkdir'),'full admission before custom monitor import or mutation')
ok('target.unlink()'in own_defs['stage']and"baseline_preimage(target"in own_defs['stage']and'durable(target,data)'in own_defs['stage'],'checked clone baseline replaced exclusively')
ok("'wb'"not in code and"Path(path).open('xb')"in code,'no write-truncation path')
ok("git_blob_id(data)==item['object']"in own_defs['baseline_preimage'],'actual Git-content preimage proof')
ok("'--no-local','--no-checkout'"in code and"'checkout','--detach',BASE"in code and"'ls-tree','-r','-z','--full-tree',BASE"in code,'genuine fixed Git APIs')
ok("'cat-file','blob',item['object']"in code and"consumedBySourceOrTools=False"in code,'genuine doclink blob proof not consumed Source')
ok("copiedSourceFiles=1642"in code and"copiedEmbeddingDataFiles=3"in code,'honest split target counts')
ok("result['partialEmbeddingData']"in code and"result['partialTargets']"in code,'both partial copy roots retained')
ok("result['finalInputProtectionPassed']"in code and"result['finalOriginalGitProtectionPassed']"in code and'if final_failure is not None:raise final_failure'in code,'final failures retain failed state and refuse success')
ok("frame['originalStats']"in own_defs['recheck']and'git_objects(REPO)==original_git'in code,'before/final bytes modes inodes and Git hashes')
ok('setattr('not in code and'.__dict__'not in code and'globals()['not in code,'no namespace/global rebinding')
for name in ['root-authority.template.json','config.template.json']:
 value=json.loads((OWN/name).read_bytes());ok(value['state'].startswith('UNISSUED_'),'no issued action')
root=json.loads((OWN/'root-authority.template.json').read_bytes());ok(root['sourceStageAllowed']is False,'source stage unissued')
for k in ['stageControllerIndex','stageControllerEntry','stageControllerReview','gitBinary','pythonExecutable','actualStageResult','actualStageReview','actualBuildResult','reviewedNativePins','runtimeAuthority']:ok(root[k]is None,'closed Root slot '+k)
asts=0
for p in OWN.glob('*.py'):ast.parse(p.read_text(),filename=str(p));asts+=1
ast.parse(body,filename='stage-body.py.txt');asts+=1
for path,(row,identity)in original.items():actual,after=desc(path);ok(actual==row and identity==after,'final original bytes/modes/inodes unchanged')
result=dict(schemaVersion=1,state='HASH_HMAC357_STAGE_SOURCE_BOUNDARY_PASSED',checks=checks,currentInputFiles=len(original),completeFamilies=len(v['families']),sourceCopies=1642,embeddingDataCopies=3,pythonAstUnits=asts,genuineUnmodifiedPrimitives=12,derivedCanonicalPrimitive=1,authorizeInvoked=False,monitorInvoked=False,gitInvoked=False,stageInvoked=False,nativeHelperImported=False,nativeBuildInvoked=False,engineExecuted=False,cryptoOperationsInvoked=False)
(OWN/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
