"""Independent source hash/AST reader; no source operational modules invoked."""
from pathlib import Path
import ast,hashlib,json,stat,os,shutil
P=Path(__file__).resolve().parent;S=P.parent/'node-crypto-hash-hmac-native-controller-candidate-v1';checks=0;rows={};ids={};families={}
def need(v,m='check'):
 global checks
 checks+=1;assert v,m
def ident(p):
 s=p.lstat();return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def row(p):
 p=Path(p);a=ident(p);need(stat.S_ISREG(a[2]),'regular '+str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(ident(p)==a,'stable '+str(p));return dict(path=str(p),sha256=h.hexdigest(),bytes=a[4])
def check(r):
 need(set(r)=={'path','sha256','bytes'}and Path(r['path']).is_absolute(),'exactdescriptor')
 p=Path(r['path']);old=rows.get(str(p));need(old is None or old==r,'same descriptor')
 if old is None:need(row(p)==r,'hash '+str(p));rows[str(p)]=r;ids[str(p)]=ident(p)
 else:need(ident(p)==ids[str(p)],'stable current identity')
 return p
def read(r):return json.loads(check(r).read_bytes())
def direct(p):return read(row(p))
def family(r):
 if r['path']in families:need(families[r['path']]==r);return
 p=check(r);v=json.loads(p.read_bytes());names={'index.json'}
 for x in v['files']:
  n=x['path'];need(n not in names and not Path(n).is_absolute()and '..'not in Path(n).parts);names.add(n);check(dict(x,path=str(p.parent/n)))
 need(not any(q.is_symlink()for q in p.parent.rglob('*')));need(names=={q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()},'whole family '+str(p));families[r['path']]=r
sourceIndex=dict(path=str(S/'index.json'),sha256='9e5195b90e20708a8a398fa9013eba867e2f2e5e1d18c2f5b76ed5bbc3c01d3b',bytes=4907);family(sourceIndex)
inputs=direct(S/'source-inputs.json');refs=direct(S/'references.json');need(len(inputs['files'])==4795 and len(inputs['families'])==15)
for r in inputs['files']:check(r)
for r in inputs['families']:family(r)
need(not any(r['path'].startswith('/Users/dan/dev/StarlingMonkey/.git/')for r in inputs['files']),'historical user Git not liveguard')
stage=read(refs['actualStageReview']['result']);contract=read(refs['actualStageContract']);family(refs['actualStageReview']['index']);members=json.loads(Path(refs['actualStageReview']['index']['path']).read_bytes())['files'];base=Path(refs['actualStageReview']['index']['path']).parent
for d in [refs['actualStageReview']['result'],refs['actualStageContract']]:need(sum(dict(x,path=str(base/x['path']))==d for x in members)==1)
need(stage['state']==contract['requiredReviewState']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_RESULTS_REVIEW_PASSED_V2')
for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
 for k,v in contract[group].items():need(stage[k]==v)
need(stage['coverage']==contract['requiredCoverage']);j=read(refs['stageJournal']);need(len(j['copies'])==1642 and len(j['embeddingDataCompleted'])==3)
for x in j['copies']:
 p=check(dict(path=str(Path(refs['configuredSourceRoot'])/x['path']),sha256=x['sha256'],bytes=x['bytes']));need(stat.S_IMODE(p.stat().st_mode)==0o600 and p.stat().st_nlink==1)
for x in j['embeddingDataCompleted']:check(x['target'])
tree=direct(S/'configured-tree.json');root=Path(tree['root']);need(root==Path(refs['configuredSourceRoot']));actual=set();links={}
for p in root.rglob('*'):
 if p.is_symlink():links[p.relative_to(root).as_posix()]=os.readlink(p)
 elif p.is_file():actual.add(str(p))
for x in tree['files']:check(x['file']);need(stat.S_IMODE(Path(x['file']['path']).stat().st_mode)==x['mode'])
need(actual=={x['file']['path']for x in tree['files']});need(links=={x['path']:x['linkText']for x in tree['documentationLinks']});need((root/'.git/HEAD').read_text()=='54b3329b3ce818fd1f244e871e9c259b63667cda\n')
need(not Path(refs['workRoot']).exists()and not Path(refs['freezeRoot']).exists(),'no actual build/freeze yet')
for x in refs['hostTools']:
 need(str(Path(shutil.which(x['name'],path=refs['hostPath'])).resolve())==x['executable']['path']);check(x['executable'])
provenance=direct(S/'api-provenance.json')
for name,original in provenance['byteExactCopies'].items():check(original);need(row(S/name)['sha256']==original['sha256']and row(S/name)['bytes']==original['bytes'])
asts={f.name:ast.parse(f.read_bytes(),filename=str(f))for f in S.glob('*.py')};need(len(asts)==13)
controller=asts['controller.py'];bootstrap=next(n for n in controller.body if isinstance(n,ast.FunctionDef)and n.name=='bootstrap');firstLoad=min(n.lineno for n in ast.walk(bootstrap)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='load')
forNeed=[]
for needle in ["for r in ledger['files']:add(r)","aliases=read(proof['referenceAliases'])"]:
 lines=(S/'controller.py').read_text().splitlines();loc=[n for n,l in enumerate(lines,1)if needle in l];need(any(n<firstLoad for n in loc),'full future proof preimport '+needle);forNeed+=loc
calls=[]
for n in ast.walk(asts['controller.py']):
 if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor':need(len(n.args)==6);calls.append(dict(api='original0af.monitor',line=n.lineno,positionalArgs=len(n.args)))
need(len(calls)==1)
for n in ast.walk(asts['build_body.py']):
 if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor_owned_command':need(len(n.args)==5);calls.append(dict(api='originalf751.monitor_owned_command',line=n.lineno,positionalArgs=len(n.args)))
need(len(calls)==2)
# Authentic real modules are imported inertly only in the separate pure reader after this intake.
for name,t in asts.items():
 for node in ast.walk(t):
  if isinstance(node,ast.Call)and isinstance(node.func,ast.Name):need(node.func.id not in ['exec','eval'],'no dynamiceval')
for path,i in ids.items():need(ident(Path(path))==i,'final current identity')
summary=dict(schemaVersion=1,passed=True,checks=checks,sourceIndex=sourceIndex,currentFullHashFiles=len(rows),currentLogicalBytes=sum(x['bytes']for x in rows.values()),currentSourceFamilies=len(families),declaredFiles=4795,declaredFamilies=15,currentConfiguredSourceFiles=len(tree['files']),sourceStageCopies=1642,embeddingReferences=3,wholeConfiguredTreeMatches=True,currentOriginalUserGitFiles=0,pythonAstFiles=sorted(asts),firstCustomImportLine=firstLoad,preimportFutureBuildLedgerStatements=forNeed,actualApiCallSites=calls,ownActionModulesNotInvoked=True,producerOrMonitorOrCompilerOrEngineOrCryptoActions=False)
(P/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=[rows[x]for x in sorted(rows)],families=list(families.values())),indent=2)+'\n');print(json.dumps(summary))
