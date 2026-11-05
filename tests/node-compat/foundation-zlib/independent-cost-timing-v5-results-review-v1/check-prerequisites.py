"""Read/hash of actual timing source/plan/native/tool prerequisites; no helper call."""
from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parent;Z=P.parent;S=Z/'cost-pilot-timing-candidate-v5';checks=0;seen={};cache={}
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

rootrow=dict(path=str(Z/'cost-timing-v5-root-results.json'),sha256='55cf580f379c89bf9252ef78d5b133ff3647b8c406f0d09bb52e192b0f976a8f',bytes=9365)
root=data(rootrow);auth=data(root['rootAuthority']);cfg=data(root['controllerConfig']);run=data(cfg['runConfig']);source=run['sourceIndex'];need(source==root['sourceIndex']and source['sha256']=='e799350100bb3b54148fdc5bd46a857579a6aae7608890f620569ea3704ab321','exact actual V5 source')
families=[]
for r in[source,auth['sourceIndependentReview']['index'],auth['independentPreparedPlanReview']['index'],auth['warmNPlan']['index'],auth['controllerSourceIndex'],auth['controllerIndependentReview']['index']]:families.append(dict(index=r,members=family(r)))
for version,pin,count in[(1,'55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b',85),(2,'1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2',26),(3,'c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9',50),(4,'b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1',59)]:
 r=row(Z/('cost-pilot-timing-candidate-v'+str(version))/'index.json');need(r['sha256']==pin and family(r)==count,'literal complete source ancestry');families.append(dict(index=r,members=count))
refs=data(row(S/'references.json'))
for r in data(row(S/'source-inputs.json'))['files']:verify(r)
for name in('runtime-dependencies.json','worker-dependencies.json'):
 for r in data(row(S/name))['files']:verify(r)
source_peer=data(auth['sourceIndependentReview']['result']);need(source_peer['sourceIndexSha256']==source['sha256']and source_peer['sourceOnly']is source_peer['sourceReviewPassed']is True and source_peer['ownerActionsInvoked']is False,'actual V5 source peer')
plan_peer=data(auth['independentPreparedPlanReview']['result']);need(plan_peer['state']=='INDEPENDENT_ZLIB_COST_PREPARED_PLAN_V5_RESULTS_REVIEW_PASSED_V1'and plan_peer['verifiedPassed']is True and plan_peer['sourceIndex']==source and plan_peer['preparedPlan']==auth['preparedPlan'],'actual fresh9b75 plan proof')
for r in data(plan_peer['inputClosure'])['files']:verify(r)
pilot=data(auth['warmNPlan']['result']);need(auth['warmNPlan']==refs['actualCalibrationReview']and pilot['sourceIndex']==auth['calibrationSourceIndex']==refs['originalPilotSourceIndex']and pilot['sourceIndexSha256']!=source['sha256'],'real64472 and originalB5 distinct source role')
need(pilot['matchedPlan']==auth['warmNMatchedPlan']==refs['actualMatchedPlan']and pilot['cases']==refs['cases']and pilot['components']==plan_peer['components'],'actual matched plan/corpus/components consistent')
plan=data(auth['preparedPlan']);need(plan['sourceIndexSha256']==source['sha256']and plan['artifacts']==plan_peer['artifacts']and len(plan['expected'])==90 and plan['calibrationSourceIndex']==pilot['sourceIndex']and plan['calibrationReview']==auth['warmNPlan']and plan['calibrationMatchedPlan']==auth['warmNMatchedPlan'],'all actual V5 inputs exact')
for name,state in [('fullCorrectness','INDEPENDENT_ZLIB_COST_JCO_CORRECTNESS_V3_RESULTS_REVIEW_PASSED_V1'),('stockWasmtimeStrings','INDEPENDENT_ZLIB_COST_STOCK_WASMTIME42_STRING_TRANSPORT_RESULTS_VERIFIED_V1'),('actualControlsProof','INDEPENDENT_ZLIB_COST_JCO_CONTROL_V2_RESULTS_REVIEW_PASSED_V1')]:
 p=refs[name];family(p['index']);v=data(p['result']);c=data(p['contract']);need(v['schemaVersion']==1 and v['state']==state and v['verifiedPassed']is True and c['requiredReviewState']==state,'current original actual proof state '+name)
 for k,w in c.get('requiredFixedValues',{}).items():need(v[k]==w,'original fixed proof value '+k)
 if name=='fullCorrectness':need(v['controlOperations']==0 and v['actualBatchControlProofPending']is True,'old correctness pending control fields unchanged')
 elif name=='stockWasmtimeStrings':need(v['actualBatchControlProofPending']is True,'old transport pending control fields unchanged')
 else:need(v['controlOperations']==540 and v['codecCalls']==0 and v['pilotPrerequisitesSatisfied']is False,'separate actual controls no phase authority')
 need(v.get('components',v.get('requiredComponents'))==pilot['components'],'original actual component tuple '+name)
cases=data(refs['cases']);need(len(cases)==30,'whole original primary corpus')
for c in plan['expected']:
 v=cases[c['caseId']];need(v['id']==c['caseName']and v['index']==c['caseId']and v['direction']==c['direction']and v['timingNMax']==c['timingNMax']and v['logicalUncompressedBytesPerOperation']==c['logicalBytes'],'all90 whole corpus identities')
for r in[auth['phaseAuthority'],auth['quietWindowAuthority'],auth['externalController'],auth['rootActivationIssuer'],refs['calibrationDecision'],root['quietWindowCompletion']]:verify(r)
history=data(row(Z/'cost-timing-v5-observer-history.json'));need(history['actualTimingSourceOrOutputChanged']is False and history['workerOrCodecOrTimingActionsRepeated']is False,'Root observer clerical correction preserved')
observer=row(Z/'cost-timing-v5-observe.py');need(observer['sha256']==history['afterObserverSha256'],'actual corrected read-only observer source')
verify(observer)

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

for real,c in cache.items():
 s=Path(real).stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==c['identity'],'final prerequisite identity stable')
result=dict(schemaVersion=1,verifiedPassed=True,checks=checks,rootObservation=rootrow,families=families,sourceIndex=source,cases=refs['cases'],calibrationDecision=refs['calibrationDecision'],sourceReview=auth['sourceIndependentReview'],actualPlan=auth['preparedPlan'],actualPlanReview=auth['independentPreparedPlanReview'],actualPilotReview=auth['warmNPlan'],originalPilotSource=auth['calibrationSourceIndex'],actualMatchedPlan=auth['warmNMatchedPlan'],artifacts=plan['artifacts'],components={arm:a['component']for arm,a in plan['artifacts'].items()},toolTrees=2,typedToolLinks=22,actualPublicationRegularFiles=len(actual_files),uniqueReferencePaths=len(seen),ownerModulesOrHelpersOrToolsInvoked=False)
with(P/'prerequisite-audit.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
with(P/'prerequisite-input-hashes.json').open('x')as f:json.dump(dict(schemaVersion=1,files=[seen[p]for p in sorted(seen)]),f,indent=2);f.write('\n')
print(json.dumps(dict(prerequisitesPassed=True,checks=checks,paths=len(seen),toolTrees=2,links=22,ownerActionsInvoked=False)))
