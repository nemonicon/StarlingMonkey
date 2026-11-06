"""Independent bounded SOURCE/DATA intake, no operational imports or calls."""
from pathlib import Path
import ast,hashlib,json,os,re,stat,subprocess,time
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'node-crypto-hash-hmac-stage-candidate-v1'
EXPECTED='2395af2c6807953fb32173cd8c7f63b4f1f379360f991e2bb39dff87153620c0'
rows={};identities={};families={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def digest(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def descriptor(path):return dict(path=str(path),sha256=digest(path),bytes=path.stat().st_size)
def key(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_nlink,s.st_mtime_ns,s.st_ctime_ns)
def checked(r):
 need(type(r)is dict and type(r['path'])is str and Path(r['path']).is_absolute(),'absolute descriptor')
 p=Path(r['path']);s=p.lstat();need(stat.S_ISREG(s.st_mode)and s.st_size==r['bytes'],'regular exact file')
 if str(p)in rows:
  need(rows[str(p)]==r and identities[str(p)]==key(s),'same descriptor/identity');return p
 need(digest(p)==r['sha256']and key(s)==key(p.lstat()),'full stable SHA '+str(p))
 rows[str(p)]=r;identities[str(p)]=key(s);return p
def read(r):return json.loads(checked(r).read_bytes())
def family(ix):
 if ix['path']in families:need(families[ix['path']]==ix,'same family');return
 v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique member')
  names.add(n);checked(dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']))
 paths=list(root.rglob('*'));need(not any(p.is_symlink()for p in paths),'no family symlinks')
 need({p.relative_to(root).as_posix()for p in paths if p.is_file()}==names,'exact whole indexed family')
 families[ix['path']]=ix

source_index=descriptor(SOURCE/'index.json');need(source_index['sha256']==EXPECTED and source_index['bytes']==4708,'genuine final stage Source pin');family(source_index)
refs=read(descriptor(SOURCE/'references.json'));inputs=read(descriptor(SOURCE/'input-hashes.json'));need(len(inputs['files'])==refs['declaredCurrentInputRows']==2723 and len(inputs['families'])==11,'finite exact declared current2723/11 inputs')
for r in inputs['files']:checked(r)
for r in inputs['families']:family(r)
family(refs['integrationIndex']);need(refs['integrationIndex']['sha256']=='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429','real357 integration7c5a')
family(refs['actualIntegrationSourceReview']['index']);peer=read(refs['actualIntegrationSourceReview']['result']);pc=read(refs['actualIntegrationSourceReviewContract']);need(peer['state']==pc['requiredReviewState'],'actual integration Source peer contract state')
need(peer['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==refs['integrationIndex']['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True,'genuine independent integration Source wire')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for k,v in pc.get(group,{}).items():need(peer[k]==v,'actual0a7 contract '+k)
for k,v in [('nativeSourceFiles',357),('retainedParentNativeFiles',353),('changedParentNativeFiles',2),('newNativeFiles',2),('externalEmbeddingSources',3),('selectedManifestCount',12)]:need(peer[k]==v,'new357 initial lineage '+k)
family(refs['monitorIndex']);need(refs['monitorIndex']['sha256']=='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b','real original0af')
monitor=checked(refs['monitorEntry']);mt=ast.parse(monitor.read_text());fn=next(n for n in mt.body if isinstance(n,ast.FunctionDef)and n.name=='monitor');need(len(fn.args.args)==6,'genuine six argument monitor')
source=Path(refs['integrationIndex']['path']).parent;integration_index=read(refs['integrationIndex']);source_rows=[refs['integrationIndex']]+[dict(r,path=str(source/r['path']))for r in integration_index['files']];need(len(source_rows)==58,'whole57+index Source family')
native=read(descriptor(source/'native-origins.json'))['files'];tools=read(descriptor(source/'tool-origins.json'))['files'];embedding=read(descriptor(source/'embedding-origins.json'))['files'];plan=read(descriptor(SOURCE/'stage-copy-plan.json'));need(len(native)==357 and len(tools)==1227 and len(embedding)==3,'actual native/tool/reference plan boundaries')
merged={}
for r in native+tools:
 origin=checked(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']));n=r['path'];need(n not in merged,'base plan no destination overlap');merged[n]=dict(path=n,original=r['original'],sha256=r['sha256'],bytes=r['bytes'],sourceMode=stat.S_IMODE(origin.stat().st_mode),targetMode=0o600,roles=sorted([r.get('role','GENUINE_DONOR_TOOL_DATA'),'EXACT_7C5A_STAGE_PLAN_ROW']))
need(len(merged)==1584,'357+1227=1584 actual base plan')
for r in source_rows:
 checked(r);n=Path(r['path']).relative_to(SOURCE.parents[3]).as_posix();need(n not in merged,'Source family58 has no base destination overlap');merged[n]=dict(path=n,original=r['path'],sha256=r['sha256'],bytes=r['bytes'],sourceMode=stat.S_IMODE(Path(r['path']).stat().st_mode),targetMode=0o600,roles=['SEALED_7C5A_FAMILY_STAGED_DATA_ACTIVE_PRODUCER_REMAINS_ORIGINAL'])
need(len(merged)==1642 and plan['files']==[merged[n]for n in sorted(merged)],'whole1642 exact byte/origin/mode/roles destination union')
expected_embedding=[]
for r in embedding:
 p=checked(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']));expected_embedding.append(dict(r,sourceMode=stat.S_IMODE(p.stat().st_mode),targetMode=0o600))
need(plan['embeddingData']==expected_embedding and plan['totalPhysicalCopies']==1645,'separate3 references, not configured external build inputs')
code=(SOURCE/'controller.py').read_text();tree=ast.parse(code);defs={n.name:ast.get_source_segment(code,n)for n in tree.body if isinstance(n,ast.FunctionDef)}
derivation=read(descriptor(SOURCE/'generic-derivation.json'));donor=checked(derivation['donor']).read_text();dd={n.name:ast.get_source_segment(donor,n)for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef)}
for r in derivation['definitions']:
 need(hashlib.sha256(dd[r['name']].encode()).hexdigest()==r['beforeSha256']and hashlib.sha256(defs[r['name']].encode()).hexdigest()==r['afterSha256'],'genuine actual primitive Source '+r['name'])
 need((dd[r['name']]==defs[r['name']])==r['unchanged'],'actual primitive unchanged flag')
need(len(derivation['definitions'])==13 and sum(r['unchanged']for r in derivation['definitions'])==12,'exact12 primitive copies+canonicalchecked refinement')
need(code.endswith(checked(derivation['newStageBody']).read_text()),'whole actual own Source body')
for p in SOURCE.glob('*.py'):ast.parse(p.read_text());checks+=1
ast.parse((SOURCE/'stage-body.py.txt').read_text());checks+=1
# Actual own constants are also inspected via a genuine inert import by the
# independent pure script, never by changing an imported module's globals.
need("OWN=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v1'"in code and "SOURCE_SHA='"+refs['integrationIndex']['sha256']+"'"in code,'actual own Source and active original integration contexts')
need(refs['activeProducerOriginal']==str(source/'build-engine.sh')and refs['activeHelperOriginal']==str(source/'layer-policy.py')and refs['stagedSourceFamily']=='DATA_ONLY','no staged operational helper/context projection')
need(defs['main'].index('frame=authorize')<defs['main'].index('spec=importlib.util')<defs['main'].index('OUT.mkdir'),'full auth before monitor custom import/output mutation')
need("for row in inputs['files']:checked(row)"in defs['authorize']and"for ix in inputs['families']"in defs['authorize']and"source_peer_model"in defs['authorize']and"stage_peer_model"in defs['authorize'],'whole current intake/own+integration+controller peers')
need("module.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,TIMEOUT,frame['config']['rootAuthority'])"in defs['main'],'real original sixarg API/600s')
need("'--no-local','--no-checkout'"in defs['stage']and"'checkout','--detach',BASE"in defs['stage']and"'ls-tree','-r','-z','--full-tree',BASE"in defs['stage'],'actual detached54b Git mechanism')
need(defs['stage'].index('baseline_preimage(target')<defs['stage'].index('target.unlink()')<defs['stage'].index('durable(target,data)'),'checked preimage→unlink→exclusive fsynced write')
need("progress(progress_path,dict(event='authorized-baseline-preimage',preimage=preimage));target.unlink()"in defs['stage'],'preimage durable before unlink')
need("git_blob_id(data)==item['object']"in defs['baseline_preimage']and"s.st_nlink==1"in defs['baseline_preimage']and"not in original_ids"in defs['baseline_preimage'],'fresh Git blob/inode ownership boundary')
need("Path(path).open('xb')"in defs['durable']and'os.fsync(f.fileno())'in defs['durable']and'fsync_directory(Path(path).parent)'in defs['durable'],'exclusive durable full copy')
need("result['partialEmbeddingData']"in defs['stage']and"result['partialTargets']"in defs['stage']and"result['state']='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_FAILED_OR_PARTIAL_RETAINED'"in defs['stage'],'honest partial source+reference FAILED journal')
need("git_objects(REPO)==original_git"in defs['stage']and'if final_failure is not None:raise final_failure'in defs['stage']and"frame['originalStats']"in defs['recheck'],'full final/failure original Git/Source identity protection')
for n in ['config.template.json','root-authority.template.json']:
 v=read(descriptor(SOURCE/n));need(v['state'].startswith('UNISSUED_'),'actual authority unissued')
root=read(descriptor(SOURCE/'root-authority.template.json'));need(root['sourceStageAllowed']is False,'no Source action grant')
for k in ['stageControllerIndex','stageControllerEntry','stageControllerReview','gitBinary','pythonExecutable','actualStageResult','actualStageReview','actualBuildResult','reviewedNativePins','runtimeAuthority']:need(root[k]is None,'closed new Rootslot '+k)
for k in ['configuredSourceRoot','workRoot','freezeRoot','externalOutputRoot','stageJournal']:need(not os.path.lexists(refs[k]),'future exact root absent')
for p,ident in identities.items():need(key(Path(p).lstat())==ident,'final input byte/mode/inode identity')
for path in families:
 base=Path(path).parent;need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in json.loads(Path(path).read_bytes())['files']]},'final whole family membership')
summary=dict(schemaVersion=1,state='INDEPENDENT_HASH_HMAC357_STAGE_SOURCE_DATA_AST_INTAKE_PASSED',checks=checks,currentFullHashFiles=len(rows),currentLogicalBytes=sum(r['bytes']for r in rows.values()),currentFamilies=len(families),controllerSourceIndex=source_index,integrationSourceIndex=refs['integrationIndex'],genericMonitorSourceIndex=refs['monitorIndex'],declaredInputManifest=descriptor(SOURCE/'input-hashes.json'),sourcePlan=descriptor(SOURCE/'stage-copy-plan.json'),nativeFiles=357,toolRows=1227,baseRows=1584,integrationFamilyRows=58,uniqueSourceDestinations=1642,sourceDestinationOverlap=[],embeddingReferenceDataCopies=3,totalPhysicalCopies=1645,primitiveCopies=12,canonicalPrimitiveRefinements=1,ownPythonAstFiles=len(list(SOURCE.glob('*.py'))),allOperationalActionsInvoked=False,selfWritingAuthorChecksInvoked=False,cloneHistoryQualification='Full reachable clone; no depth/single-branch/object byte-count cap.120s commands/600s outer are deadline refusal bounds, not history-size proof',gitConfigurationQualification='Explicit GIT_* override removal and system/globalconfig /dev/null; no universal Git host/tool hermeticity claim',publicCryptoInitAndLiveEvpSnapshotPolicy='UNRESOLVED_SEPARATE_COMPONENT_LIFECYCLE_GATE')
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
