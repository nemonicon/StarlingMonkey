"""Seal source/evidence only, without importing JS or invoking an owner action."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
def data(p):return json.loads(p.read_bytes())
def row(p):
 b=p.read_bytes();return {'path':str(p.relative_to(HERE)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def save(p,value):
 with p.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert data(HERE/'evidence/pure-terminal.json')['rawExitCode']==0
assert data(HERE/'evidence/source-terminal.json')['rawExitCode']==0
pure=data(HERE/'evidence/pure.stdout.log');source=data(HERE/'evidence/source.stdout.log');syntax=data(HERE/'evidence/syntax.json')
assert pure['checks']==61 and source['checks']==13274 and source['inputRows']==13247
assert len(syntax['modules'])==7 and all(r['rawExitCode']==0 for r in syntax['modules']) and syntax['pythonAstParsed'] is True
save(HERE/'results.json',{'schemaVersion':1,'state':'CRYPTO_OWNER355_NORMAL_RUNTIME_SOURCE_PREPARATION_PASSED_V1','sourcePreparationPassed':True,'pureChecks':61,'sourceDataChecks':13274,'inputRows':13247,'jsParseChecks':7,'pythonAstChecks':1,'actualComponent':'842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d','actualComponentReview':'8be6c70b212922b201ed4e4439f903b01aad53f2d7b31999e0e0a3d31ff82200','generatedModuleImported':False,'guestOrNodeKeyHmacOperationsInvoked':False,'workerOrHostOrNativeActionInvoked':False,'sourceIndependentReview':None,'rootRuntimeAuthority':None,'normalRuntimeResults':None,'operationalAdmission':False,'runtimeAcceptanceClaim':False})
files=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file():
  assert not p.is_symlink();assert p.name not in ('index.json','source-receipt.json');files.append(row(p))
save(HERE/'index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_CRYPTO_OWNER355_NORMAL_RUNTIME_V1','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
save(HERE/'source-receipt.json',{'schemaVersion':1,'state':'CRYPTO_OWNER355_NORMAL_RUNTIME_SOURCE_SEALED_NOT_EXECUTED','index':row(HERE/'index.json'),'sourceMembers':len(files),'inputRows':13247,'sourceIndependentReview':None,'rootRuntimeAuthority':None,'actualRuntime':None,'generatedModuleImported':False,'keyOperationsInvoked':False})
print(json.dumps({'index':row(HERE/'index.json'),'files':len(files),'inputRows':13247,'sourceOnly':True}))
