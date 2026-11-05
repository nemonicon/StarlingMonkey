"""Seal this source family only. No helper, process or runtime action."""
from pathlib import Path
import ast
import hashlib
import json
OWN=Path(__file__).resolve().parent
assert OWN==Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/resource-component-candidate-v1')
assert not(OWN/'index.json').exists()
def descriptor(path):
 p=Path(path);assert p.is_file()and not p.is_symlink();h=hashlib.sha256();n=0;a=p.stat()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def write(name,value):
 with(OWN/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
manifest=json.loads((OWN/'input-freeze.json').read_bytes());refs=json.loads((OWN/'references.json').read_bytes())
for r in manifest['files']:assert descriptor(r['path'])==r
checks=json.loads((OWN/'source-check-results.json').read_bytes());syntax=json.loads((OWN/'evidence/summary.json').read_bytes())
assert checks['state']=='RESOURCE342_COMPONENT_SOURCE_DATA_CHECKS_PASSED_V1'and checks['preparationRows']==len(manifest['files'])
assert syntax['allRawExitCodesZero']is True and syntax['helperOrBootstrapOrJcoOrSplicerOrCompilerOrComponentOrGuestOrClockActionsInvoked']is False
for p in (OWN/'evidence').glob('*.terminal.json'):
 terminal=json.loads(p.read_bytes());assert terminal['rawExitCode']==0 and terminal['ownerHelpersOrBootstrapOrPackagerOrGuestInvoked']is False
 assert descriptor(terminal['source']['path'])==terminal['source']
asts=[]
for p in OWN.glob('*.py'):ast.parse(p.read_bytes());asts.append(p.name)
result=dict(schemaVersion=1,state='SOURCE_ONLY_RESOURCE342_COMPONENT_CANDIDATE_PREPARED_V1',sourceOnly=True,sourcePreparationPassed=True,sourceIndexSha256=None,sourceIndependentReview=None,resourceSourceIndexSha256=refs['resourceSourceIndex']['sha256'],toolingSourceIndexSha256=refs['toolingIndex']['sha256'],actualBootstrapReview=refs['actualBootstrapReview'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=342,selectedManifestCount=9,packagingRegularFiles=4934,toolLinks=22,preparationRows=len(manifest['files']),exactFixtureCopies=5,scalarWitLiteralCopies=1,ordinaryGuestCases=7,sourceChecks=descriptor(OWN/'source-check-results.json'),pureAndGrammar=descriptor(OWN/'evidence/summary.json'),pythonAst=sorted(asts),prospectiveIndependentState='INDEPENDENT_SCHEDULER_RESOURCE342_COMPONENT_SOURCE_REVIEW_PASSED_V1',constructionRootAuthority=None,actualConstruction=None,actualComponent=None,actualArtifactReview=None,actualGeneratedLoaderSource=None,ordinaryRuntimeAuthority=None,nativeBootstrapInvokedInPreparation=False,ownerHelpersImported=False,componentizerOrJcoOrSplicerInvoked=False,nativeBuildOrEngineInvoked=False,guestOrTimerOrClockOrHostInvoked=False,generatedModuleImported=False,operationalAdmission=False,runtimeAcceptanceClaim=False,adoptionAllowed=False,fullResetOrReuse=False,als=False,qualifications=['Coarse Clocks may emit interfaces outside the exact two selections. Full bytes are captured before audit; such construction fails admission without automatic widening.','One fixture per new source-pinned Root phase; all activation/source-peer/component/runtime slots remain NULL.','An expected initializer rejection is generic and unattributed; a captured post-build interface rejection cannot count as that initializer control.','Opaque rejected object properties are not read/captured. Full owned stdout/stderr and fixed source stage/type transports are retained.','Actual glue/core/shim/clock type graphs and async ESM/TLA scalar loading require separate independent artifact/source gates; no generated import or timer export occurs here.'])
write('results.json',result)
write('source-receipt.json',dict(schemaVersion=1,state='RESOURCE342_COMPONENT_SOURCE_SEALED_V1',sourceOnly=True,results=descriptor(OWN/'results.json'),preparationManifest=descriptor(OWN/'input-freeze.json'),sourceChecks=descriptor(OWN/'source-check-results.json'),pureAndGrammar=descriptor(OWN/'evidence/summary.json'),allPreparationRowsRehashed=True,ownerHelperOrBootstrapOrPackagingOrGuestActionsInvoked=False,rootAuthority=None))
assert not any(p.is_symlink()for p in OWN.rglob('*'))
rows=[]
for p in sorted(OWN.rglob('*')):
 if p.is_file():
  r=descriptor(p);r['path']=p.relative_to(OWN).as_posix();rows.append(r)
write('index.json',dict(schemaVersion=1,state='RESOURCE342_COMPONENT_SOURCE_INDEX_V1',files=rows))
print(json.dumps(dict(index=descriptor(OWN/'index.json'),results=descriptor(OWN/'results.json'),receipt=descriptor(OWN/'source-receipt.json'),members=len(rows),inputs=len(manifest['files']),sourceOnly=True)))
