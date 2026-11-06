"""Compact WT companion Source publication only; never invoke target binaries."""
from pathlib import Path
import hashlib,json,os,subprocess,ast
OWN=Path(__file__).resolve().parent
assert not (OWN/'index.json').exists()
def read(n):return json.loads((OWN/n).read_bytes())
def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
refs=read('references.json');provenance=read('mechanism-provenance.json')
for r in [refs['node'],refs['wasmtime'],refs['wave'],refs['durableHost'],refs['comparator']['module']]:assert desc(r['path'])==r
source=(OWN/'companion.mjs').read_bytes();donor=Path(provenance['stdlibGuardDonor']['path']).read_bytes();n=provenance['exactPrefixBytes'];assert source[:n]==donor[:n]and hashlib.sha256(source[:n]).hexdigest()==provenance['stdlibGuardPrefixSha256']
test=read('parser-test.stdout.json');assert test['syntheticWaveCases']==13 and (OWN/'parser-test.stderr.log').read_bytes()==b''
grammar=[]
for name in ['companion.mjs','test-wave.mjs']:
 argv=[refs['node']['path'],'--check',str(OWN/name)];r=subprocess.run(argv,env={k:v for k,v in os.environ.items()if k not in ['NODE_OPTIONS','NODE_PATH']},capture_output=True,timeout=30);(OWN/(name+'.grammar.stdout.log')).write_bytes(r.stdout);(OWN/(name+'.grammar.stderr.log')).write_bytes(r.stderr);assert r.returncode==0 and not r.stderr;grammar.append(dict(argv=argv,rawExitCode=0,stdoutBytes=len(r.stdout),stderrBytes=0))
ast.parse(Path(__file__).read_bytes());root=read('root-authority.template.json');root['entrySha256']=desc(OWN/'companion.mjs')['sha256'];assert root['sourceIndex']is root['component']is root['sourceReviewedByRoot']is None;save('root-authority.template.json',root)
save('grammar-results.json',dict(schemaVersion=1,records=grammar,pythonAsts=1,actualTargetInvoked=False))
save('preparation-history.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_NO_ACTUAL_WASMTIME',stockWasmtimeExecuted=False,guestOrCryptoExecuted=False,rootAuthority=None))
save('results.json',dict(schemaVersion=1,state='UNEXECUTED_EXPERIMENTAL_HASH_HMAC357_WASMTIME3_SOURCE_COMPLETE_V1',sourceOnly=True,sourcePrepared=True,parentCallerIndex=refs['parentCallerIndex'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],nativeSourceFiles=357,rawMetadataFields=83,selectedWholeManifests=12,wasmtime=refs['wasmtime'],freshProcesses=3,argv=['run','--invoke','run()','<actual-root-approved-component>'],perChildDeadlineMs=180000,fullRawBeforeDecodeOrSemantics=True,wholeWaveDecoder=refs['wave'],comparator=refs['comparator'],expectedOrdinaryCallOrdinals=[1,1,1],actualSameArmFreshJcoStringRequired=True,wholeComparatorReturnAndExplicitPassRequired=True,parserCases=13,nodeGrammarChecks=2,pythonAsts=1,stdlibGuardPrefixByteIdentical=True,operationalParentEntryImported=False,stockWasmtimeExecuted=False,guestOrCryptoExecuted=False,generatedJsImported=False,newOracleExecuted=False,nativeBuildOrFreezeInvoked=False,sourceReviewedByRoot=None,rootAuthority=None,actualComponent=None,actualFreshJcoRawReturn=None,actualRuntimeResults=None,publicProfileAdmission=False,freezeOrSnapshotOrReuseOrSecurityOrCostAcceptance=False))
save('source-receipt.json',dict(schemaVersion=1,result=desc(OWN/'results.json'),references=desc(OWN/'references.json'),provenance=desc(OWN/'mechanism-provenance.json'),grammar=desc(OWN/'grammar-results.json'),parserTest=desc(OWN/'parser-test.stdout.json'),operationalActionsInvoked=False))
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():r=desc(p);r['path']=p.relative_to(OWN).as_posix();rows.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_WASMTIME_COMPANION_NO_ACTION_AUTHORITY_V1',files=rows))
assert {r['path']for r in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for name in ['index.json','results.json','source-receipt.json']:print(json.dumps(desc(OWN/name)))
