"""Derive an owned data reader from the prior sealed independent reader."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
base=HERE.parent/'independent-native-consumers-v2-disabled-off-review-v1/verify.py'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='88c9dc6d3c7e15a4d5257710b9e09b8e0c0cb38d0a3afb0d99a9c6f9fbbf0260'
value=base.read_text()
changes=[]
def edit(old,new,count=None):
 global value
 actual=value.count(old)
 assert actual and(count is None or actual==count),(old,actual,count)
 value=value.replace(old,new);changes.append({'before':old,'after':new,'occurrences':actual})
edit('disabled-off','normal-runtime')
edit('81ffa152cf1bbdc7dbd59d7390478964be1a0ae213f636710692c2a08c3e5110','b227a8d2e6fb6b83da556d3520dceec82d5e1978801ba3c607bc9a31aa28ad60')
edit('8e05a70593c09fd41eadcd56b6de47da9892a2acbf78e174f97b78b0991f76ac','9668b23dbac34f3e835b59f339f9a40504153eb03cdd149f0a761cb99ed77b49')
edit('9353df3cb9db5aa0db6b47e627ee689023405e35334f5189d2b07b1eb6a34b44','0866e4b8d76a4c89225b07124874587c29b0ecce8de7c6992eaa5f164a8615b8')
edit('9d6fd22252de089370ba104d39e15431283e8ed62a26514c66ff2af181e4a4e1','3180f5b8a81d77cc2dab80cdeb31d6f0922c9fefb4b1ac8ee43c4ad1e70c5040')
edit('9995242','10009523')
edit("for name in['NODE_COMPAT_ENTROPY_RUNTIME_ONLY','NODE_COMPAT_OOM_TESTING']:macro(words,name,False)","macro(words,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',True);macro(words,'NODE_COMPAT_OOM_TESTING',False)")
edit("macro(words,'NODE_COMPAT_STREAM_CONSUMERS',False)","macro(words,'NODE_COMPAT_STREAM_CONSUMERS',private)")
edit("assert root['rootObservedSessions']=={'build':99558,'freeze':3263,'readOnlyVerify':24291}","assert root['rootObservedSessions']=={'build':7122,'freezeAndReadOnlyVerify':80421}")
edit("references=root['references'];assert len(references)==11", "references=root['references'];assert len(references)==12")
edit("for name in ['build','freeze','verify']:\n terminal=doc(WORK.parent/('consumers355-v2-normal-runtime-'+name+'-v1.terminal.json'));assert terminal['rawExitCode']==0", "LOGS=WORK.parent/'consumers355-v2-normal-runtime-build-root'\nfor name,pid in [('terminal.json',80946),('freeze.terminal.json',2217),('verify.terminal.json',2236)]:\n terminal=doc(LOGS/name);assert terminal['rawExitCode']==0 and terminal['pid']==pid and terminal['observedByRoot']is True\n for key in ['stdout','stderr']:read(Path(terminal[key]['path']),terminal[key]['sha256'],terminal[key]['bytes'],capture=False)\n assert read(Path(terminal['stderr']['path']))==b''")
edit("'entropyPolicy':'off'", "'entropyPolicy':'runtime-only'")
edit("m['entropyPolicy']=='off'", "m['entropyPolicy']=='runtime-only'")
edit("len(m['selectedModuleManifests'])==10", "len(m['selectedModuleManifests'])==11")
edit("assert m['downloadedArchives']==[]  # Actual optional per-project tar inventory is empty; never relabel normal six as newOFF records.", "assert len(m['downloadedArchives'])==1\nfor row in m['downloadedArchives']:read(Path(row['path']),row['sha256'],capture=False)\nassert m['downloadedArchives'][0]['sha256']==m['openssl']['completeSourceAudit']['archiveSha256']")
edit("audit_build_fields={'beforeReportPath','beforeReportSha256','buildDirectory','receiptSha256'}", "audit_build_fields={'beforeReportPath','beforeReportSha256','buildDirectory','sourceDirectory','receiptSha256'}")
edit("assert ssl['sourceDir']==normal_metadata['openssl']['sourceDir']", "assert ssl['sourceDir']!=normal_metadata['openssl']['sourceDir'] and ssl['sourceKey']!=normal_metadata['openssl']['sourceKey']\nassert ssl['entropy']=='RUNTIME_ONLY' and ssl['randSeed']=='none' and ssl['profile']=='ON'")
edit("assert m['streamConsumersEnabled']is f['streamConsumersEnabled']is False", "assert m['streamConsumersEnabled']is f['streamConsumersEnabled']is True")
edit("assert consumer['enabled']is False", "assert consumer['enabled']is True")
edit("cache['NODE_COMPAT_STREAM_CONSUMERS']=='OFF'", "cache['NODE_COMPAT_STREAM_CONSUMERS']=='ON'")
edit("admission['options']['streamConsumersEnabled']is False", "admission['options']['streamConsumersEnabled']is True")
edit("root['consumerEnabled']is False", "root['consumerEnabled']is True")
edit("consumer['moduleManifest']not in admission['selectedManifestPaths']", "consumer['moduleManifest']in admission['selectedManifestPaths']")
edit("len(admission['selectedManifestPaths'])==10", "len(admission['selectedManifestPaths'])==11")
edit("ssl_build_fields={'installDir','completeSourceAudit','receiptPath','receiptSha256','configureRecipe','configdata','library'}", "ssl_build_fields={'entropy','sourceKey','sourceDir','installDir','completeSourceAudit','receiptPath','receiptSha256','configureRecipe','configdata','library'}")
edit("configure_raw.replace(str(build),str(Path(normal_metadata['cmakeCachePath']).parent))", "configure_raw.replace(str(build),str(Path(normal_metadata['cmakeCachePath']).parent)).replace(ssl['sourceKey'],normal_metadata['openssl']['sourceKey'])")
edit("assert '.s0'in str(build)and '.s1'in normal_metadata['cmakeCachePath']", "assert '.RUNTIME_ONLY.'in str(build)and '.OFF.'in normal_metadata['cmakeCachePath']\nassert build!=Path(normal_metadata['cmakeCachePath']).parent")
edit("launch['explicitEnvironment']['NODE_COMPAT_STREAM_CONSUMERS']=='0'", "launch['explicitEnvironment']['NODE_COMPAT_STREAM_CONSUMERS']=='1'")
edit("assert not MUTABLE and not MUTABLE_READ_REQUESTS", "assert launch['explicitEnvironment']['NODE_COMPAT_ENTROPY_MODE']=='RUNTIME_ONLY'\nassert cache['NODE_COMPAT_ENTROPY_MODE']=='RUNTIME_ONLY'\nassert admission['options']['entropyPolicy']=='runtime-only'\nassert not MUTABLE and not MUTABLE_READ_REQUESTS")

# The RuntimeOnly OpenSSL source directory is distinct: audit all its4650 files.
source_audit="""
read(Path(audit['archivePath']),audit['archiveSha256'],capture=False)
expected_ssl={}
with tarfile.open(audit['archivePath'])as archive:
 for member in archive.getmembers():
  if not member.isfile():assert member.isdir();continue
  prefix,slash,name=member.name.partition('/');assert prefix=='openssl-3.0.17'and slash;relative(name)
  assert name not in expected_ssl
  expected_ssl[name]=audit['patchedSources'].get(name)or sha(archive.extractfile(member).read())
