"""Read/hash of actual pilot source/plan/native/tool prerequisites; no helper call."""
from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parent;Z=P.parent;S=Z/'cost-pilot-timing-candidate-v4';checks=0;seen={};cache={}
def need(v,n):
 global checks
 assert v,n;checks+=1
def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def verify(r):
 p=Path(r['path']);need(p.is_file()and not p.is_symlink()and p.is_absolute(),'ordinary prerequisite file');a=p.stat();identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns);real=str(p.resolve())
 if real not in cache:need(row(p)=={k:r[k]for k in('path','sha256','bytes')},'full prerequisite hash');cache[real]=dict(identity=identity,expected={k:r[k]for k in('sha256','bytes')})
 need(cache[real]['identity']==identity and cache[real]['expected']=={k:r[k]for k in('sha256','bytes')},'stable repeated prerequisite');seen[str(p)]={k:r[k]for k in('path','sha256','bytes')};return p
def data(r):return json.loads(verify(r).read_bytes())
def family(r):
 x=data(r);base=Path(r['path']).parent;names=set()
 for v in x['files']:
  n=v['path'];need(type(n)is str and n and not n.startswith('/')and all(p not in('','.','..')for p in n.split('/'))and n not in names,'local unique prerequisite member');names.add(n);verify(dict(v,path=str(base/n)))
 need(not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'},'whole prerequisite family membership');return len(names)
root=data(dict(path=str(Z/'cost-pilot-v4-root-results.json'),sha256='3f7c0b443490692e4b4a04d22ee6c83a1a84bc72d091703fa29f18cb77002e42',bytes=4270));auth=data(root['rootAuthority']);cfg=data(root['rootConfig']);source=cfg['sourceIndex'];need(source['sha256']==root['sourceIndexSha256'],'actual pilot source preserved')
families=[]
for r in[source,auth['sourceIndependentReview']['index'],auth['independentPreparedPlanReview']['index']]:families.append(dict(index=r,members=family(r)))
for name,pin,count in[('cost-pilot-timing-candidate-v1','55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b',85),('cost-pilot-timing-candidate-v2','1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2',26),('cost-pilot-timing-candidate-v3','c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9',50)]:
 r=row(Z/name/'index.json');need(r['sha256']==pin and family(r)==count,'literal immutable source ancestor');families.append(dict(index=r,members=count))
refs=json.loads((S/'references.json').read_bytes());need(refs['calibrationDecision']['sha256']==root['calibrationDecisionSha256']=='3cf4eb748d9fcf1e985eddfbdfd49544e507e83300056336fc8665fff22c546e','actual selected protocol decision')
for r in json.loads((S/'source-inputs.json').read_bytes())['files']:verify(r)
source_peer=data(auth['sourceIndependentReview']['result']);need(source_peer['state']=='INDEPENDENT_ZLIB_COST_PILOT_TIMING_SOURCE_REVIEW_PASSED_V1'and source_peer['sourceIndexSha256']==source['sha256']and source_peer['ownerActionsInvoked']is False,'source peer unchanged')
plan_peer=data(auth['independentPreparedPlanReview']['result']);need(plan_peer['state']=='INDEPENDENT_ZLIB_COST_PREPARED_PLAN_V4_RESULTS_REVIEW_PASSED_V1'and plan_peer['verifiedPassed']is True and plan_peer['sourceIndexSha256']==source['sha256']and plan_peer['preparedPlan']==auth['preparedPlan'],'actual independent prepared plan proof tuple')
for r in data(plan_peer['inputClosure'])['files']:verify(r)
plan=data(auth['preparedPlan']);need(plan['sourceIndexSha256']==source['sha256']and plan['artifacts']==plan_peer['artifacts']and len(plan['expected'])==90,'whole real pilot input plan/artifact tuple')
cases=data(refs['cases']);need(len(cases)==30,'full original primary case corpus')
for c in plan['expected']:
 case=cases[c['caseId']];need(case['index']==c['caseId']and case['id']==c['caseName']and case['direction']==c['direction']and case['timingNMax']==c['timingNMax']and case['logicalUncompressedBytesPerOperation']==c['logicalBytes'],'all plan corpus identities/logical bounds')
for r in[auth['phaseAuthority'],auth['quietWindowAuthority'],auth['externalController'],refs['calibrationDecision'],root['reader'],root['windowCompletion']]:verify(r)
# Whole actual publication boundary, rechecked as DATA from its typed ledger.
tooltrees=data(row(Z/'cost-tooling-candidate-v3/tool-trees.json'));publication=Path('/private/tmp/starling-node-compat/zlib-cost-source-v3');ix=data(row(publication/'index.json'));need(len(tooltrees['trees'])==2 and len(tooltrees['links'])==len(ix['links'])==22,'two tool trees/22 typed links')
need(publication.stat().st_ino==ix['rootIdentity']['inode']and publication.stat().st_dev==ix['rootIdentity']['device'],'same actual publication root inode')
actual_files=set();actual_dirs=set();actual_links=set()
for parent,dirs,files in os.walk(publication,followlinks=False):
 for n in dirs+files:
  p=Path(parent)/n;relative=p.relative_to(publication).as_posix()
  if p.is_symlink():actual_links.add(relative)
  elif p.is_dir():actual_dirs.add(relative)
  else:need(p.is_file(),'ordinary actual publication member');actual_files.add(relative)
need(actual_files=={r['path']for r in ix['files']}|{'index.json','completion.json'}and actual_dirs==set(ix['directories'])and actual_links=={r['destination']for r in tooltrees['links']},'whole actual publication membership')
for r in tooltrees['links']:
 p=publication/r['destination'];need(os.readlink(p)==r['newLinkText']and p.resolve()==publication/r['mappedTarget'],'all exact link texts and mapped targets')
for tree in tooltrees['trees']:
 actual={n for n in actual_files|actual_links|actual_dirs if n.startswith(tree['publicationRoot']+'/')};wanted={r['destination']if'destination'in r else tree['publicationRoot']+'/'+r['path']for r in tree['entries']};need(actual==wanted,'full typed tool-tree membership')
 for r in tree['entries']:
  if r['kind']=='file':verify(dict(path=str(publication/r['destination']),sha256=r['sha256'],bytes=r['bytes']))
for real,c in cache.items():s=Path(real).stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==c['identity'],'final prerequisite identity stable')
result=dict(schemaVersion=1,verifiedPassed=True,checks=checks,families=families,sourceIndex=source,cases=refs['cases'],calibrationDecision=refs['calibrationDecision'],sourceReview=auth['sourceIndependentReview'],actualPlan=auth['preparedPlan'],actualPlanReview=auth['independentPreparedPlanReview'],artifacts=plan['artifacts'],components={arm:a['component']for arm,a in plan['artifacts'].items()},toolTrees=2,typedToolLinks=22,actualPublicationRegularFiles=len(actual_files),uniqueReferencePaths=len(seen),ownerModulesOrHelpersOrToolsInvoked=False)
with(P/'prerequisite-audit.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
with(P/'prerequisite-input-hashes.json').open('x')as f:json.dump(dict(schemaVersion=1,files=[seen[p]for p in sorted(seen)]),f,indent=2);f.write('\n')
print(json.dumps(dict(prerequisitesPassed=True,checks=checks,paths=len(seen),toolTrees=2,links=22,ownerActionsInvoked=False)))
