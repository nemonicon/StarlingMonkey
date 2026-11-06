"""Compact readonly Root contract review; never calls controller/helper/monitor."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,stat
P=Path(__file__).resolve().parent;K=P.parent;SOURCE=K/'node-crypto-hash-hmac-native-controller-candidate-v1'
rows={};families={};identities={};checks=0

def need(v,m):
 global checks
 assert v,m;checks+=1

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()

def desc(p):p=Path(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def identity(p):s=Path(p).lstat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def checked(r):
 p=Path(r['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'regular absolute declared Source/Root DATA');need(p.stat().st_size==r['bytes']and sha(p)==r['sha256'],'full exact immutable bytes');rows[str(p)]=r;identities[str(p)]=identity(p);return p

def read(r):return json.loads(checked(r).read_bytes())
def family(ix):
 if ix['path']in families:need(families[ix['path']]==ix,'same family');return
 v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];need(n and n not in names and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique confined family member');names.add(n);checked(dict(r,path=str(root/n)))
 need(not any(p.is_symlink()for p in root.rglob('*')),'no family aliases');need({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names,'whole family membership including nestedindices');families[ix['path']]=ix
own=desc(SOURCE/'index.json');need(own['sha256']=='9e5195b90e20708a8a398fa9013eba867e2f2e5e1d18c2f5b76ed5bbc3c01d3b','sealed Source9e519');family(own)
refs=json.loads((SOURCE/'references.json').read_bytes());policy=json.loads((SOURCE/'root-environment-policy.json').read_bytes())
roles={n:desc(K/('node-crypto-hash-hmac-native-build-v2-root-'+n+'.json'))for n in ['authority','config','invocation']}
need(roles['invocation']['sha256']=='2171882a5f621c5e6c6e3a70a0022752c1419bfbd3257a00e2d106af2e684854'and roles['invocation']['bytes']==2494,'actualRoot v2 invocation pin')
root=read(roles['authority']);cfg=read(roles['config']);inv=read(roles['invocation']);roles['launcher']=inv['launcher'];launcher=checked(roles['launcher']).read_text()
pair=root['controllerSourceReview'];family(pair['index']);peer=read(pair['result']);need(pair==inv['sourcePeer']and pair['index']['sha256']=='85f2984300c5c2ae8cb4fed1aaaa252c6b0d93bdeac25b9b45fedbf9e9197062','actual85f Sourcepeer')
peer_contract=read(desc(Path(pair['index']['path']).parent/'result-contract.json'))
need(peer['state']==peer_contract['requiredReviewState'],'peercontract state')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for n,v in peer_contract.get(group,{}).items():need(peer[n]==v,'actual peercontract '+n)
for ix in [refs['integrationSourceIndex'],refs['integrationSourceReview']['index'],refs['actualStageReview']['index'],refs['monitorIndex'],refs['lifecycleIndex']]:family(ix)
stage=read(refs['actualStageReview']['result']);stagek=read(refs['actualStageContract']);need(stage['state']==stagek['requiredReviewState'],'actual stagecontract state')
for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
 for n,v in stagek.get(group,{}).items():need(stage[n]==v,'actual stagecontract '+n)
need(stage['coverage']==stagek['requiredCoverage'],'actual stagewholecoverage')
for n in ['recipe','helper','policy','cachePlan','monitorEntry','lifecycleEntry','metadataModel','hashModel','python']:checked(refs[n])
need(cfg['state']=='NODE_CRYPTO_HASH_HMAC357_NATIVE_CONFIG_V1'and cfg['controllerIndex']==inv['controllerIndex']==root['controllerIndex']==own and cfg['rootAuthority']==inv['rootAuthority']==roles['authority']and cfg['integrationSourceIndex']==refs['integrationSourceIndex'],'original contexts/root/config/Source joins')
need(inv['config']==roles['config']and inv['actualArgv']==[refs['python']['path'],'-B','-I',str(SOURCE/'controller.py'),'launcher',json.dumps(roles['config'],separators=(',',':'))],'literal real isolatedPython/controller argv')
need(inv['originalOuterDeadlineSeconds']==inv['originalInnerDeadlineSeconds']==root['externalParentDeadlineSeconds']==7200,'original unchanged monitor max7200')
for n in ['freezeAllowed','engineExecutionAllowed','cryptoOperationsAllowed','liveEvpSnapshotAdmission','operationalAdmission']:need(inv[n]is False,'invocation closed '+n)
need(inv['buildOnly']is True and root['phase']=='build','only normal build scope')
# Real inert module in its actual original context. No namespace/global rewrite.
modelpath=SOURCE/'models.py';tree=ast.parse(modelpath.read_text());need(not any(isinstance(n,(ast.Import,ast.ImportFrom))for n in ast.walk(tree)),'models has no custom/operational imports');need(all(isinstance(n,(ast.Expr,ast.Assign,ast.FunctionDef))for n in tree.body),'only pure model constants/function definitions')
spec=importlib.util.spec_from_file_location('independent_original_hash357_models',str(modelpath));model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
need(Path(model.__file__).resolve()==modelpath.resolve(),'real model file context');model.root(root,own,refs,policy);model.peer(peer,own,refs,policy);model.stage(stage,refs);model.cache_plan(read(refs['cachePlan']),refs);checks+=4
cases=[]
def reject(name,fn):
 try:fn()
 except(AssertionError,KeyError):cases.append(name);return
 raise AssertionError('Mutation accepted: '+name)
def root_case(name,key,value):
 v=copy.deepcopy(root);v[key]=value;reject(name,lambda:model.root(v,own,refs,policy))
for n in ['debugAllowed','gcAllowed','oomAllowed','borrowAllowed','engineExecutionAllowed','keyOrCryptoAllowed','guestAllowed','componentAllowed','exportAllowed','bootstrapAllowed','globalMutationAllowed','metadataProjectionAllowed','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:root_case('closed '+n,n,True)
for n,v in [('externalParentDeadlineSeconds',7500),('nativeSourceFiles',355),('rawMetadataFields',80),('selectedManifestCount',11),('hashHmacEnabled',False),('auditedBorrowEnabled',True),('entropyPolicy','on'),('defaultCopyOnly',False),('variant','gc-off'),('workRoot','/private/tmp/foreign-work'),('configuredSourceRoot','/private/tmp/foreign-source'),('nativeBuildAllowed',False),('freezeAllowed',True),('readOnlySourceAdmissionAllowed',True),('postBuildNinjaListingAllowed',True),('actualBuildReview',{'synthetic':True}),('actualBuildContract',{'synthetic':True}),('bootstrapFrame',{}),('parallelBuilds',2),('requiredStartFreeBytes',0),('stopBelowFreeBytes',0)]:root_case('invalid '+n,n,v)
for n,v in [('sourceOnly',False),('sourceReviewPassed',False),('controllerSourceIndexSha256','0'*64),('integrationSourceIndexSha256','0'*64),('nativeBuildActionsInvoked',True)]:
 x=copy.deepcopy(peer);x[n]=v;reject('peer '+n,lambda x=x:model.peer(x,own,refs,policy))
# Static original API/ordering proof. Never imports or invokes the monitor.
mt=ast.parse(checked(refs['monitorEntry']).read_text());monitor=next(n for n in mt.body if isinstance(n,ast.FunctionDef)and n.name=='monitor');need(len(monitor.args.args)==6,'original six positional monitor API');first=next(n for n in monitor.body if isinstance(n,ast.Assert));popen=next(n for n in ast.walk(monitor)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='Popen');need(first.lineno<popen.lineno,'deadline assertion before Popen')
expr=compile(ast.Expression(first.test),'original monitor deadline condition','eval');need(eval(expr,{},dict(timeout_seconds=7200,parent_grace_seconds=45))is True and eval(expr,{},dict(timeout_seconds=7500,parent_grace_seconds=45))is False,'exact monitor assertion old-refusal/new-bound')
lt=ast.parse(launcher);calls=[n for n in ast.walk(lt)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor'];need(len(calls)==1 and len(calls[0].args)==6 and isinstance(calls[0].args[4],ast.Constant)and calls[0].args[4].value==7200,'genuine sixarg Rootmonitor call max7200')
need("family(Path(refs['monitorIndex']['path']).parent)"in launcher and launcher.index("family(Path(refs['monitorIndex']['path']).parent)")<launcher.index('spec.loader.exec_module(m)')<launcher.index('t = m.monitor('),'monitor family/hash before real import/call')
controller=(SOURCE/'controller.py').read_text();need(controller.index("for r in inputs['files']:add(r)")<controller.index("# Actual own modules are first imported")<controller.index("models.root(root,own,refs,ENV_POLICY)")<controller.index('def launcher(frame):'),'original fullSource intake then pureRoot before actions')
need("os.execve(argv[0],argv,child)"in controller and "assert clean_environment(dict(os.environ))[1]==[]"in controller,'genuine cleaned exec and parent/worker checks')
need("['HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME', 'TMPDIR']"in launcher and "PYTHONDONTWRITEBYTECODE='1'"in launcher,'Root env allowlist preserves home and excludes startup functions')
oldrole=desc(K/'node-crypto-hash-hmac-native-build-v1-root-results.json');old=read(oldrole);need(old['state']=='ROOT_NATIVE_BUILD_PRESPAWN_DEADLINE_REFUSAL_V1'and old['requestedOuterDeadlineSeconds']==7500 and old['existingMonitorMaximumSeconds']==7200 and old['monitorEnteredBeforeAnySpawn']is True and old['monitorSpawnReached']is False and old['sourceControllerInvoked']is old['nativeBuildInvoked']is old['workCreated']is False,'historical originalv1 saved prespawn report')
for n in ['rootAuthority','rootConfig','rootInvocation','rootLauncher','monitor','callerOnlyFile']:checked(old[n])
need(old['actualEngine']is old['actualMetadata']is None,'historical no build artifact');oldinv=read(old['rootInvocation']);need(oldinv['originalOuterDeadlineSeconds']==7500 and oldinv['originalInnerDeadlineSeconds']==7200,'old actual deadline role')
need(old['rootAuthority']['sha256']==roles['authority']['sha256']and old['rootAuthority']['path']!=roles['authority']['path'],'byte-identical authority in distinct v1/v2 Root role paths, no Source rewrite')
# Snapshot absence is historical DATA only; WORK may now exist for actual14463.
raw=[]
for d in [*roles.values(),oldrole,old['rootInvocation'],old['rootLauncher'],old['callerOnlyFile']]:
 src=checked(d);target=P/'raw'/src.name;target.parent.mkdir(exist_ok=True);target.write_bytes(src.read_bytes());need(sha(target)==d['sha256'],'compact exact Rootrawcopy');raw.append(dict(original=d,copy=desc(target)))
for path,v in identities.items():need(identity(path)==v,'final immutable Source/Root identitybookend')
for path in families:
 base=Path(path).parent;need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in json.loads(Path(path).read_bytes())['files']]},'final exact closed family')
summary=dict(schemaVersion=1,state='ROOT_V2_PREFLIGHT_SOURCE_AND_PURE_MODELS_VALIDATED',sourceIndex=own,sourcePeer=pair,roles=roles,refsRoles={n:refs[n]for n in ['integrationSourceIndex','actualStageReview','actualStageContract','recipe','helper','policy','cachePlan','monitorIndex','monitorEntry','lifecycleIndex','lifecycleEntry']},historicalV1Result=oldrole,checks=checks,fullHashFiles=len(rows),logicalBytes=sum(d['bytes']for d in rows.values()),families=len(families),realModelsRootPeerStageCachePlanPassed=True,pureNegativeCases=len(cases),pureCases=cases,monitorDeadlineAssertionBeforeSpawn=True,rootMonitorSixArgumentCall=7200,scope='Root/Source/peer exact families and direct required recipe/helper/model roles only; no declared historical mega-ledger expansion or liveWORK audit',actualBuildSuccessClaim=False,actualBuildArtifactReview=None,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False,cryptoOperationsInvoked=False)
(P/'preflight-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=list(rows.values()),families=list(families.values())),indent=2)+'\n');(P/'raw-copy-ledger.json').write_text(json.dumps(dict(schemaVersion=1,files=raw),indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['state','checks','fullHashFiles','logicalBytes','families','pureNegativeCases']}))