actual_ssl={}
for path in sorted(Path(ssl['sourceDir']).rglob('*')):
 assert not path.is_symlink()
 if path.is_file():actual_ssl[str(path.relative_to(ssl['sourceDir']))]=read(path,capture=False)['sha256']
assert actual_ssl==expected_ssl and len(actual_ssl)==4650
assert sha(json.dumps([{'path':name,'sha256':h}for name,h in sorted(actual_ssl.items())],separators=(',',':')).encode())==audit['sourceManifestSha256']
"""
edit("assert ssl['version']==normal_metadata['openssl']['version']", "assert ssl['version']==normal_metadata['openssl']['version']\n"+source_audit)

# Preserve the old three frozen sets and verify Root's fresh authority/closure.
before_final="""
disabled_peer=FAMILY/'independent-native-consumers-v2-disabled-off-review-v1'
indexed(disabled_peer,'6b5414f6fe74948a4d0591e21c3b69d66fe3230ad88b3a9deab1411783f35908',16)
disabled_freeze=doc(FROZEN/'disabled-off-freeze-receipt.json','9d6fd22252de089370ba104d39e15431283e8ed62a26514c66ff2af181e4a4e1')
for row in disabled_freeze['copies']:read(Path(row['path']),row['sha256'],row['bytes'],FROZEN,capture=False)
authority=doc(FAMILY/'native-integration-v2-normal-runtime-build-root-review.json','decfa0d15271459936e69e26e9cfbedd9f414b3822c91f6e665682c2fd41505c')
for key in ['nativeProducerIndex','sourceInspectionTemplate','producerSourceReview','actualSourceStageReview','oldReviewedPins','oldThreeFrozenPrebuildCheckpoint']:
 row=authority[key];read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
