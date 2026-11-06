"""Own Source checks/seal only: pinned Node grammar and pure DATA tests.

Never imports the package, invokes construct(), or replays the 44,369 native
ledger. Operational authentication stays in the separately authorized caller.
"""
from pathlib import Path
import ast,hashlib,json,subprocess,time
OWN=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
refs=read(OWN/'references.json');facts=read(refs['packageFacts']['path']);seen={}
def capture(r):
 assert set(r)=={'path','sha256','bytes'} and Path(r['path']).is_absolute()
 assert d(r['path'])==r
 if r['path']in seen:assert seen[r['path']]==r
 seen[r['path']]=r
def family(ix):
 capture(ix);root=Path(ix['path']).parent;v=read(ix['path']);names={'index.json'}
 for row in v['files']:
  assert not Path(row['path']).is_absolute()and '..'not in Path(row['path']).parts
  assert row['path']not in names;names.add(row['path']);capture(dict(row,path=str(root/row['path'])))
 assert names=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
def descriptors(v):
 if isinstance(v,dict):
  if set(v)=={'path','sha256','bytes'}:capture(v)
  else:
   for x in v.values():descriptors(x)
 elif isinstance(v,list):
  for x in v:descriptors(x)
# Compact direct provenance: full BUILD proof family, references and actual API
# modules. Referenced current native/package ledgers are authenticated as DATA,
# not expanded into another historical input tree during Source authoring.
descriptors(refs);family(refs['nativeBuildReview']['index'])
for key in ['packageEntry','splicerCore','prunedAdapter','node','packageInventory']:capture(facts[key])
manifest=read(OWN/'private-native-manifest.json');capture(manifest['compiledCpp']);capture(manifest['diagnosticSourceIndex']);capture(manifest['diagnosticSourcePeerIndex'])
assert(OWN/'selector.mjs').read_bytes()==Path(refs['originalFixture']['path']).read_bytes()
assert(OWN/'selector.wit').read_bytes()==Path(refs['originalWit']['path']).read_bytes()
root=read(OWN/'root-authority.template.json');assert all(root[k]is None for k in ['sourceIndex','sourceReviewedByRoot','sourceReview','sourceReviewContract','outputRoot','privateTemporaryRoot','packageInitializationAllowed','componentConstructionAllowed','engineInitializationDuringConstructionAllowed','actualComponent','actualRuntime'])
assert all(refs[k]is None for k in ['sourceReview','rootAuthority','actualComponent','actualRuntime'])
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
commands=[];node=facts['node'];capture(node)
def run(argv,stem):
 started=time.monotonic();p=subprocess.run(argv,capture_output=True,timeout=90)
 (OWN/(stem+'.stdout.log')).write_bytes(p.stdout);(OWN/(stem+'.stderr.log')).write_bytes(p.stderr)
 row=dict(argv=argv,rawExitCode=p.returncode,stdout=d(OWN/(stem+'.stdout.log')),stderr=d(OWN/(stem+'.stderr.log')),elapsedOperationalSeconds=time.monotonic()-started,hostSourceOnly=True,packageOrEngineOrFixtureOrProbeInvoked=False)
 commands.append(row);assert p.returncode==0 and p.stderr==b''
 return p.stdout
for n in ['entry.mjs','models.mjs','selector.mjs','test-models.mjs']:
 assert run([node['path'],'--check',str(OWN/n)],'grammar-'+n)==b''
stdout=run([node['path'],str(OWN/'test-models.mjs')],'pure-tests')
test=json.loads(stdout);assert test['checks']==60 and test['packageOrComponentizerOrFixtureOrEngineOrProbeInvoked']is False
save('test.stdout.json',test);(OWN/'test.stderr.log').write_bytes(b'')
save('grammar-results.json',dict(schemaVersion=1,node=node,commands=commands,activePythonAsts=len(list(OWN.glob('*.py'))),packageOrComponentizerOrEngineOrProbeActionsInvoked=False))
for row in list(seen.values()):capture(row)
save('input-hashes.json',dict(schemaVersion=1,scope='Compact Source direct API/provenance/BUILD proof bytes only; full native and package operational ledgers remain referenced DATA, not rehashed here.',files=sorted(seen.values(),key=lambda r:r['path']),fullCurrentNativeLedgerAuthoringReplay=False,packageTreeAuthoringReplay=False))
save('results.json',dict(schemaVersion=1,state='PRIVATE_CLOCK_DIAGNOSTIC357_SELECTOR_COMPONENT_CALLER_SOURCE_READY_FOR_INDEPENDENT_REVIEW_V1',sourceOnly=True,sourceChecksPassed=True,nativeSourceFiles=357,externalEmbeddingSources=3,rawMetadataFields=82,selectedWholeManifests=11,nativeBuildReview=refs['nativeBuildReview'],engine=refs['engine'],metadata=refs['metadata'],fixture=refs['fixture'],wit=refs['wit'],rawFixtureByteIdentical=True,actualPackageEntry=facts['packageEntry'],actualSplicerCore=facts['splicerCore'],actualExplicitAdapter=facts['prunedAdapter'],actualAPI='componentize(sourceString, options)',componentCaptureBeforeAudit=True,selectedInterfaces=root['selectedInterfaces'],privateBuiltin='starling:test-clock-lifecycle',publicBuiltinMapUsed=False,actualFull82ClassificationConsumedAsData=True,pythonClassifierOrHelperInvoked=False,pureSourceChecks=test['checks'],grammarOnlyCommands=4,hostPureCommands=1,compactCurrentDescriptors=len(seen),sourceReview=None,rootAuthority=None,actualComponent=None,actualRuntime=None,ownerActionsInvoked=False,packageOrEngineOrGuestOrProbeActionsInvoked=False,compilerActionsInvoked=False,operationalAdmission=False,fullSeventeenGatesAccepted=False,qualifications=['Source-only unexecuted caller; the separate Root must issue a complete authority/config and fresh monitored Node before package/engine initialization.','The future operational caller rehashes the complete actual44369 native ledger and full4889+21 package. This compact Source authoring check does not claim another full-boundary replay.','Raw source/WIT and native private manifest are exact actual diagnostic357 inputs; no355/80 or Hash83 frame is constructed.','The entire actual component is retained before interface/WIT audits. Captured rejected bytes are not an admitted component.','Selected three standard0.2.10 interfaces do not close type/core/loading, natural-loop, Store-death, epoch, fatal-object identity, overflow, full17 lifecycle, profile, snapshot/reuse or security/cost gates.','Direct private package API is used because generic loadComponentizer pins another splicer and existing experimental loader audits before returning; original loaders and APIs are unchanged.']))
save('source-receipt.json',dict(schemaVersion=1,state='PRIVATE_CLOCK_DIAGNOSTIC357_SELECTOR_COMPONENT_SOURCE_SEALED_UNEXECUTED_V1',result=d(OWN/'results.json'),references=d(OWN/'references.json'),sourceContract=d(OWN/'future-source-review-contract.json'),tests=d(OWN/'test.stdout.json'),commands=d(OWN/'grammar-results.json'),inputHashes=d(OWN/'input-hashes.json'),ownerActionsInvoked=False,allFutureAuthoritiesUnissued=True))
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():rows.append(dict(d(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_PRIVATE_CLOCK_DIAGNOSTIC357_SELECTOR_COMPONENT_V1',files=rows))
assert {r['path']for r in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for n in ['index.json','results.json','source-receipt.json','future-source-review-contract.json']:print(json.dumps(d(OWN/n)))
