"""Independent read/hash/AST-data review. Does not import owner code."""
from pathlib import Path
import hashlib,json,stat,ast
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'ownership-wasmtime-candidate-v1'
EXPECTED='6f5d38ec7ff4df7b4eb063ec9d818b59b1f6e27005e28edb124f26a76f166256'
seen={}
def row(p):
 p=Path(p);before=p.stat();assert p.is_file() and not p.is_symlink()
 h=hashlib.sha256();n=0
 with p.open('rb')as f:
  while b:=f.read(1024*1024):h.update(b);n+=len(b)
 after=p.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
 d={'path':str(p),'sha256':h.hexdigest(),'bytes':n};old=seen.get(str(p));assert old is None or old==d;seen[str(p)]=d;return d
def verify(d):
 assert row(d['path'])=={k:d[k]for k in ['path','sha256','bytes']},d['path']
def read(d):verify(d);return json.loads(Path(d['path']).read_bytes())
def index(d):
 v=read(d);assert v['schemaVersion']==1;names=set()
 for r in v['files']:
  name=r['path'];assert name not in names and not Path(name).is_absolute() and all(x not in ('','.','..')for x in name.split('/'));names.add(name);verify({'path':str(Path(d['path']).parent/name),'sha256':r['sha256'],'bytes':r['bytes']})
 return v
own=row(SOURCE/'index.json');assert own['sha256']==EXPECTED;ix=index(own);assert len(ix['files'])==30
freeze=json.loads((SOURCE/'input-freeze.json').read_bytes());assert len(freeze['files'])==13425 and len({r['path']for r in freeze['files']})==13425
for r in freeze['files']:verify(r)
refs=json.loads((SOURCE/'references.json').read_bytes());normal=index(refs['normalReview']['index']);artifact=index(refs['artifactReview']['index'])
nr=read(refs['normalReview']['result']);ar=read(refs['artifactReview']['result']);nc=read(refs['normalContract']);ac=read(refs['artifactContract'])
for proof,contract in [(nr,nc),(ar,ac)]:
 assert proof['state']==contract['requiredReviewState']
 for k,v in contract['requiredFixedValues'].items():assert proof[k]==v,(k,proof.get(k),v)
assert nr['coverage']==nc['requiredCoverage'] and nc['artifacts']==ac['artifacts']==refs['artifacts']
assert ac['requiredFixedValues']['publicAbiFunctions']['validate']=='() -> string' and ac['requiredFixedValues']['emittedImports']==[]
assert nr['generatedModuleImported'] is True and nr['asyncGuestScalarObservedAsOrdinaryStrings'] is True and nr['stockWasmtimeExecuted'] is False and nr['gcExecuted'] is False
assert ar['generatedModuleImported'] is False and ar['keyOperationsInvoked'] is False
assert refs['artifacts']['component']['sha256']=='842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d' and refs['wasmtime']['sha256']=='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'
oi=read(refs['normalOutputIndex']);wr=refs['normalWrapper'];assert sum(r['path']=='wrapper/raw/001.json' and r['sha256']==wr['sha256'] and r['bytes']==wr['bytes']for r in oi['files'])==1
wrapper=read(wr);assert wrapper['name']=='validate' and wrapper['args']==[] and wrapper['returnedType']=='string' and wrapper['kind']=='return'
oracle=read(refs['nodeOracle']);assert oracle['node']=='v22.14.0' and len(oracle['keys'])==2
record=json.loads(wrapper['value']);assert len(record['records'])==4 and record['withinOneOuterExport'] is True and record['separateHostCallInterleavingProved'] is False
for p in SOURCE.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
guard=(SOURCE/'guard.mjs').read_text();run=(SOURCE/'run.mjs').read_text();protocol=(SOURCE/'protocol.mjs').read_text()
assert "return ['run','--invoke','validate()',row.path]"in protocol and 'invocation('not in protocol
assert run.index('checkOwnedTerminal(terminal)')<run.index('parseScalarStringOutput(')<run.index('JSON.parse(value)')<run.index('checkWholeRecord(record')
assert run.index("mkdir(join(out.root,'processes')")<run.index('await runOwnedCommand(')
assert 'JSON.stringify(value)===JSON.stringify(JSON.parse(expectedWrapper.value))'in protocol
assert 'loadSession('not in run and 'nodeOracle('not in run and 'cryptoOwnerBootstrapPreflight('not in guard
template=json.loads((SOURCE/'future-root-authority.template.json').read_bytes());assert template['wasmtimeValidateAllowed'] is False and template['sourceIndexSha256'] is None and template['sourceIndependentReview'] is None and template['externalController'] is None
for k in ['nodeOracleAllowed','generatedJsAllowed','gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim']:assert template[k]is False
assert template['freshProcesses']==3 and template['invocation']=='validate()' and template['workerTimeoutMs']==600000 and template['externalParentDeadlineSeconds']==2400
assert not Path(template['outputRoot']).exists()
result={'schemaVersion':1,'state':'INDEPENDENT_CRYPTO_OWNER355_WASMTIME_SOURCE_REVIEW_PASSED_V1','sourceIndexSha256':EXPECTED,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'sourceMembers':30,'inputReferences':13425,'uniqueInputsRehashed':len(seen),'componentSha256':refs['artifacts']['component']['sha256'],'actualNormalReviewIndexSha256':refs['normalReview']['index']['sha256'],'actualArtifactReviewIndexSha256':refs['artifactReview']['index']['sha256'],'actualWholeContractsAndCoverageUnchanged':True,'actualZeroArgumentStringAbiVerified':True,'literalArgv':['run','--invoke','validate()',refs['artifacts']['component']['path']],'rawStreamsAndTerminalBeforeDecoding':True,'wholeWrapperMatchesActualNormalRecord':True,'freshProcesses':3,'workerTimeoutMs':600000,'externalParentDeadlineSeconds':2400,'newRootAndControllerRequired':True,'allOtherActionsFalse':True,'readHashDataAndPythonAstOnly':True,'wasmtimeProcessGuestKeyOrCryptoActionsInvoked':False,'runtimeAcceptanceClaim':False,'operationalAdmission':False,'concreteBlockers':[],'limitations':['Source review only; no stock-Wasmtime key execution or backend/GC/free/wipe/isolated-root proof.','One ordinary validate export in each fresh process cannot prove separate-host-call interleaving or request reuse.','The new actual external Root controller and its2400s overall deadline remain required.','Existing16MiB per-pipe bound and2MiB decoded code-unit bound refuse oversize results; no clipping or full opaque return is accepted.']}
for name,value in [('rehashed-inputs.json',{'schemaVersion':1,'files':[seen[p]for p in sorted(seen)]}),('results.json',result)]:
 with (HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'state':result['state'],'members':30,'inputs':13425,'unique':len(seen),'ownerActionsInvoked':False}))
