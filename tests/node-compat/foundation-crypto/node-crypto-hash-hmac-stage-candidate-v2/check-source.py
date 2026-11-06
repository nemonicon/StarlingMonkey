"""Source/read/hash/AST only. Never Git, authorize, monitor or stage."""
import ast,hashlib,json,os,stat
from pathlib import Path
OWN=Path(__file__).resolve().parent;V1=OWN.parent/'node-crypto-hash-hmac-stage-candidate-v1';assert not(OWN/'index.json').exists();checks=0

def ok(v,label):
 global checks
 assert v,label;checks+=1

def read(n):return json.loads((OWN/n).read_bytes())
def measured(path):
 p=Path(path);a=p.lstat();ok(stat.S_ISREG(a.st_mode),'regular input');h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.lstat();identity=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns);ok(identity(a)==identity(z),'stable current input')
 return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z)

inputs=read('input-hashes.json');refs=read('references.json');seen={}
ok(len(inputs['files'])==refs['declaredCurrentInputRows']==2779,'actual full current boundary count')
for r in inputs['files']:
 actual,identity=measured(r['path']);ok(actual==r,'current exact hash');seen[r['path']]=(r,identity)
for ix in inputs['families']:
 root=Path(ix['path']).parent;v=json.loads(Path(ix['path']).read_bytes());names={'index.json'}
 for r in v['files']:
  n=r['path'];ok(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'confined family member');names.add(n);ok(seen[str(root/n)][0]==dict(r,path=str(root/n)),'indexed member authenticated')
 ok(not any(p.is_symlink()for p in root.rglob('*'))and{str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==names,'complete actual family')
ok(len(inputs['families'])==13,'all13 Source/peer/ancestry families')
plan=read('stage-copy-plan.json');ok((OWN/'stage-copy-plan.json').read_bytes()==(V1/'stage-copy-plan.json').read_bytes(),'whole1642+3plan unchanged')
ok(len(plan['files'])==len({r['path']for r in plan['files']})==1642 and len(plan['embeddingData'])==3,'exact physical roles')
for row in plan['files']+plan['embeddingData']:ok(seen[row['original']][0]==dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']),'all original copy roles covered')
derive=read('v2-derivation.json');code=(OWN/'controller.py').read_text();reversed_code=code
for e in reversed(derive['edits']):
 ok(len(e['afterPositions'])==e['count'],'exact edit positions')
 for pos in reversed(e['afterPositions']):
  ok(reversed_code[pos:pos+len(e['after'])]==e['after'],'exact derived Source span');reversed_code=reversed_code[:pos]+e['before']+reversed_code[pos+len(e['after']):]
ok(reversed_code==(V1/'controller.py').read_text()and len(derive['edits'])==27,'whole27-step reversal to immutable2395')
tree=ast.parse(code);defs={n.name:ast.get_source_segment(code,n)for n in tree.body if isinstance(n,ast.FunctionDef)}
ok("OWN=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v2'"in code,'actual genuine V2 OWN')
ok("SOURCE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'"in code,'actual7c5a native Source unchanged')
ok('SOURCE_STAGE_V2' in code and'STAGE_SOURCE_REVIEW_PASSED_V2'in code,'new Root/peer states')
ok('globals()['not in code and'setattr('not in code and'.__dict__'not in code,'no namespace rebinding')
ok("'clone','--no-local'"not in code and"'--unshallow'"not in code,'no history-copy/fallback path')
ok("'fetch','--no-tags','--depth=1','--no-recurse-submodules','--no-auto-maintenance','--no-write-commit-graph'"in defs['initial_git_commands'],'explicit native fetch policy')
ok("REPO.as_uri(),BASE"in defs['initial_git_commands'],'only fixed local Repo literalBASE requested')
ok("shlex.join"in defs['upload_pack_command']and"uploadpack.allowAnySHA1InWant=true"in defs['upload_pack_command'],'quoted explicit server command, not original config mutation')
ok("'--no-replace-objects'"in defs['git_prefix'],'no replacement-object semantics')
ok("cwd=git_policy()['commandCwd']"in defs['command'],'private cwd before all Git commands')
ok('GIT_CONFIG_GLOBAL' in defs['git_environment']and"'/dev/null'"in defs['git_environment']and'BASH_FUNC_'in defs['git_environment'],'global/system/config-prefix/shell startup controls')
ok("['HOME','home','CODEX_HOME']"in defs['git_environment'],'user home values preserved')
ok("valuesRecorded=False"in defs['git_environment_fact'],'removed names only')
ok('assert_private_git_policy()'in defs['command'],'empty template/hooks checked before each command')
ok("b'1\\n'"in defs['baseline_git_observation']and'assert not references'in defs['baseline_git_observation'],'real reachable-count and no-ref checks')
ok('transientPackByteCapClaim=False'in defs['git_policy']and'exactPackObjectSetClaim=False'in defs['baseline_git_observation'],'honest pack-byte/object scope')
ok("value['baselineGitPolicy']==refs['baselineGitPolicy']==git_policy()"in defs['root_model'],'issued Root binds full Git policy')
ok("len(expected)==8"in defs['journal_model'],'all8 raw Git commands required')
ok("result['stagedGitObjects']=git_objects(DEST)"in defs['stage'],'full resulting Git object hash/byte inventory retained')
ok("source_config=descriptor(REPO/'.git/config')"in defs['authorize']and"unique[source_config['path']]==source_config"in defs['authorize'],'original config current read-only identity without hiding declared row')
ok(defs['main'].index('frame=authorize')<defs['main'].index('spec=importlib.util')<defs['main'].index('OUT.mkdir'),'full guard before custom monitor/mutation')
ok("module.monitor(argv,str(REPO),"in defs['main']and",OUT,TIMEOUT,frame['config']['rootAuthority'])"in defs['main'],'same genuine sixarg0af600')
for name in ['merge_rows','baseline_preimage','observe_partial','private_parents','recheck']:
 v1text=(V1/'controller.py').read_text();n=next(n for n in ast.parse(v1text).body if isinstance(n,ast.FunctionDef)and n.name==name);v1func=ast.get_source_segment(v1text,n)
 if name=='baseline_preimage':v1func=v1func.replace('fresh-clone, Git-byte-identical','fresh-checkout, Git-byte-identical').replace('ownedFreshCloneOnly=True','ownedFreshBaselineCheckoutOnly=True')
 ok(defs[name]==v1func,'unchanged copy/retention/protection API '+name)
ok("target.unlink()"in defs['stage']and'baseline_preimage(target'in defs['stage']and'durable(target,data)'in defs['stage'],'Git-byte checked authorized baseline overlay retained')
ok("result['partialEmbeddingData']"in defs['stage']and"result['partialTargets']"in defs['stage']and'if final_failure is not None:raise final_failure'in defs['stage'],'partial/final failure refusal preserved')
evidence=read('history-and-git-isolation-evidence.json');ok(evidence['rootProvenanceGitOperations']==['diff --binary HEAD','rev-parse HEAD'],'named producer HEAD/tree-only evidence')
ok(evidence['nativeSourceFilesInspected']==357 and evidence['rootRepositoryHistoryRequiredByInspectedCode']is False,'bounded Source history finding')
ok(evidence['configurationValuesRecorded']is False,'no Git config secrets copied')
root=read('root-authority.template.json');cfg=read('config.template.json');ok(root['state'].startswith('UNISSUED')and cfg['state'].startswith('UNISSUED')and root['sourceStageAllowed']is False,'no action grant')
for k in ['stageControllerIndex','stageControllerEntry','stageControllerReview','gitBinary','pythonExecutable','actualStageResult','actualStageReview','actualBuildResult','reviewedNativePins','runtimeAuthority']:ok(root[k]is None,'closed new Root slot '+k)
for k in ['configuredSourceRoot','workRoot','freezeRoot','externalOutputRoot','stageJournal']:ok(not os.path.lexists(refs[k]),'future fixed roots absent')
asts=0
for p in OWN.glob('*.py'):ast.parse(p.read_text(),filename=str(p));asts+=1
for p in OWN.glob('*.py.txt'):ast.parse(p.read_text(),filename=str(p));asts+=1
for path,(row,identity)in seen.items():actual,after=measured(path);ok(actual==row and identity==after,'final original bytes/modes/inodes')
result=dict(schemaVersion=1,state='HASH_HMAC357_STAGE_V2_SOURCE_BOUNDARY_PASSED',checks=checks,currentInputFiles=len(seen),completeFamilies=13,sourceCopies=1642,embeddingDataCopies=3,exactSourceEdits=27,pythonAstUnits=asts,authorizeInvoked=False,stageInvoked=False,gitInvoked=False,monitorInvoked=False,nativeHelperImported=False,nativeBuildInvoked=False,engineExecuted=False,cryptoOperationsInvoked=False)
(OWN/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
