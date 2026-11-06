"""Run finite host Source checks, retain raw evidence, seal own Source once."""
import hashlib,json,os,stat,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
assert not (OWN/'index.json').exists(), 'Sealed family is immutable'
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb')as file:
  for chunk in iter(lambda:file.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def desc(path):
 path=Path(path).absolute();return dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size)
def write(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
refs=json.loads((OWN/'references.json').read_bytes());node=refs['node']
assert sha(node['path'])==node['sha256']and Path(node['path']).stat().st_size==node['bytes']
raw=OWN/'checks';raw.mkdir(exist_ok=False)
records=[]
commands=[('01-input-before',[sys.executable,'-B',str(OWN/'check-source.py')]),('02-python-pure',[sys.executable,'-B',str(OWN/'test-models.py')]),('03-manifest-pure',[node['path'],str(OWN/'test-manifests.mjs')]),('04-bash-grammar',['/bin/bash','-n',str(OWN/'build-engine.sh')]),('05-manifest-grammar',[node['path'],'--check',str(OWN/'manifest-model.mjs')]),('06-test-grammar',[node['path'],'--check',str(OWN/'test-manifests.mjs')]),('07-input-final',[sys.executable,'-B',str(OWN/'check-source.py')])]
for label,argv in commands:
 result=subprocess.run(argv,cwd=OWN,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,check=False)
 for suffix,payload in [('stdout',result.stdout),('stderr',result.stderr)]:
  with open(raw/(label+'.'+suffix),'xb')as output:output.write(payload);output.flush();os.fsync(output.fileno())
 record=dict(argv=argv,cwd=str(OWN),rawExitCode=result.returncode,stdout=desc(raw/(label+'.stdout')),stderr=desc(raw/(label+'.stderr')),hostSourceOrPureOnly=True,engineExecuted=False,cryptoOperationsInvoked=False)
 with open(raw/(label+'.terminal.json'),'x')as output:json.dump(record,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
 records.append(record)
 assert result.returncode==0 and result.stderr==b'',label
assert sha(node['path'])==node['sha256']
source=json.loads((OWN/'source-check-results.json').read_bytes());pure=json.loads((OWN/'pure-check-results.json').read_bytes());manifest=json.loads((OWN/'manifest-check-results.json').read_bytes());policy=json.loads((OWN/'policy.json').read_bytes())
roles={name:desc(OWN/path)for name,path in dict(policy='policy.json',helper='layer-policy.py',recipe='build-engine.sh',admissionModel='native-admission-model.py',hashHmacModel='hash-hmac-model.py',manifestModel='manifest-model.mjs',cryptoModuleManifest='crypto-module-manifest.json',nativeOrigins='native-origins.json',embeddingOrigins='embedding-origins.json',toolOrigins='tool-origins.json',stageInputPlan='stage-input-plan.json',sourceChecks='source-check-results.json',pureChecks='pure-check-results.json',manifestChecks='manifest-check-results.json',toolingDerivations='tooling-derivations.json',policyDelta='policy-delta.json',inputHashes='input-hashes.json',references='references.json',futureSourceReviewContract='future-source-review-contract.json',futureAuthority='future-authority.json').items()}
result=dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_NATIVE_INTEGRATION_SOURCE_PREPARED_V1',sourceOnly=True,sourcePreparationPassed=True,independentSourceReview=None,nativeSourceFiles=357,retainedParentNativeFiles=353,changedParentNativeFiles=2,newNativeFiles=2,externalEmbeddingSources=3,selectedNativeManifests=11,selectedPackagingManifests=1,selectedManifestCount=12,initialVariant='normal-off',hashHmacEnabledForInitialExperimentalBuild=True,globalHashHmacDefaultEnabled=False,auditedBorrowEnabled=False,copyOnly=True,expectedCompilation=policy['expectedCompilation'],expectedRawMetadataFields=83,contexts=policy['contexts'],sourceChecks=source,pureChecks=pure['checks'],manifestChecks=manifest['checks'],hostCheckCommands=records,artifacts=roles,scope='UNAPPLIED new Source/producer/shape models. Actual previous355 engine is ancestry DATA only; SDK proof is frontend-only.',inputBoundary='2622 current references/seven indexed families; no recursive claim over unrelated historical receipts or every nested BUILD reference.',sdkSyntaxIsLinkedNativeProof=False,actualStage=None,actualBuild=None,actualMetadata=None,actualEngine=None,actualFreeze=None,pins=None,bootstrap=None,component=None,runtime=None,stageActionsInvoked=False,nativeBuildActionsInvoked=False,ownerActionsInvoked=False,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False,remainingGates=['independent Source peer','genuine owned stage/build controllers and fresh Root phases','actual HASH_HMAC-enabled COPY-only357 build and full new83 metadata proof','new357 admission/freezer/verifier/export/pins/bootstrap','actual algorithm/output/alias/default/descriptor/refusal/GC/finalizer/snapshot/zeroization tests','separate BORROW gate','full profile adoption and existing15 zlib differences/backend-version evidence'])
write('results.json',result)
contract=dict(schemaVersion=1,state='PROSPECTIVE_NODE_CRYPTO_HASH_HMAC357_SOURCE_INTEGRATION_CONTRACT_V1',results=desc(OWN/'results.json'),artifacts=roles,nativeSourceFiles=357,retainedParentNativeFiles=353,changedParentNativeFiles=2,newNativeFiles=2,externalEmbeddingSources=3,selectedManifestCount=12,initialVariant='normal-off',contexts=policy['contexts'],expectedCompilation=policy['expectedCompilation'],expectedRawMetadataFields=83,rawMetadataGateApi='validate_metadata(metadata,policy,policy_sha256,helper_sha256,recipe_sha256,external_sources,variant)',rawMetadataGateResult='FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',producerHelperApi='decorate(metadata,repo,source_dir,entries,embedding_commands,enabled,ninja_capture,ninja_text)',packagingSourceApi='validateHashHmacSelectedManifests(values,policy,schema); later genuine builtinMap(full12)/bundleProfile(...builtinManifests:full12) after actual new357 admission',actualIndependentSourcePeer=None,allActionAuthority=None,operationalAdmission=False,grantsAnyActionAuthority=False)
write('source-contract.json',contract)
write('source-receipt.json',dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_SOURCE_FAMILY_SEALED_V1',sourceOnly=True,results=desc(OWN/'results.json'),contract=desc(OWN/'source-contract.json'),sourceChecks=roles['sourceChecks'],currentInputReferences=2622,indexedInputFamilies=7,hostSourceChecksRawZero=7,sourceDataChecks=source['checks'],pureModelChecks=pure['checks'],manifestChecks=manifest['checks'],stageActionsInvoked=False,nativeBuildActionsInvoked=False,engineExecuted=False,cryptoOperationsInvoked=False,independentReview=None,allActionAuthority=None))
files=[]
for path in sorted(OWN.rglob('*')):
 if not path.is_file():continue
 assert not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode)
 relative=str(path.relative_to(OWN));assert relative!='index.json'
 assert '__pycache__'not in path.parts and path.suffix not in ['.pyc','.o','.a','.wasm']
 files.append(dict(path=relative,sha256=sha(path),bytes=path.stat().st_size))
write('index.json',dict(schemaVersion=1,state='SEALED_NODE_CRYPTO_HASH_HMAC357_NATIVE_INTEGRATION_SOURCE_V1',files=files))
print(json.dumps(dict(index=desc(OWN/'index.json'),results=desc(OWN/'results.json'),contract=desc(OWN/'source-contract.json'),receipt=desc(OWN/'source-receipt.json'),members=len(files),indexedBytes=sum(r['bytes']for r in files))))