assert authority['argv']==doc(LOGS/'terminal.json')['argv']
assert authority['nativeCodeRecipeOrOldToolContextChangesAllowed']is False and authority['oldThreeFrozenChangesAllowed']is False
checkpoint=doc(Path(authority['oldThreeFrozenPrebuildCheckpoint']['path']),authority['oldThreeFrozenPrebuildCheckpoint']['sha256'])
assert checkpoint['frozenRows']==len(checkpoint['files'])==3492
assert checkpoint['normalTwoHistoricalMutableOriginalsNotRestored']is True
old_sets={'normal-off':normal_freeze,'gc-off':gc_freeze,'disabled-off':disabled_freeze}
expected_checkpoint=[]
for label,old in old_sets.items():
 for row in old['copies']:expected_checkpoint.append({'label':label,**{k:row[k]for k in ['path','sha256','bytes']}})
assert checkpoint['files']==expected_checkpoint
for row in checkpoint['files']:read(Path(row['path']),row['sha256'],row['bytes'],FROZEN,capture=False)
post=doc(Path(root['oldThreePostfreezeCheckpoint']['path']),root['oldThreePostfreezeCheckpoint']['sha256'])
assert post['rowsRehashed']==3492 and post['allMatched']is True and post['prebuildCheckpoint']==authority['oldThreeFrozenPrebuildCheckpoint']
original_closure=doc(Path(root['originalInputClosure']['path']),root['originalInputClosure']['sha256'])
assert original_closure['entries']==len(original_closure['files'])==1162
expected_originals=[{'path':row['original'],'sha256':row['sha256'],'bytes':row['bytes']}for row in f['copies']if row['original']is not None]
assert original_closure['files']==expected_originals
for row in original_closure['files']:read(Path(row['path']),row['sha256'],row['bytes'],capture=False)
assert doc(Path(authority['oldReviewedPins']['path']))['variants']['normal-runtime']is None
assert root['checkedInRuntimePinStillNull']is True and root['guestOrComponentExecuted']is False and root['operationalAdmission']is False
assert sha(read(HERE.parent/'release-host-plan-v1/runtime-only-build.template.json'))=='096ad77302cd8f0fcc0fd78a07e557af1dbad5b67d3b5a6e51f8f8dae8f680e1'
"""
edit("universal=read(STAGED/'artifact-tools/artifact_common.py').decode()",before_final+"\nuniversal=read(STAGED/'artifact-tools/artifact_common.py').decode()")
at=value.index("result={'schemaVersion':1,")
value=value[:at]+"""result={
 'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_V2_NORMAL_RUNTIME_NATIVE_FREEZE_PASSED_NO_GUEST',
 'sourceIndexSha256':INDEX,'rootReceiptSha256':ROOT_SHA,'freezeReceiptSha256':FREEZE_SHA,'metadataSha256':META,
 'engineSha256':ENGINE,'engineBytes':10009523,'recipeSha256':RECIPE,'policySha256':POLICY,'helperSha256':HELPER,
 'nativeSources':355,'externalEmbeddingSources':3,'toolDependencyRows':767,
 'frozenCopiesObserved':1164,'allRuntimeOriginalEntryReferencesRehashed':1162,'rootOriginalClosureExact':True,
 'oldThreeFrozenEntryReferencesRehashedUnchanged':3492,'normalMutableProjectOriginalsReopened':False,
 'configuredNativeCompileCommands':62,'strictCompileCommands':4,'privateCompileCommands':6,'separateNoLtoEmbeddingCompileCommands':1,
 'runtimeOnlyMacroOnEveryNativeAndEmbeddingCompile':True,'consumerDefineOnExactSixPrivateCppAbsentEmbedding':True,'streamConsumersEnabled':True,
 'zlibEnabled':True,'gcStress':False,'entropyPolicy':'runtime-only','selectedManifests':11,'consumerManifestSelected':True,
 'separateRuntimeOnlySourceAndCmakeProject':True,'decoderNamespaceBeforeNodeObservedInCapturedInstall':True,
 'actualBuildStepsObservedInRootLog':108,'codecWitnessFiles':len(codec_files),'rawLinkCaptureBytes':len(raw_link),
 'rawLinkSelectedLineOneBased':link_number,'rawLinkResponseFiles':0,'rawLinkSameOutputProved':True,
 'selectedMozZSymbolDefinitions':7,'selectedArchiveSha256':ARCHIVE,'selectedArchiveBytes':538170426,'headers':selected['headers'],
 'opensslCompleteSourcesIndependentlyRehashed':4650,'opensslSourceDirectoryDistinctFromOff':True,
 'opensslSourceManifestMatchesOff':True,'opensslSourceKey':ssl['sourceKey'],'opensslActualLibrary':ssl['library'],
 'opensslOwnRuntimeConfigSourceArchiveAndLibcryptoChecked':True,'cargoLockedAndCurrentRawCommandBound':True,
 'originalPreparationProofInheritedRows':3420,'originalPreparationBroadRehashRepeated':False,
 'sourceAdmissionRecordAuthenticatedNotRerun':True,'universalHelperAuthenticationBeforeCustomImports':True,
 'rootEvidenceReferences':12,'rootOuterRawStatusesObservedByThisReader':False,
 'operationalAdmissionOpen':False,'runtimeBackendProof':f['runtimeBackendProof'],
 'runtimeBootstrapPinsNull':True,'newActualReviewedPinIssuedByThisReader':False,
 'ownerImportsHelpersTestsNativeVerifiersNinjaNmCompilerGuestsHostsOrTimingExecuted':False,
 'runtimeAcceptanceClaim':False,'performanceClaim':False,'concreteBlockers':[],
 'limitations':['Actual Release normal-runtime native build/freeze only; no new component/guest/host result.',
  'RuntimeOnly native macro/config evidence is not an observed final component random-import or entropy behavior proof.',
  'All old3492 frozen rows remain exact; old normal two historical mutable cache/DB originals are not reopened or relabelled.',
  'The shared355/3420 preparation source proof is inherited by exact source/native review hashes; the new RuntimeOnly4650-file OpenSSL source tree is independently rehashed.',
  'No codec runtime version, GC/root isolation, reset/ALS/request reuse, TLS, full Node support, statistical or performance claim.',
  'Root outer statuses are authenticated records, not directly observed events; captured compiler driver is not a separate LLD argv/thread observation.',
  'Old3 authority and checked-in NULL documents remain unchanged; a new explicit Root overlay is still required.'],
 'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\\n')
print(json.dumps({k:result[k]for k in['state','frozenCopiesObserved','allRuntimeOriginalEntryReferencesRehashed','oldThreeFrozenEntryReferencesRehashedUnchanged','configuredNativeCompileCommands','selectedManifests','opensslCompleteSourcesIndependentlyRehashed']}))
"""
with(HERE/'verify.py').open('x')as stream:stream.write(value)
(HERE/'reader-derivation.json').write_text(json.dumps({'schemaVersion':1,'parentReader':str(base),'parentReaderSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'changes':changes,'newResultSummary':True,'ownerCodeImportedOrExecuted':False},indent=2)+'\n')
print(json.dumps({'reader':str(HERE/'verify.py'),'sha256':hashlib.sha256(value.encode()).hexdigest(),'derivationEdits':len(changes)}))
