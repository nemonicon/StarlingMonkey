"""Frozen-only current355 DATA verifier; no old original/helper or engine access."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,shlex,stat,sys
FREEZE=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
SOURCE_SHA='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65'
ENGINE='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b'
META='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'

def checked(row):
 assert type(row)is dict and set(row)=={'path','sha256','bytes'} and type(row['path'])is str and row['path'].startswith('/') and str(Path(row['path']))==row['path'] and '..' not in Path(row['path']).parts and '\\' not in row['path'] and '\0' not in row['path']
 assert type(row['bytes'])is int and row['bytes']>=0 and re.fullmatch('[a-f0-9]{64}',row['sha256'])
 p=Path(row['path']);assert p.is_relative_to(FREEZE)
 for q in (p,*p.parents):assert not q.is_symlink()
 a=p.stat();assert stat.S_ISREG(a.st_mode);h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns) and a.st_size==row['bytes'] and h.hexdigest()==row['sha256'];return p

def frozen_json(row):
 assert row['bytes']<=32*1024*1024;return json.loads(checked(row).read_bytes())

def verify_frozen(receipt_row,expected_source):
 assert __debug__ and sys.dont_write_bytecode and re.fullmatch('[a-f0-9]{64}',expected_source)
 assert receipt_row['path']==str(FREEZE/'normal-off-freeze-receipt.json');r=frozen_json(receipt_row)
 assert r['schemaVersion']==1 and r['state']=='COMBINED355_NORMAL_OFF_NATIVE_FREEZE_COMPLETE_UNREVIEWED_V1' and r['variant']=='normal-off'
 assert r['nativeSourceIndexSha256']==r['nativeSourceIndexed']['sha256']==SOURCE_SHA and r['freezerSourceIndexSha256']==r['freezerSourceIndexed']['sha256']==expected_source
 assert r['engine']['sha256']==ENGINE and r['metadata']['sha256']==META
 for k,n in dict(nativeInputsVerified=355,unchangedSecretParentFiles=348,nativeReplacements=7,externalEmbeddingInputsVerified=3,selectedManifestCount=11,rawMetadataFields=80,compileDatabaseRows=68,policyCppCommands=62,otherConfiguredSourceRows=5,generatedNullCppRows=1,embeddingRowsInCompileDatabase=0,separatePostBuildEmbeddingCommands=1,actualStrictCommands=4,actualPrivateClassicCommands=6).items():assert r[k]==n
 for k in ('rawMetadataBytesUnchanged','rawMetadataOriginalConfiguredPathsPreserved','allInputsValidatedBeforeHelperImports','allInputsValidatedBeforeCopies','allCopiesAndOriginalsRehashed','receiptRequiresExternalParentZeroAndIndependentReview','verifiedReferencesNotAllCopied','referenceAliasesNotCopiedAsLinks'):assert r[k] is True
 for k in ('gcReconfigureAllowed','engineExecuted','bootstrapExecuted','componentOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim','historicalPreinstallSettingsRawBytesSeparatelyRetained','zlibRemainingDeviationsApproved'):assert r[k] is False
 assert r['nativeAllInvalidRuntimeValidation'] is r['resourceNativeRuntimeValidation'] is r['reviewedEnginePins'] is None
 assert r['runtimeBackendProof']==dict(verified=False,version=None,vernum=None)
 before=FREEZE.lstat();assert stat.S_ISDIR(before.st_mode) and stat.S_IMODE(before.st_mode)==0o700 and not FREEZE.is_symlink()
 copies={};inodes=set()
 for item in r['copies']:
  path=Path(item['path']);name=path.relative_to(FREEZE).as_posix();assert name and all(p not in ('','.','..') for p in name.split('/')) and name not in copies
  checked({k:item[k] for k in ('path','sha256','bytes')});s=path.lstat();identity=(s.st_dev,s.st_ino)
  assert identity not in inodes and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600;inodes.add(identity);copies[name]=item
 actual=set()
 for path in FREEZE.rglob('*'):
  s=path.lstat();assert not path.is_symlink()
  if stat.S_ISDIR(s.st_mode):assert stat.S_IMODE(s.st_mode)==0o700
  else:assert stat.S_ISREG(s.st_mode);actual.add(path.relative_to(FREEZE).as_posix())
 receipt_stat=Path(receipt_row['path']).stat();assert actual==set(copies)|{'normal-off-freeze-receipt.json'} and stat.S_IMODE(receipt_stat.st_mode)==0o600 and receipt_stat.st_nlink==1 and (receipt_stat.st_dev,receipt_stat.st_ino) not in inodes
 def row(name):return {k:copies[name][k] for k in ('path','sha256','bytes')}
 # Authenticate complete saved own source before importing only its two pure models.
 frozen_index=FREEZE/'artifact-tools/source/index.json';assert hashlib.sha256(frozen_index.read_bytes()).hexdigest()==expected_source
 index=json.loads(frozen_index.read_bytes());names=set()
 for item in index['files']:
  name=item['path'];assert name and not name.startswith('/') and all(p not in ('','.','..') for p in name.split('/')) and name not in names;names.add(name)
  saved=copies['artifact-tools/source/'+name];assert saved['sha256']==item['sha256'] and saved['bytes']==item['bytes']
 verifier=next(x for x in index['files'] if x['path']=='verify.py');self_path=Path(__file__).resolve();assert hashlib.sha256(self_path.read_bytes()).hexdigest()==verifier['sha256'] and self_path.stat().st_size==verifier['bytes']
 def pure_model(name):
  location=checked(row('artifact-tools/source/'+name));spec=importlib.util.spec_from_file_location('frozen_combined355_pure_'+name.replace('.','_'),location);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
 refs=frozen_json(row('artifact-tools/source/references.json'));plan=frozen_json(row('artifact-tools/source/capture-plan.json'))
 for item in plan['copies']:
  c=copies[item['destination']];assert c['original']==item['source'] and c['role']==item['role'] and c['sha256']==item['source']['sha256'] and c['bytes']==item['source']['bytes']
 assert r['staticLibrariesPhysicallyCopied']==plan['staticLibraries']==len([c for c in copies.values() if c['role']=='selected-static-library'])
 assert r['verifiedOriginalReferenceCount']==refs['verifiedBuildReferenceCount'] and r['verifiedBuildInputLedger']==refs['buildInputLedger']
 assert r['verifiedReferenceAliases']==refs['referenceAliases'] and r['declaredArchiveHardlinks']==refs['declaredArchiveHardlinks']
 assert r['retryBuildControllerIndexed']==refs['buildControllerIndex'] and r['actualBuildReview']==refs['actualBuildReview']
 build=frozen_json(row('build-proof/results.json'));build_contract=frozen_json(row('build-proof/result-contract.json'))
 for key,value in build_contract['requiredFixedValues'].items():assert build[key]==value,key
 for key,value in build_contract['requiredExactDescriptors'].items():assert build[key]==value,key
 assert build['coverage']==build_contract['requiredCoverage'] and build['inputHashes']==refs['buildInputLedger'] and build['referenceAliases']==refs['referenceAliasWitness']
 assert len(frozen_json(row('build-proof/input-hashes.json'))['files'])==refs['verifiedBuildReferenceCount']
 assert frozen_json(row('build-proof/reference-aliases.json'))['symlinks']==refs['referenceAliases']
 assert r['configuredSourceRoot']==refs['configuredSourceRoot'] and r['workRoot']==refs['workRoot'] and r['sourceRoot']==str(FREEZE/'source') and r['componentizeSourceRoot']==str(FREEZE/'componentize-source')
 assert r['engine']['path']==str(FREEZE/'normal-off.engine.wasm') and r['metadata']['path']==str(FREEZE/'normal-off.engine.wasm.build.json')
 metadata=frozen_json(r['metadata']);checked(r['engine']);policy=frozen_json(row('build-evidence/combined355-policy.json'))
 models=pure_model('models.py');models.metadata(metadata,policy,refs)
 classifier=pure_model('metadata_model.py').validate_metadata(metadata,policy,refs['policy']['sha256'],refs['layer']['sha256'],refs['recipe']['sha256'],refs['externalSourceManifest'],'normal-off')
 assert classifier==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False)
 database=frozen_json(row('build-evidence/compile_commands.json'));models.compilation(database,metadata,policy,refs)
 assert r['sourcePolicies']=={k:metadata[k] for k in refs['copiedMetadataPolicyKeys']} and r['privateRustupBootstrapPolicy']==metadata['privateRustupBootstrapPolicy']
 for key,prefix in (('sourceManifest','source'),('componentizeSourceManifest','componentize-source')):
  for source in metadata[key]:assert copies[prefix+'/'+source['path']]['sha256']==source['sha256']
 selected=[]
 for source in metadata['selectedModuleManifests']:
  value=frozen_json(row('source/'+source['path']));assert value['profileVersion']==source['profileVersion'];selected.append(value)
 assert selected==refs['selectedManifestValues']
 assert frozen_json(row('build-evidence/private-rustup-settings-before-install.json'))==refs['rustupBeforeValue']
 assert checked(row('build-evidence/private-rustup-settings-at-build-completion.toml')).read_bytes()==refs['rustupCurrentSettingsText'].encode('utf8')
 assert copies['build-evidence/private-rustup-settings-before-install.json']['original']==refs['rustupBeforeRecord'] and copies['build-evidence/private-rustup-settings-at-build-completion.toml']['original']==refs['rustupCurrentSettings']
 # The prior 57-byte nested descriptor stays historical; it is never opened.
 for role,e in (('source-admission',r['sourceAdmissionEvidence']),('embedding-after',r['postBuildEmbeddingEvidence'])):
  for key,name in (('stdout','stdout.log'),('stderr','stderr.log'),('terminal','terminal.json')):assert row('helper-calls/'+role+'/'+name)==e[key]
  t=frozen_json(e['terminal']);assert t['rawExitCode']==0 and t['timedOut'] is False and t['errorType'] is None and t['capturedStreamsComplete'] is True and t['compilerExecuted'] is False and t['engineExecuted'] is False and t['role']==role and t['stdout']==e['stdout'] and t['stderr']==e['stderr'] and t['cwd']==refs['configuredSourceRoot']
 admission=frozen_json(r['sourceAdmissionEvidence']['stdout']);models.admission(admission,metadata,refs,expected_source)
 config=copies['provenance/freeze-config.json']['original']
 assert frozen_json(r['sourceAdmissionEvidence']['terminal'])['argv']==[refs['python']['path'],'-B','-I',str(Path(r['freezerSourceIndexed']['path']).parent/'entry.py'),'admit',json.dumps(config,separators=(',',':'))]
 e=r['postBuildEmbeddingEvidence'];assert e['beforeBuildCaptureExists'] is e['perCompilerRawTerminalsClaimed'] is False and e['commands']==metadata['actualEmbeddingCompileCommands'] and len(e['commands'])==1
 commands=[]
 for line in checked(e['stdout']).read_text().splitlines():
  if ' -c ' in line:
   words=shlex.split(line)
   if words.count('-c')==1 and words[words.index('-c')+1]==e['sourcePath']:commands.append(line)
 assert commands==e['commands'] and e['sourcePath']==refs['externalSourceRoot']+'/embedding/embedding.cpp'
 assert frozen_json(e['terminal'])['argv']==[refs['ninja']['path'],'-C',str(Path(metadata['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding']
 control=frozen_json(r['freezerControl'])
 for key in ('nativeSourceIndexed','retryBuildControllerIndexed','freezerSourceIndexed','rootAuthority','sourceIndependentReview','actualBuildReview'):assert control[key]==r[key]
 assert control['privateRustupBeforeRecord']==refs['rustupBeforeRecord'] and control['privateRustupCurrentSettings']==refs['rustupCurrentSettings'] and control['engineExecuted'] is False
 after=FREEZE.lstat();assert (before.st_dev,before.st_ino)==(after.st_dev,after.st_ino);checked(receipt_row)
 return dict(schemaVersion=1,state='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1',receipt=receipt_row,engine=r['engine'],metadata=r['metadata'],copies=len(copies),nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifests=11,rawMetadataFields=80,originalBuildReferencesNotReexecuted=True,requiresExternalParentZeroAndIndependentReview=True,engineExecuted=False,bootstrapExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
if __name__=='__main__':
 assert len(sys.argv)==3
 print(json.dumps(verify_frozen(json.loads(sys.argv[2]),sys.argv[1])),flush=True)
