"""Own finite source/data sealer; no parser test, library or target is rerun."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def row(p,relative=False):
 p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes()
 return dict(path=p.relative_to(HERE).as_posix()if relative else str(p.absolute()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def load(p):return json.loads(Path(p).read_bytes())
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
test=load(HERE/'evidence/results.json');helper=row(HERE/'bindings.mjs')
assert test['helperSha256']==helper['sha256']and test['syntheticCases']==60
assert len(test['realSourceCases'])==2 and [len(r['observed'])for r in test['realSourceCases']]==[3,0]
inputs=[]
for r in test['realSourceCases']:
 actual=row(r['path']);assert(actual['sha256'],actual['bytes'])==(r['sha256'],r['bytes']);inputs.append(actual)
tool=Path('/private/tmp/starling-node-compat/toolchain/node_modules/rolldown')
assert load(tool/'package.json')['version']=='1.2.16'
inputs += [row(tool/p)for p in ['package.json','dist/parse-ast-index.mjs','dist/parse-ast-index.d.mts']]
inputs.append(row('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'))
write('input-hashes.json',dict(schemaVersion=1,files=inputs,parsedLibrarySourcesAreExternalData=True,analyzedModulesExecuted=False))
write('results.json',dict(schemaVersion=1,state='PURE_LEXICAL_BINDINGS_HELPER_SOURCE_PREPARED_V2',sourceOnly=True,sourcePrepared=True,sourceChecksPassed=True,independentSourceReview=None,helper=helper,api='findUnboundReferences(ast,names)',pureSyntheticCases=60,astNonMutationCases=62,realSourceParsedOnlyCases=2,realReactUnboundProcessReferences=3,realReactDomEdgeUnboundProcessReferences=0,realRendererLocalProcessClaim=False,parserInvoked=True,lexicalAnalyzerInvoked=True,analyzedModulesExecuted=False,frameworkPackageExecuted=False,componentizerInvoked=False,nativeEngineExecuted=False,guestExecuted=False,compilerInvoked=False,optionalBundlerApproved=False,rootActionAuthority=None,runtimeAcceptance=False))
write('source-receipt.json',dict(schemaVersion=1,state='SEALED_PURE_LEXICAL_BINDINGS_SOURCE_V2',helper=helper,results=row(HERE/'results.json'),contract=row(HERE/'source-contract.json'),testEvidence=row(HERE/'evidence/results.json'),inputs=row(HERE/'input-hashes.json'),allInputsRehashed=True,rootActionAuthority=None))
for r in inputs:assert row(r['path'])==r
files=[row(p,True)for p in sorted(HERE.rglob('*'))if p.is_file()and p.name!='index.json']
assert not any(p.is_symlink()for p in HERE.rglob('*'))
write('index.json',dict(schemaVersion=1,state='SEALED_PURE_LEXICAL_BINDINGS_HELPER_SOURCE_V2',files=files))
print(json.dumps(dict(index=row(HERE/'index.json'),members=len(files),helper=helper,results=row(HERE/'results.json'),contract=row(HERE/'source-contract.json'),receipt=row(HERE/'source-receipt.json'),syntheticCases=60,realParsedOnly=2)))
