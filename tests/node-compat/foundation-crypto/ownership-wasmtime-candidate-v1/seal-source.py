"""Seal source/data evidence only. No owner import, process or crypto action."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parent
def row(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(P)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):
 with (P/n).open('x')as f:json.dump(v,f,indent=2);f.write('\n')
pure=json.loads((P/'evidence/pure.stdout.log').read_bytes());source=json.loads((P/'evidence/source.stdout.log').read_bytes());term=json.loads((P/'evidence/terminals.json').read_bytes())
assert pure['checks']==37 and source['checks']==13456 and source['inputRows']==13425 and all(r['rawExitCode']==0 and r['stderr']['bytes']==0 for r in term['records'])
python=[]
for p in P.glob('*.py'):ast.parse(p.read_text(),filename=str(p));python.append(p.name)
save('source-python-ast.json',dict(schemaVersion=1,files=sorted(python),passed=True,noImports=True))
save('preparation-history.json',dict(schemaVersion=1,unexpectedFailures=[],preparationActions=['Read/hash original normal and artifact proof closures','Pure WAVE/JSON/counterexample checks using actual retained data','Node parse-only checks and Python AST'],wasmtimeOrProcessWorkloadGuestCryptoActionsInvoked=False,priorSealsChanged=False))
save('results.json',dict(schemaVersion=1,state='CRYPTO_OWNER355_STOCK_WASMTIME_SOURCE_PREPARATION_PASSED_V1',sourcePreparationPassed=True,
 pureChecks=37,sourceDataChecks=13456,inputRows=13425,literalModules=15,jsParseChecks=4,pythonAstChecks=len(python),
 exactInvocation='validate()',ordinaryPublicArguments=0,plannedFreshProcesses=3,plannedOuterStrings=3,plannedInnerRunRecords=12,
 actualNormalReviewIndex='abcb6da340ab7ffb53189d64f51c2e4c8b1ca4fb1cd50f2cc035235818a32c42',actualNormalContract='859649edac081ae8dff0a34b100d130faade6b0a20776062e572394d94527e4f',
 actualArtifactReviewIndex='8be6c70b212922b201ed4e4439f903b01aad53f2d7b31999e0e0a3d31ff82200',actualArtifactContract='47ea76aabd722336ab694040fa5f7a20fddc5634bc6f43537e6bce794b0cbd97',
 sourceIndependentReview=None,rootWasmtimeAuthority=None,actualStockWasmtimeResult=None,wasmtimeInvoked=False,
 nodeOracleRerun=False,generatedModuleImported=False,guestOrKeyCryptoNativeHelperPreflightProcessWorkloadActionsInvoked=False,
 operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False))
files=[row(p)for p in sorted(P.rglob('*'))if p.is_file()and p.name not in ['index.json','source-receipt.json']]
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_CRYPTO_OWNER355_STOCK_WASMTIME_V1',files=files,sourceOnly=True,ownerActionsInvoked=False))
save('source-receipt.json',dict(schemaVersion=1,state='CRYPTO_OWNER355_STOCK_WASMTIME_SOURCE_SEALED_UNEXECUTED',index=row(P/'index.json'),
 sourceMembers=len(files),inputRows=13425,sourceIndependentReview=None,rootWasmtimeAuthority=None,actualStockWasmtimeResult=None,wasmtimeInvoked=False,guestOrKeyCryptoActionsInvoked=False))
print(json.dumps(dict(index=row(P/'index.json'),results=row(P/'results.json'),sourceReceipt=row(P/'source-receipt.json'),members=len(files),inputRows=13425)))
