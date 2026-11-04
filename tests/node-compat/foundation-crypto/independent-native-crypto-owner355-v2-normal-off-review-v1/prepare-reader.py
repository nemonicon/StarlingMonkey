"""Derive an owned data reader from the prior independent reader as source DATA.

This script never imports or executes that donor or any project/owner helper.
"""
from pathlib import Path
import hashlib,json

P=Path(__file__).resolve().parent
BASE=P.parent.parent/'foundation-stream-consumers/independent-native-consumers-v2-normal-off-review-v1/verify.py'
text=BASE.read_text()
changes=[]
def replace(a,b):
 global text
 assert text.count(a)==1,(a[:100],text.count(a))
 text=text.replace(a,b)
 changes.append(dict(beforeSha256=hashlib.sha256(a.encode()).hexdigest(),afterSha256=hashlib.sha256(b.encode()).hexdigest(),beforeBytes=len(a.encode()),afterBytes=len(b.encode())))
def span(a,z,b):
 global text
 start=text.index(a);end=text.index(z,start);replace(text[start:end],b)
replace("from pathlib import Path\nimport hashlib,json,os,re,shlex,stat,sys,tarfile", "from pathlib import Path\nimport hashlib,json,os,re,shlex,stat,sys,tarfile,struct")
replace("SOURCE=Path('/tmp/starling-node-compat/consumers-source-v2').resolve()", "SOURCE=Path('/private/tmp/starling-node-compat/crypto-owner-source-v2')")
replace("STAGED=SOURCE/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2'", "STAGED=SOURCE/'tests/node-compat/foundation-crypto/native-integration-candidate-v2'")
replace("FROZEN=Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze')", "FROZEN=Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')")
replace("WORK=Path('/tmp/starling-node-compat/consumers-v2-build')", "WORK=Path('/tmp/starling-node-compat/crypto-owner-v2-build')")
for a,b in {
 '9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378':'68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575',
 '661ef79418ab139c9a7bcebb57eb36c17c3c398f67c80bbcd680cb95839f0c79':'36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05',
 '860e95213953e26f96ca74946495a9719253f05cbca6c221a9b4b44d83962f92':'8bafca1a1a76168eebe2bbbb6cd774215db43a3c44c3a8ce9253d0152373ca37',
 '3a5fa8cd58d3948c373b59ff486eae5792ae7ec1b51ed47f43f4edc5b39b4c68':'eec3245841fff07e5bf9c3ff7b488106c94b71705262b22272d60a8ea4d7bfb3',
 'f174d2e38cfe5f9a3de268ff04468cdc57abcdfb33f7577962690cfcbe12df98':'5a3bd48ebac975f7a3fd72691432b34c0e4afb9eec33bd2ad6273d78225193f9',
 '21f7be307c0fd2f34ce7dbd1cfdb433a7965a5f02c45c78290b4705fd0796448':'4e5a1019ceffea629f2ec0b42322e17444cb877519596cb273ea34464d15bd78',
 }.items():replace(a,b)
