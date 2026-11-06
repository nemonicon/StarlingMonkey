"""Final bounded DATA publication; only this own review folder is written."""
from pathlib import Path
import json,hashlib,ast,stat
O=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def desc(p):return dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size)
def need(v,m):
 if not v:raise AssertionError(m)
def read(p):return json.loads(p.read_bytes())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
need(not(O/'index.json').exists(),'fresh unsealed own index')
for p in O.glob('*.py'):ast.parse(p.read_text())
for e in ['intake-3','host-ast-2','protection-1','finalize-3']:
 need(read(O/'evidence'/e/'terminal.json')['rawExitCode']==0,'final checker raw0');need((O/'evidence'/e/'stderr.log').read_bytes()==b'','final checker stderr empty')
r=read(O/'results.json');c=read(O/'result-contract.json');need(r['state']==c['requiredReviewState'],'aggregate state/contract')
for k,v in c['requiredFixedValues'].items():need(r[k]==v,'aggregate fixed '+k)
need(r['acceptedComponentCount']==5 and r['expectedUnacceptedConstructionFailureCount']==1 and r['allSixAcceptedComponents']is False,'honest six outcomes')
for case in ['clock-snapshot','surviving-interest','fatal','init-fatal']:
 rr=read(O/case/'results.json');cc=read(O/case/'result-contract.json');need(rr['state']==cc['requiredReviewState'],'percase actual state')
 for k,v in cc['requiredFixedValues'].items():need(rr[k]==v,'percase fixed '+k)
 need(rr['artifacts']==cc['artifacts']and rr['generatedFiles']==cc['generatedFiles'],'percase actual maps')
 for row in r['fixtureReviews'][case].values():
  if type(row)is dict and set(row)=={'path','sha256','bytes'}:
   p=Path(row['path']);need(desc(p)==row,'current percase result/contract descriptors')
for row in read(O/'raw-copy-ledger.json')['files']:
 for role in ['original','copy']:
  p=Path(row[role]['path']);need(desc(p)==row[role],'final exact raw bytes '+role)
# All exact actual/percase referenced roles are checked once more while small;
# inherited Source ledger payloads retain the full original read/hash evidence.
verified=set()
def walk(v):
 if type(v)is dict:
  if set(v)=={'path','sha256','bytes'}:
   p=Path(v['path'])
   if str(p)not in verified:need(p.is_file()and not p.is_symlink()and desc(p)==v,'final descriptor stability');verified.add(str(p))
  else:
   for x in v.values():walk(x)
 elif type(v)is list:
  for x in v:walk(x)
walk(r);walk(c)
for case in ['clock-snapshot','surviving-interest','fatal','init-fatal']:walk(read(O/case/'results.json'));walk(read(O/case/'result-contract.json'))
receipt=dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMBINED355_REMAINING_CONSTRUCTION_DATA_REVIEW_V1',aggregateResult=desc(O/'results.json'),aggregateContract=desc(O/'result-contract.json'),intakeSummary=desc(O/'intake-summary.json'),currentProtection=desc(O/'current-protection.json'),finalDirectDescriptorsRehashed=len(verified),acceptedComponentsInThisPacket=3,identifiedUnacceptedConstructionFailures=1,combinedWithImmutablePriorPureAndResourceAcceptedComponents=5,fullSixConstructionOutcomesReviewed=True,allSixAcceptedComponents=False,ordinaryExportsOrGeneratedModulesInvokedByReviewer=False,operationalHelperToolEngineOrGuestActionsInvokedByReviewer=False,hostMetadataParserOnly=True,allOperationalAuthoritiesUnissued=True,history=desc(O/'reader-history.json'),ownIndexExcludesOnlyOwnRootIndex=True)
write(O/'receipt.json',receipt)
payloads=[p for p in sorted(O.rglob('*'))if p.is_file()and p not in [O/'index.json',O/'member-ledger.json']]
write(O/'member-ledger.json',dict(schemaVersion=1,scope='All own payloads excluding only this ledger and own root index; nested copied indices included',files=[dict(path=p.relative_to(O).as_posix(),sha256=digest(p),bytes=p.stat().st_size)for p in payloads]))
files=[p for p in sorted(O.rglob('*'))if p.is_file()and p!=O/'index.json'];need(not any(p.is_symlink()for p in O.rglob('*')),'ordinary own closed set')
index=dict(schemaVersion=1,files=[dict(path=p.relative_to(O).as_posix(),sha256=digest(p),bytes=p.stat().st_size)for p in files]);write(O/'index.json',index)
need({p.relative_to(O).as_posix()for p in O.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in index['files']]},'whole exact own publication membership')
for row in index['files']:
 p=O/row['path'];need(desc(p)==dict(row,path=str(p)),'every own indexed byte final')
print(json.dumps(dict(index=desc(O/'index.json'),result=desc(O/'results.json'),contract=desc(O/'result-contract.json'),receipt=desc(O/'receipt.json'),indexedFiles=len(files),actualFiles=len(files)+1,ownLogicalBytes=sum(p.stat().st_size for p in O.rglob('*')if p.is_file()),perCase={case:{role:desc(O/case/name)for role,name in [('result','results.json'),('contract','result-contract.json')]}for case in ['clock-snapshot','surviving-interest','fatal','init-fatal']}),indent=2))
