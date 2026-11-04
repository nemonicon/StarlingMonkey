"""Seal source/data evidence only. Never invokes SDK, key or owner actions."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[3];OWNER=H.parent/'key-owner-candidate-v1';STAGE=Path('/private/tmp/starling-node-compat/consumers-source-v2')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with(H/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
assert not(H/'index.json').exists();refs={}
def add(path,role,expected=None,size=None):
 p=Path(path).absolute();assert p.is_file();raw=p.read_bytes();digest=sha(raw);assert expected is None or digest==expected,p;assert size is None or len(raw)==size,p
 row={'path':str(p),'realpath':str(p.resolve()),'isSymlink':p.is_symlink(),'sha256':digest,'bytes':len(raw)}
 if str(p)in refs:
  assert all(refs[str(p)][key]==value for key,value in row.items())
  if role not in refs[str(p)]['roles']:refs[str(p)]['roles'].append(role)
 else:refs[str(p)]={**row,'roles':[role]}
def indexed(root,expected,role):
 add(root/'index.json',role,expected)
 for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],role,row['sha256'],row['bytes'])
indexed(OWNER,'216d0272025145f70c3a1e1c5e4f27cc3cc47ef6f97ae8131467e803db3c47d0','IMMUTABLE_PARENT_OWNER_INDEXED_BYTES')
indexed(H.parent/'independent-key-owner-source-review-v1','a213a1e215336eff57701e816a843f36869a773e9a18298d82463746e20720e5','PARENT_INDEPENDENT_SOURCE_REVIEW_INDEXED_ONLY')
for row in json.loads((OWNER/'source-inputs.json').read_bytes())['files']:add(row['path'],'ORIGINAL_PARENT_PREPARATION_CONTEXT_NOT_RELOCATED',row['sha256'],row['bytes'])
parent=json.loads((OWNER/'source-derivations.json').read_bytes());new=json.loads((H/'source-derivations.json').read_bytes());before={row['path']:row['beforeSha256']for row in parent['files']};before[new['path']]=new['beforeSha256']
for path,digest in before.items():add(ROOT/path,'LIVE_UNMODIFIED_PREIMAGE',digest);add(STAGE/path,'CONFIGURED355_UNMODIFIED_PREIMAGE',digest)
composition=json.loads((H/'composition.json').read_bytes())
for row in composition['afterimages']:add(H/row['afterimage'],'UNAPPLIED_COMPOSED_SOURCE_AFTERIMAGE',row['sha256'],row['bytes'])
for row in json.loads((H/'evidence/dependencies.json').read_bytes())['files']:add(row['physicalPath'],'ACTUAL_SDK_DEPENDENCY_HASHED_AFTER_FRONTEND',row['sha256'],row['bytes'])
command=json.loads((H/'evidence/sdk-command.json').read_bytes());compiler=command['compiler'];add(compiler['path'],'SDK_FRONTEND_BINARY_NOT_COPIED',compiler['sha256'],compiler['bytes']);r=command['prototypeCompileCommands'];add(r['path'],'FROZEN_NORMAL355_RELEASE_COMMAND_DB',r['sha256'],r['bytes']);r=command['wrapper'];add(r['path'],'ACTUAL_RELEASE_COMPILER_WRAPPER',r['sha256'],r['bytes'])
for row in json.loads((H/'callsite-audit.json').read_bytes())['citations']:add(row['path'],'SOURCE_CONTROL_FLOW_AND_API_CITATION',row['sha256'],row['bytes'])
source=json.loads((H/'source-results.json').read_bytes());syntax=json.loads((H/'evidence/syntax-results.json').read_bytes());assert source['oldUnsafePrototypePathExecuted']is False and source['state']=='SOURCE_AND_BOOLEAN_MODEL_CHECKS_PASSED_NO_KEY_RUNTIME';assert syntax['exitCode']==syntax['errors']==syntax['warnings']==0
for p in H.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in sorted(H.rglob('*')):
 assert not p.is_symlink(),p
 if p.is_file()and p.name not in ['index.json','source-inputs.json','source-receipt.json']:add(p,'OWN_SOURCE_OR_ACTUAL_FRONTEND_TEXT_EVIDENCE')
put('source-inputs.json',{'schemaVersion':1,'state':'ORIGINAL_PREPARATION_CONTEXT_SOURCE_REFERENCES_NO_REBASING','originalPreparationRoot':str(H),'files':[refs[key]for key in sorted(refs)],'ownerPreparationRowsReinterpreted':False,'nativeOrPackagingAdmissionClosureClaim':False})
put('source-receipt.json',{'schemaVersion':1,'state':'UNAPPLIED_CRYPTO_PROTOTYPE_KEY_GUARD_SOURCE_SDK_SYNTAX_ONLY','ownerSourceIndexSha256':'216d0272025145f70c3a1e1c5e4f27cc3cc47ef6f97ae8131467e803db3c47d0','ownerIndependentSourceReviewIndexSha256':'a213a1e215336eff57701e816a843f36869a773e9a18298d82463746e20720e5','newSourceAfterimages':1,'newExactReversibleEdits':2,'parentAfterimagesPreservedExact':4,'composedSourceAfterimages':5,'composedExactEdits':20,'sourceChecks':source['checks'],'syntheticGuardModels':len(source['syntheticGuardModels']),'actualSdkFrontendRuns':1,'actualSdkFrontendExit':0,'warnings':0,'logicalDependencyFiles':syntax['logicalDependencies'],'headersPrehashedClaim':False,'sourcePreparationReferences':len(refs),'liveAndConfiguredSourcesChanged':False,'ownerPacketChanged':False,'oldUnsafePrototypePathExecuted':False,'keyCryptoGcGuestOrFullNativeBuildExecuted':False,'linkOrInstallExecuted':False,'newNativePolicyHelperRecipeOrPinsIssued':False,'allOwnerFollowonsStillOpen':True,'futureRootIntegrationAuthority':None,'runtimePrototypeRejectionResult':None,'operationalAdmission':False})
files=[]
for p in sorted(H.rglob('*')):
 if p.is_file()and p.name!='index.json':raw=p.read_bytes();name=str(p.relative_to(H));assert all(len(part.encode())<=255 for part in p.relative_to(H).parts);files.append({'path':name,'sha256':sha(raw),'bytes':len(raw)})
put('index.json',{'schemaVersion':1,'state':'SEALED_UNAPPLIED_CRYPTO_PROTOTYPE_KEY_GUARD_SOURCE_ONLY','files':files,'sourcePreparationReferences':len(refs),'runtimeOrAcceptanceClaim':False})
for row in files:assert sha((H/row['path']).read_bytes())==row['sha256']
print(json.dumps({'indexSha256':sha((H/'index.json').read_bytes()),'files':len(files),'inputs':len(refs),'receiptSha256':sha((H/'source-receipt.json').read_bytes()),'sourceChecks':source['checks'],'actualSdkFrontend':1,'unsafeKeyOrCryptoRuntime':False}))