span('checkpoint_raw=', 'seen={}', 'MUTABLE={}\nMUTABLE_READ_REQUESTS=[]\n')
span("ROOT_SHA=", "f=doc(FROZEN/", '''ROOT_SHA='88cfe19d16f09f0dba109d6e0b3923000116be286102ee6d4c20ca60d48d4bba'
FREEZE_SHA='d088286c6eadc20a7262a06fd804c9e2c597c7959a2d15762306c442161f7760'
assert not(HERE/'results.json').exists()
root=doc(FAMILY/'native-freezer-v1-normal-off-root-results.json',ROOT_SHA)
def descriptors(value):
 if isinstance(value,dict):
  if set(value)=={'path','sha256','bytes'}:read(Path(value['path']),value['sha256'],value['bytes'],capture=False)
  else:
   for child in value.values():descriptors(child)
 elif isinstance(value,list):
  for child in value:descriptors(child)
descriptors(root)
buildroot=doc(Path(root['completedBuildResult']['path']),root['completedBuildResult']['sha256']);descriptors(buildroot)
terminals=[]
for role,descriptor in [('build',buildroot['externalTerminal']),('freeze',root['actualFreezeTerminal']),('verify',root['actualVerificationTerminal'])]:
 terminal=doc(Path(descriptor['path']),descriptor['sha256']);descriptors(terminal)
 assert terminal['rawExitCode']==0 and terminal['timeout']is False
 assert read(Path(terminal['stderr']['path']),terminal['stderr']['sha256'],terminal['stderr']['bytes'])==b''
 terminals.append({'role':role,**terminal,'observedByThisReader':False})
assert [t['pid']for t in terminals]==[53008,79054,80524]
assert root['freezeRootSessionId']==25578 and root['verifyRootSessionId']==43902 and buildroot['rootSessionId']==62629
owner=indexed(PACKET,INDEX,44);indexed(STAGED,INDEX,44)
indexed(FAMILY/'independent-crypto-owner355-native-integration-v2-source-review-v1','ebbfda800fc288ea249b9c2e3af2f77a6a0ae1153bc9586b9aab91999a060dac',8)
indexed(FAMILY/'independent-native-integration-v2-stage-review-v1','8c0583a4863bc33b74b500ffe026d67fce2258985eb562b5f895a76636541c79',8)
amendment=FAMILY/'native-freezer-source-amendment-v1'
indexed(amendment,'0ff37e52888f37ffdc0bd2dc13870c327faadac5889fb495b53bb9549e5ecccd',13)
indexed(FAMILY/'independent-native-freezer-source-review-v1','aa25647e8d918b23d3b13d8d14d3da566d42ad9921d174d3dcbd87e1c8b4a06b',7)
policy=doc(PACKET/'policy.json',POLICY);tools=doc(PACKET/'artifact-tools/tool-pins.json')
native=inventory(policy['expectedNativeSourceManifest'],355);assert len(tools['toolDependencies'])==922
for name,h in native.items():read(SOURCE/name,h,anchor=SOURCE,capture=False)
for row in tools['toolDependencies']:read(SOURCE/relative(row['path']),row['sha256'],row['bytes'],SOURCE,capture=False)
preparation=doc(PACKET/'input-freeze.json');assert len(preparation['files'])==1323 and preparation['parentPreparationManifestsFollowed']is False
for row in preparation['files']:read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
for name in['bootstrap-pins.json','runtime-pins.json']:assert all(v is None for v in doc(PACKET/name)['variants'].values())
''')
replace("f['state']=='immutable-consumers-release-engine-frozen'", "f['state']=='immutable-crypto-owner-release-engine-frozen'")
# Every old artifact byte count is replaced; this is data-model adaptation,
# never acceptance of an old result/receipt or old metadata under new pins.
text=text.replace('10002283','10002820').replace("admission['toolDependenciesVerified']==767","admission['toolDependenciesVerified']==922")
replace("engine_path=Path(m['enginePath']);assert str(engine_path)==f['originalEngine'];assert read(engine_path,ENGINE,10002820,capture=False)", "engine_path=Path(f['originalEngine']);assert engine_path.resolve()==Path(m['enginePath']).resolve();assert read(engine_path,ENGINE,10002820,capture=False)")
replace("admission['state']=='ACTUAL_FINITE_CONSUMERS_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'", "admission['state']=='ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'")
replace("for name in['build-one.py','freeze-engine.py','artifact_common.py','metadata-admission.mjs','export-pin-candidate.py','tool-pins.json','parent-inputs.json']:plan('artifact-tools/'+name,read(STAGED/'artifact-tools'/name,capture=False)['sha256'],STAGED/'artifact-tools'/name,True)", '''for name in['build-one.py','freeze-engine.py','artifact_common.py','metadata-admission.mjs','export-pin-candidate.py','tool-pins.json','parent-inputs.json']:
 target='artifact-tools/donor-data/freeze-engine.py'if name=='freeze-engine.py'else'artifact-tools/'+name
 plan(target,read(STAGED/'artifact-tools'/name,capture=False)['sha256'],STAGED/'artifact-tools'/name,True)
plan('artifact-tools/freeze-engine.py',read(amendment/'freeze-engine.py',capture=False)['sha256'],amendment/'freeze-engine.py',True)
plan('artifact-tools/active-freezer/freezer-guard.py',read(amendment/'freezer-guard.py',capture=False)['sha256'],amendment/'freezer-guard.py',True)
correction=doc(FROZEN/'normal-off-freezer-correction-control.json',f['freezerSourceCorrection']['sha256'])
assert correction['state']=='ACTUAL_AUTHORIZED_CRYPTO_FREEZER_SOURCE_CORRECTION_CAPTURE'
assert correction['amendmentSourceIndex']['sha256']=='0ff37e52888f37ffdc0bd2dc13870c327faadac5889fb495b53bb9549e5ecccd'
assert correction['donorSourceIndexSha256']==INDEX and correction['configuredSourceRoot']==str(SOURCE) and correction['stagedArtifactToolsRoot']==str(STAGED/'artifact-tools') and correction['freezeRoot']==str(FROZEN)
assert correction['nativeRecipePolicyHelperAnd922ToolsUnchanged']is True and correction['engineExecuted']is False
descriptors(correction)
control_expected=[]
for source_index in[correction['amendmentSourceIndex'],{'path':str(PACKET/'index.json'),'sha256':INDEX,'bytes':(PACKET/'index.json').stat().st_size},correction['independentSourceReview']['index']]:
 control_expected.append(source_index)
 ix=doc(Path(source_index['path']),source_index['sha256']);base=Path(source_index['path']).parent
 for row in ix['files']:control_expected.append({'path':str(base/row['path']),'sha256':row['sha256'],'bytes':row['bytes']})
control_expected.append(correction['rootAuthority'])
assert len(correction['copies'])==len(control_expected)
for n,row in enumerate(control_expected):
 name='normal-off-freezer-correction-control/'+str(n)+'-'+Path(row['path']).name
 expected={'original':row['path'],'path':str(FROZEN/name),'sha256':row['sha256'],'bytes':row['bytes']}
 assert correction['copies'][n]==expected;plan(name,row['sha256'],Path(row['path']))
plan('normal-off-freezer-correction-control.json',f['freezerSourceCorrection']['sha256'])
for key,target,role in [('activeFreezerTooling','artifact-tools/freeze-engine.py','ACTUAL_ACTIVE_CORRECTED_FREEZER'),('donorFreezerTooling','artifact-tools/donor-data/freeze-engine.py','IMMUTABLE_STAGED_DONOR_DATA_NOT_ACTIVE')]:
 value=f[key];assert value['role']==role and Path(value['path']).resolve()==(FROZEN/target).resolve() and copies[target]['sha256']==value['sha256']
assert f['helperSha256']==f['activeFreezerTooling']['sha256']==correction['activeSource']['sha256']=='dc479abf2b703080dbaa7b8013a7be531ccd54015955afb1d48c645a89169613'
assert f['donorFreezerTooling']['sha256']==correction['donorSourceData']['sha256']=='44dd669ab05349514108dadf1a8a72eaae60d969335c8caaa80985a09eacc25f'
assert f['freezerSourceCorrection']['sourceIndexSha256']==correction['amendmentSourceIndex']['sha256']
assert root['activeFreezerTooling']==f['activeFreezerTooling']and root['donorFreezerTooling']==f['donorFreezerTooling']
''')
replace("root['originalInputEntries']", "root['originalRowsRehashed']")
replace("assert set(copies)|{'normal-off-freeze-receipt.json'}<=actual_frozen", "assert set(copies)|{'normal-off-freeze-receipt.json'}==actual_frozen\nassert len(actual_frozen)==1391\nassert not any(p.is_symlink()for p in FROZEN.rglob('*'))")
span("assert len(copies)==1164", "universal=read(", '''assert len(copies)==1390 and sum(row['original']is not None for row in copies.values())==1387
assert m['cryptoKeyOwnershipPolicy']==f['cryptoKeyOwnershipPolicy']==policy['cryptoKeyOwnershipSourcePolicy']
crypto=policy['cryptoKeyOwnershipSourcePolicy'];assert crypto['sourceFiles']==355 and crypto['changedSourceFiles']==5 and crypto['unchangedParentFiles']==350 and crypto['exactComposedEdits']==20
parent355=doc(SOURCE/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/policy.json',crypto['parent355PolicySha256'])
parent_native=inventory(parent355['expectedNativeSourceManifest'],355)
assert {name for name in native if native[name]!=parent_native[name]}=={row['path']for row in crypto['changes']}
for row in crypto['changes']:
 assert parent_native[row['path']]==row['beforeSha256']and native[row['path']]==row['afterSha256']
 read(Path(row['afterimage']),row['afterSha256'],row['bytes'],capture=False)
crypto_evidence=m['cryptoKeyOwnershipBuildEvidence']
assert cache['ENABLE_BUILTIN_WEB_CRYPTO']=='ON'and crypto_evidence['cryptoBuiltinEnabled']is True
assert crypto_evidence['cachePath']==m['cmakeCachePath']and crypto_evidence['cacheSha256']==m['cmakeCacheSha256']
assert install.count('NS_DEF(builtins::web::crypto)')==1 and crypto_evidence['installationSource']=={'path':w['install']['path'],'sha256':w['install']['sha256'],'namespace':'NS_DEF(builtins::web::crypto)','count':1}
assert sorted(crypto_evidence['changedNativeCompileCommands'])==sorted(mapped[row['path']]for row in crypto['changes']if row['path'].endswith('.cpp'))and len(crypto_evidence['changedNativeCompileCommands'])==3
# Pure static GNU archive-index decoding, not nm, compiler or crypto execution.
archive_bytes=read(FROZEN/'normal-off-libcrypto.a',ssl['library']['sha256'],ssl['library']['bytes'])
assert archive_bytes[:8]==b'!<arch>\\n';offset=8;ar_members={};symbol_index=None;long_names=b''
while offset<len(archive_bytes):
 header=archive_bytes[offset:offset+60];assert len(header)==60 and header[58:60]==b'`\\n'
 name=header[:16].decode().strip();size=int(header[48:58]);payload=archive_bytes[offset+60:offset+60+size];assert len(payload)==size
 ar_members[offset]=(name,payload)
 if name=='/':symbol_index=payload
 if name=='//':long_names=payload
 offset+=60+size+(size%2)
assert offset==len(archive_bytes)and symbol_index is not None
symbol_count=struct.unpack('>I',symbol_index[:4])[0];member_offsets=struct.unpack('>'+str(symbol_count)+'I',symbol_index[4:4+4*symbol_count]);symbol_names=symbol_index[4+4*symbol_count:].split(b'\\0')
crypto_archive_symbols={}
for name in['OPENSSL_cleanse','EVP_PKEY_free']:
 matches=[i for i,symbol in enumerate(symbol_names[:symbol_count])if symbol==name.encode()];assert len(matches)==1
 member_offset=member_offsets[matches[0]];member_name,payload=ar_members[member_offset]
 if member_name.startswith('/')and member_name[1:].isdigit():member_name=long_names[int(member_name[1:]):].split(b'/\\n',1)[0].decode()
 assert payload[:8]==b'\\0asm\\x01\\0\\0\\0'
 crypto_archive_symbols[name]={'archiveSha256':ssl['library']['sha256'],'gnuArchiveIndexSymbol':name,'memberOffset':member_offset,'memberName':member_name,'memberCoreWasmMagic':True,'runtimeExecuted':False}
link_crypto=[word for word in compiler if word.endswith('/libcrypto.a')];assert len(link_crypto)==1 and(build/link_crypto[0]).resolve()==Path(ssl['library']['path']).resolve()
assert 'starling-raw.wasm/libbuiltin_web_crypto.a'in compiler
assert ssl['version']=='3.0.17'and ssl['entropy']=='OFF'and ssl['randSeed']=='none'and ssl['profile']=='ON'
assert audit['patchedSources']=={'crypto/uid.c':'86b53aecb1046e81dfbfe74d779704b408cbaa70abfb9a7d1cc98211bdc8ba08','crypto/rand/rand_lib.c':'e8c853b5d609b5b13f3a63ddcd88047a37fb75afa59e88d1950907c5a85bcd95'}
assert ssl['randPatchSha256']==native['deps/patches/rand.patch']
assert cache['ENABLE_BUILTIN_WEB_CRYPTO']=='ON'and cache['CMAKE_EXE_LINKER_FLAGS']==''
verification=doc(Path(root['genuineVerificationResult']['path']),root['genuineVerificationResult']['sha256'])
assert verification['freezeReceipt']['sha256']==FREEZE_SHA and verification['engine']['sha256']==ENGINE and verification['metadata']['sha256']==META
assert verification['genuineConfiguredApiInvoked']=='verify_frozen_variant(normal-off,return_receipt_digest=True)'and verification['configuredSourceRoot']==str(SOURCE)
verify_source=read(Path(root['verificationEntrySource']['path']),root['verificationEntrySource']['sha256']).decode()
assert 'verify_frozen_variant'in verify_source and 'return_receipt_digest=True'in verify_source
root_reader_history=doc(Path(buildroot['priorRootReaderPreparationFailure']['path']),buildroot['priorRootReaderPreparationFailure']['sha256'])
assert root_reader_history['state'].find('READER')>=0 or 'reader'in str(root_reader_history).lower()
''')
span("result={'schemaVersion':1", "with(HERE/'results.json')", '''result={'schemaVersion':1,'state':'INDEPENDENT_CRYPTO_OWNER355_V2_NORMAL_OFF_NATIVE_ARTIFACT_REVIEW_PASSED_V1','sourceIndexSha256':INDEX,'rootReceiptSha256':ROOT_SHA,'freezeReceiptSha256':FREEZE_SHA,'metadataSha256':META,'receiptSha256':META,'engineSha256':ENGINE,'engineBytes':10002820,'recipeSha256':RECIPE,'policySha256':POLICY,'helperSha256':HELPER,'nativeSources':355,'externalEmbeddingSources':3,'toolDependencyRows':922,'frozenCopiesObserved':1390,'actualFrozenRegularFiles':1391,'originalEntriesVerified':1387,'nativeCompileCommands':62,'strictCompileCommands':4,'privateCompileCommands':6,'separateNoLtoEmbeddingCompileCommands':1,'changedNativePayloads':5,'unchangedParentNativePaths':350,'composedNativeEdits':20,'webCryptoEnabled':True,'cryptoInstallNamespaceCount':1,'changedCryptoCppCommands':3,'streamConsumersEnabled':True,'zlibEnabled':True,'entropyPolicy':'off','gcStress':False,'decoderNamespaceBeforeNodeObservedInCapturedInstall':True,'codecWitnessFiles':len(codec_files),'rawLinkCaptureBytes':len(raw_link),'rawLinkSelectedLineOneBased':link_number,'rawLinkResponseFiles':0,'rawLinkSameOutputProved':True,'selectedMozZSymbolDefinitions':7,'selectedArchiveSha256':ARCHIVE,'selectedArchiveBytes':538170426,'headers':selected['headers'],'opensslCompleteSourcesIndependentlyRehashed':len(actual_ssl),'selectedLibcryptoArchiveSymbols':crypto_archive_symbols,'cargoBuildLocked':True,'sourcePreparationInputs':1323,'sourceAdmissionRecordAuthenticatedNotRerun':True,'universalHelperAuthenticationBeforeCustomImports':True,'rootOuterRawStatusesObservedByThisReader':False,'rootProcessRecords':terminals,'activeFreezerTooling':f['activeFreezerTooling'],'donorFreezerTooling':f['donorFreezerTooling'],'freezerSourceCorrection':f['freezerSourceCorrection'],'runtimeBackendProof':f['runtimeBackendProof'],'runtimeBootstrapPinsNull':True,'ownerImportsHelpersTestsNativeVerifiersNinjaNmCompilerEnginesKeysCryptoGcGuestsHostsOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'operationalAdmission':False,'performanceClaim':False,'sourcePromotionAllowed':False,'concreteBlockers':[],'limitations':['Completed native build/freeze/source/command provenance only; no key or crypto behavior, finalizer, complete zeroization, component/guest/host or runtime acceptance proof.','Root outer raw0 events are authenticated retained records, not directly observed terminals.','Selected SM archive is a current rehashed external reference, not duplicated in frozen copies.','GNU libcrypto archive index plus actual raw link records establishes static symbol/link provenance; it is not function execution or a private runtime proof.','Compiler/post-optimizer argv is independently reconstructed; spawned LLD child argv/thread count is not independently observed.','BIGNUM/private-copy/allocation-bound followons remain open.','No old355/350/classic runtime or Node parity proof is transferred.'],'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
''')
replace("for row in list(seen.values()):read(Path(row['path']),row['sha256'],row['bytes'],capture=False)", '''# Additional current-SDK and original-stage binding; ordinary data reads only.
assert m['auditedBaseRevision']==m['starlingMonkeyRevision']=='54b3329b3ce818fd1f244e871e9c259b63667cda'and m['componentizeJsRevision']=='4d812f5a7b524cea5bcfd565cac55f3fab876a57'
assert m['archivePins']=={'componentizeJsSha256':'8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10','spiderMonkeySha256':'c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b'}
read(WORK/'spidermonkey-release.tar.gz',m['archivePins']['spiderMonkeySha256'],capture=False)
wrapper=read(build/'cxx-wrapper').decode()
sdk=WORK/'cache/wasi-sdk/85e6'
assert 'PATH="'+str(SOURCE/'scripts')+':$PATH" '+str(sdk/'bin/clang++')+' "$@"'in wrapper
assert 'CMAKE_CXX_COMPILER'not in cache and cache['WASI_SDK_VERSION']=='30'
assert Path(cache['CMAKE_CXX_COMPILER_AR']).resolve()==(sdk/'bin/llvm-ar').resolve()
assert all(shlex.split(command)[0]==str(build/'cxx-wrapper')for command in mapped.values())
assert [shlex.split(command)[0]for command in embedding]==[str(sdk/'bin/clang++')]
sdk_archive=next(row for row in m['downloadedArchives']if Path(row['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz')
sdk_members={}
with tarfile.open(sdk_archive['path'])as archive:
 for name in['VERSION','bin/clang++','bin/clang','bin/clang-21','bin/llvm-nm']:
  member=archive.getmember('wasi-sdk-30.0-arm64-macos/'+name)
  target=sdk/name
  if member.issym():assert target.is_symlink()and os.readlink(target)==member.linkname;sdk_members[name]={'symlinkTarget':member.linkname}
  else:
   assert member.isfile();raw=archive.extractfile(member).read();actual=read(target.resolve(),sha(raw),len(raw));sdk_members[name]={'sha256':sha(actual),'bytes':len(actual)}
assert sdk_members['bin/llvm-nm']['sha256']==nm['nm']['sha256']and sdk_members['bin/clang++']=={'symlinkTarget':'clang'}and sdk_members['bin/clang']=={'symlinkTarget':'clang-21'}
binaryen_archive=next(row for row in m['downloadedArchives']if Path(row['path']).name=='binaryen-version_123-arm64-macos.tar.gz')
with tarfile.open(binaryen_archive['path'])as archive:
 member=next(row for row in archive.getmembers()if row.name.endswith('/bin/wasm-opt'));assert member.isfile();tool=archive.extractfile(member).read()
 optimizer_tool=read(Path(optimizer[0]),sha(tool),len(tool),capture=False)
stage_record=doc(Path(buildroot['sourceStageResult']['path']),buildroot['sourceStageResult']['sha256'])
assert len(stage_record['files'])==1311
for row in stage_record['files']:
 path=SOURCE/row['path'];original=Path(row['original']);assert stat.S_IMODE(path.stat().st_mode)==stat.S_IMODE(original.stat().st_mode)==row['sourceMode']==row['outputMode']
 assert(path.stat().st_dev,path.stat().st_ino)!=(original.stat().st_dev,original.stat().st_ino)
 read(path,row['sha256'],row['bytes'],SOURCE,capture=False)
assert verify_source.index('indexed(v[\\'amendmentSource\\'])')<verify_source.index('spec.loader.exec_module(common)')<verify_source.index("common.verify_frozen_variant('normal-off',return_receipt_digest=True)")
assert verify_source.index("for row in pins['toolDependencies']:")<verify_source.index('spec.loader.exec_module(common)')
extra={'selectedSdkVersion':m['wasiSdkVersionFiles'],'selectedSdkWrapper':seen[str(build/'cxx-wrapper')],'selectedSdkArchiveTools':sdk_members,'actualPostOptimizerTool':optimizer_tool,'staged1311SourceBytesModesAndDistinctInodesRechecked':True,'metadataOriginalEnginePathSpelling':m['enginePath'],'freezeOriginalEnginePathSpelling':f['originalEngine'],'enginePhysicalPathsEqual':Path(m['enginePath']).resolve()==Path(f['originalEngine']).resolve(),'rootGenuineVerifierControlFlowInspectedBeforeImportAndCall':True}
for row in list(seen.values()):read(Path(row['path']),row['sha256'],row['bytes'],capture=False)''')
replace("with(HERE/'results.json').open('x')", "result.update(extra)\nresult.update(variant='normal-off',label='normal-off',artifactReviewPassed=True,sourceFiles=355,engine=root['engine'],metadata=root['metadata'],freezeReceipt=root['freezeReceipt'],configuredSourceRoot=str(SOURCE),frozenSourceRoot=str(FROZEN/'source'),ownerActionsInvoked=False)\nwith(HERE/'results.json').open('x')")
span("print(json.dumps({k:result[k]", "\n", "print(json.dumps({k:result[k]for k in['state','frozenCopiesObserved','originalEntriesVerified','nativeCompileCommands','opensslCompleteSourcesIndependentlyRehashed']}))")
(P/'reader.py').write_text(text)
(P/'reader-derivation.json').write_text(json.dumps(dict(schemaVersion=1,donorReader=str(BASE),donorReaderSha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),sourceDataOnly=True,ownerOrDonorCodeImportedOrExecuted=False,changes=changes,artifactConstantsAndCountsReboundToActualNewCryptoOnly=True),indent=2)+'\n')
print(json.dumps(dict(ownedReaderBytes=len(text.encode()),mechanicalChanges=len(changes))))
