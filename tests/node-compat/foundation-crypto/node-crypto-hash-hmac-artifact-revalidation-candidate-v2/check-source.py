"""Authoring-only checks; no bootstrap/run/recheck/helper/admit calls.
Authenticates via the ACTUAL V2 checked() function, not a permissive twin.
Writes own preparation result; do not rerun in the held sealed family.
"""
from pathlib import Path
import ast,copy,difflib,hashlib,importlib.util,json,os,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;checks=0;seen={}
def need(v,label):
 global checks
 checks+=1
 if not v:raise AssertionError(label)
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(n):return json.loads((P/n).read_bytes())
refs=read('references.json')
for p in P.glob('*.py'):ast.parse(p.read_text());checks+=1
for r in read('guard-test-inputs.json')['files']:need(row(Path(r['path']))==r,'authenticated read-guard code/data')
spec=importlib.util.spec_from_file_location('actual_v2_read_guard_source_check',P/'revalidate.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
need(guard.OWN==P and guard.TMP_ALIAS_POLICY==refs['tmpAliasPolicy'],'genuine own module constants')
def checked(r):
 before=copy.deepcopy(r);p=guard.checked(r);need(before==r,'descriptor strings unchanged');seen[r['path']]=r;return p
def family(ix):
 p=checked(ix);v=json.loads(p.read_bytes());names={'index.json'}
 for r in v['files']:
  need(r['path']not in names,'unique family member');names.add(r['path']);checked(dict(r,path=str(p.parent/r['path'])))
 need(not any(q.is_symlink()for q in p.parent.rglob('*'))and names=={q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()},'complete indexed family')
base=json.loads(checked(refs['baseSourceInputs']).read_bytes());extra=json.loads(checked(refs['baseArtifactInputs']).read_bytes());additional=read('source-inputs.json');need(len(base['files'])+len(extra['files'])==21328,'unchanged whole recorded input count')
for r in [*base['files'],*extra['files'],*additional['files']]:checked(r)
families={r['path']:r for r in[*base['families'],*additional['families']]}
for ix in families.values():family(ix)
for name in ['baseArtifactTrees','baseReferenceAliases','producerReferences','producerAdmission','producerIo']:checked(refs[name])
trees=json.loads(Path(refs['baseArtifactTrees']['path']).read_bytes())['trees']
for tree in trees:
 actual=[];root=Path(tree['root'])
 for parent,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   p=Path(parent)/name;actual.append(dict(path=p.relative_to(root).as_posix(),kind='symlink'if p.is_symlink()else'directory'if p.is_dir()else'file',mode=p.lstat().st_mode&0o7777))
 need(sorted(actual,key=lambda x:x['path'])==tree['entries'],'whole shared tree/modes')
for p in[refs['outputRoot'],refs['externalOutputRoot'],refs['failedReadOnlyOutputRoot'],refs['freezeRoot']]:need(not Path(p).exists()and not Path(p).is_symlink(),'fresh/held-absent roots')
modelspec=importlib.util.spec_from_file_location('actual_v2_pure_contracts',P/'models.py');models=importlib.util.module_from_spec(modelspec);modelspec.loader.exec_module(models)
own=dict(path=str(P/'index.json'),sha256='1'*64,bytes=1) # pure synthetic contract input, NOT authority/proof
root=read('root-authority.template.json');root.update(state=models.STATE,adapterIndex=own,readOnlySourceAdmissionAllowed=True,ownedEvidencePublicationAllowed=True);models.root(root,own,refs);checks+=1
negatives=0
for key in models.NO_PERMISSIONS:
 bad=copy.deepcopy(root);bad[key]=True
 try:models.root(bad,own,refs)
 except AssertionError:negatives+=1
 else:raise AssertionError('permission mutation accepted')
peer=read('future-source-review-contract.json')['requiredFixedValues'];peer=dict(peer,state=models.PEER,sourceIndexSha256=own['sha256']);models.peer(peer,own,refs);checks+=1
for key,value in [('recordedCheckedRows',21327),('selectedTmpAliasDescriptors',3),('otherSymlinkAncestorsRejected',False),('actualCheckedGuardAllInputsPassed',False),('sourceIndexSha256','0'*64)]:
 bad=copy.deepcopy(peer);bad[key]=value
 try:models.peer(bad,own,refs)
 except AssertionError:negatives+=1
 else:raise AssertionError('peer mutation accepted')
test=read('guard-test.stdout.json');need(test['passed']and test['recordedRows']==21328 and test['otherActualSymlinkPathsRefused']==34 and test['negativeCases']==48 and test['oldSelectedRowsRefused']==2,'genuine whole guard and precise negative test')
need((P/'guard-test.stderr.log').read_bytes()==b'','empty test stderr')
before=list(seen.values())
for r in before:checked(r)
parent=Path(refs['parentAdapterIndex']['path']).parent;changes=[]
for name in['revalidate.py','models.py']:
 changes.append(dict(before=row(parent/name),after=row(P/name),unifiedDiff=''.join(difflib.unified_diff((parent/name).read_text().splitlines(True),(P/name).read_text().splitlines(True),fromfile='v1/'+name,tofile='v2/'+name))))
derivation=read('derivation.json');derivation['changedCode']=changes;(P/'derivation.json').write_text(json.dumps(derivation,indent=2)+'\n')
report=dict(schemaVersion=1,passed=True,sourceOnly=True,checks=checks,uniqueCurrentInputs=len(seen),recordedCheckedRows=21328,selectedTmpAliasDescriptors=2,otherSymlinkAncestorsRejected=True,actualCheckedGuardAllInputsPassed=True,currentBeforeFinalInputsStable=True,sourceFamilies=len(families),currentTrees=len(trees),genuineGuardNegativeCases=test['negativeCases'],pureContractNegativeCases=negatives,activePythonAsts=len(list(P.glob('*.py'))),nativeChanges=0,ledgerBytesCopied=0,adapterBootstrapRunOrRecheckInvoked=False,originalAdmitOrHelperImported=False,engineExecuted=False,cryptoOperationsInvoked=False)
(P/'source-check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
