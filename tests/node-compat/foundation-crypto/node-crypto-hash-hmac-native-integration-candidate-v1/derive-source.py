"""Source derivation only. Never stage/build/import a native helper."""
import copy, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OWN=Path(__file__).resolve().parent
DONOR=ROOT/'tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v2'
AFDB=ROOT/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-candidate-v1'
SREL='tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-integration-candidate-v1'
FRESH='/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1'
assert not (OWN/'index.json').exists(), 'Sealed family is immutable'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def desc(p):
 p=Path(p).absolute(); return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(n,v): (OWN/n).write_text(json.dumps(v,indent=2)+'\n')
changes=[]
def edit(text,old,new,role):
 positions=[m.start()for m in re.finditer(re.escape(old),text)];count=len(positions)
 assert count>0,(role,old[:90])
 changes.append(dict(role=role,before=old,after=new,count=count,afterPositions=[v+i*(len(new)-len(old))for i,v in enumerate(positions)]))
 return text.replace(old,new)
p=copy.deepcopy(json.loads((DONOR/'policy.json').read_bytes()))
parent=copy.deepcopy(p); current={r['path']:r['sha256'] for r in parent['expectedNativeSourceManifest']}
after=dict(current)
images=['cmake/builtins.cmake','builtins/node-compat/register.cpp','builtins/node-compat/hash-hmac-kernel.cpp','builtins/node-compat/crypto-factory.generated.h']
for r in images: after[r]=sha(OWN/'native'/r)
assert len(current)==355 and len(after)==357
assert sum(current[k]==after[k] for k in current)==353
p['expectedNativeSourceManifest']=[dict(path=k,sha256=after[k])for k in sorted(after)]
p['contexts']=dict(configuredSourceRoot=FRESH+'-source',workRoot=FRESH+'-build',freezeRoot=FRESH+'-freeze')
p['version']='sm-node-sha256-hash-hmac357-source-policy-v1'
p['classicPolicyVersion']='sm-node-sha256-hash-hmac357-classic-install-v1'
p['profileVersion']='sm-node-22.14.0-m0.15'
p['strictPolicyVersion']='sm-uncaught-event-v3-hash-hmac357-v1'
p['protectedPolicyVersion']='sm-protected-abort-listener-hash-hmac357-v1'
for r in images[:2]:
 assert p['sourceLayer'][r]['afterSha256']==current[r]
 p['sourceLayer'][r]['afterSha256']=after[r]
p['addedSourcePaths']+=images[2:]
p['privateTargetCpp']+=['builtins/node-compat/hash-hmac-kernel.cpp']
p['newModuleIds']+=['node:crypto']
p['requiredWhenHashHmacEnabled']={'ENABLE_BUILTIN_NODE_COMPAT':'ON','ENABLE_BUILTIN_WEB_CRYPTO':'ON','NODE_COMPAT_ENTROPY_MODE':'OFF','NODE_CRYPTO_AUDITED_BORROW':'OFF'}
p['parentCombinedSourcePolicy']=copy.deepcopy(parent['combinedSourcePolicy'])
p['combinedSourcePolicy']=dict(version='sm-node-sha256-hash-hmac357-source-layer-v1',parentSourceIndex=desc(ROOT/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/index.json'),parentSuccessfulProducerPolicy=desc(DONOR/'policy.json'),parentExpectedNativeSourceManifest=parent['expectedNativeSourceManifest'],sourceFiles=357,unchangedParentFiles=353,changedSourceFiles=2,addedSourceFiles=2,changes=[dict(path=r,beforeSha256=current.get(r),afterSha256=after[r])for r in images],preservedCombined355Layer=parent['combinedSourcePolicy']['changes'],fullAbiRebuildRequired=True,publicExportNamesChanged=True,privateBackendEvidenceHookEnabled=False,runtimeValidation=None,operationalAdmission=False)
inventory=json.loads((AFDB/'node-export-manifest.json').read_bytes())
manifest_rel=SREL+'/crypto-module-manifest.json'
manifest_value=json.loads((OWN/'crypto-module-manifest.json').read_bytes())
p['selectedModuleManifests'].append(dict(path=manifest_rel,sha256=sha(OWN/'crypto-module-manifest.json'),profileVersion=manifest_value['profileVersion']))
p['selectedManifestValues'].append(manifest_value)
p['hashHmacSourcePolicy']=dict(version='sm-node-public-sha256-hash-hmac-source-v1',sourceIndex=desc(AFDB/'index.json'),sourceReviewIndex=desc(ROOT/'tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-source-review-v1/index.json'),sourceReviewResult=desc(ROOT/'tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-source-review-v1/results.json'),sdkSyntaxIndex=desc(ROOT/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-sdk-syntax-v1/index.json'),sdkSyntaxResult=desc(ROOT/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-sdk-syntax-v1/results.json'),kernelSha256=after[images[2]],factorySha256=after[images[3]],registrationSha256=after[images[1]],cmakeSha256=after[images[0]],packagingManifestInput=dict(path=manifest_rel,sha256=sha(OWN/'crypto-module-manifest.json'),bytes=(OWN/'crypto-module-manifest.json').stat().st_size),packagingManifestRole='tool-data-not-a-native-source-row',esmNamedIncludingDefault=inventory['esmNamedIncludingDefault'],defaultCMakeFlags={'NODE_COMPAT_CRYPTO_HASH_HMAC':'OFF','NODE_CRYPTO_AUDITED_BORROW':'OFF'},initialExperimentalFlags={'NODE_COMPAT_CRYPTO_HASH_HMAC':'ON','NODE_CRYPTO_AUDITED_BORROW':'OFF'},initialCopyOnly=True,borrowNativeBuildAuthorized=False,limits=manifest_value['modules']['node:crypto']['limits'],constantScope='Finite pinned guest-header numeric subset; not backend runtime availability',nativeWebCryptoAliasIdentityValidated=False,linkedValidation=None,runtimeValidation=None,operationalAdmission=False)
p['expectedCompilation']=dict(nativeSourceFiles=357,retainedParentFiles=353,changedParentFiles=2,newSourceFiles=2,policyCpp=63,compileDatabaseRows=69,otherConfiguredRows=5,generatedNullRows=1,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,selectedNativeManifests=11,selectedPackagingManifests=1,totalSelectedManifests=12)
# Pure admission model is genuinely current357; no old classifier receives a reshaped frame.
m=(DONOR/'native-admission-model.py').read_text()
for old,new in [
 ('Pure full355 metadata-shape gate','Pure new357 metadata-shape gate'),
 ("== 355","== 357"),("== 11","== 12"),("== 6\n","== 7\n"),("== 68","== 69"),("== 62","== 63"),
 ("'ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'","'ACTUAL_FRESH_HASH_HMAC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'"),
 ("'FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1'","'FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1'"),
 ("'nativeFiles':355","'nativeFiles':357")]: m=edit(m,old,new,'metadata-model')
m=edit(m,"    assert metadata['entropyPolicy'] == 'off'","    assert metadata['entropyPolicy'] == 'off'\n    assert metadata['nodeCryptoHashHmacEnabled'] is True\n    assert metadata['nodeCryptoAuditedBorrowEnabled'] is False\n    assert len(metadata) == policy['expectedRawMetadataFields']\n    assert sorted(metadata) == policy['expectedRawMetadataKeys']",'metadata-model')
m=edit(m,"'CMAKE_C_COMPILER_LAUNCHER':'','CMAKE_CXX_COMPILER_LAUNCHER':''}","'CMAKE_C_COMPILER_LAUNCHER':'','CMAKE_CXX_COMPILER_LAUNCHER':'',\n              'NODE_COMPAT_CRYPTO_HASH_HMAC':'ON','NODE_CRYPTO_AUDITED_BORROW':'OFF'}",'metadata-model')
m=edit(m,"    return {'state':",'''    hash_policy=metadata['nodeCryptoHashHmacPolicy']
    assert hash_policy['sourcePolicy'] == policy['hashHmacSourcePolicy']
    assert hash_policy['enabled'] is True and hash_policy['auditedBorrowEnabled'] is False
    assert len(hash_policy['actualPrivateHashHmacMacroCompileCommands']) == 7
    assert len(hash_policy['actualRegistrationCompileCommands']) == len(hash_policy['actualKernelCompileCommands']) == 1
    assert hash_policy['actualInstallationOrder']['cryptoBeforeNode'] is True
    assert hash_policy['actualNinjaCapture']['rawExitCode'] == 0
    assert hash_policy['actualNinjaCapture']['timeout'] is False
    assert hash_policy['moduleManifest'] == policy['hashHmacSourcePolicy']['packagingManifestInput']
    assert hash_policy['actualNativeAliasIdentityValidated'] is False
    assert hash_policy['runtimeValidation'] is None and hash_policy['operationalAdmission'] is False
    assert hash_policy['borrowRuntimeAuthorized'] is False and hash_policy['algorithmOutputVerified'] is False
    assert metadata['privateRustupBootstrapPolicy']['persistentSetting'] == 'disable'
    return {'state':''','metadata-model')
(OWN/'native-admission-model.py').write_text(m)
p['admissionModelSha256']=sha(OWN/'native-admission-model.py')
p['hashHmacModelSha256']=sha(OWN/'hash-hmac-model.py')
schema_parent=json.loads((ROOT/'tests/node-compat/foundation-scheduler/independent-combined355-native-build-v2-results-review-v1/results.json').read_bytes())
raw_parent=json.loads(Path(schema_parent['metadata']['path']).read_bytes())
p['parentRawSchemaEvidence']=desc(Path(schema_parent['metadata']['path']))
p['expectedRawMetadataKeys']=sorted(set(raw_parent)|{'nodeCryptoHashHmacEnabled','nodeCryptoAuditedBorrowEnabled','nodeCryptoHashHmacPolicy'})
p['expectedRawMetadataFields']=len(p['expectedRawMetadataKeys'])
assert len(raw_parent)==80 and p['expectedRawMetadataFields']==83
write('policy.json',p)
# Typed real future-stage dependency list. One additional parent policy is DATA only.
auth=json.loads((ROOT/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/donor-inputs.json').read_bytes())
parent_relative=str((DONOR/'policy.json').relative_to(ROOT))
assert parent_relative not in {r['path']for r in auth['files']}
auth['files'].append(dict(path=parent_relative,sha256=sha(DONOR/'policy.json'),bytes=(DONOR/'policy.json').stat().st_size))
auth['files'].sort(key=lambda r:r['path'])
write('donor-inputs.json',auth)
h=(DONOR/'layer-policy.py').read_text()
start=h.index('BASE_ROOT='); stop=h.index('\ndef expected(')
old_prefix=h[start:stop]
new_prefix='''BASE_ROOT=REPO/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1'
BASE=json.loads((BASE_ROOT/'policy.json').read_bytes())
ANCESTOR_ROOT=REPO/'tests/node-compat/foundation-scheduler/integration-candidate-v1'
ANCESTOR=json.loads((ANCESTOR_ROOT/'policy.json').read_bytes())
PARENT_ROOT=REPO/'tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v2'
PARENT=json.loads((PARENT_ROOT/'policy.json').read_bytes())
assert PARENT['expectedNativeSourceManifest']==POLICY['combinedSourcePolicy']['parentExpectedNativeSourceManifest']
assert PARENT['combinedSourcePolicy']==POLICY['parentCombinedSourcePolicy']
assert BASE['expectedNativeSourceManifest']==PARENT['combinedSourcePolicy']['parentExpectedNativeSourceManifest']
before={r['path']:r['sha256']for r in PARENT['expectedNativeSourceManifest']}
after={r['path']:r['sha256']for r in POLICY['expectedNativeSourceManifest']}
assert len(before)==355 and len(after)==357 and before.keys() <= after.keys()
changes=POLICY['combinedSourcePolicy']['changes']
assert len(changes)==4 and sum(before[p]==after[p]for p in before)==353
assert sum(r['beforeSha256']is None for r in changes)==2
for r in changes:assert before.get(r['path'])==r['beforeSha256']and after[r['path']]==r['afterSha256']
for key in ('cryptoKeyOwnershipSourcePolicy','cryptoSecretFailureSourcePolicy','streamConsumersSourcePolicy','zlibSourcePolicy'):
    assert POLICY[key]==PARENT[key]==BASE[key], 'Historical ancestry preserved; current source checked separately'
for key in ('resourceOwnershipSourcePolicy','taskSelectionSourcePolicy','zlibErrorSemanticsSourcePolicy'):
    assert POLICY[key]==PARENT[key]
assert POLICY['parentExpectedNativeSourceManifest']==ANCESTOR['expectedNativeSourceManifest']
model_path=HERE/'hash-hmac-model.py'
assert digest(model_path)==POLICY['hashHmacModelSha256']
model_spec=importlib.util.spec_from_file_location('new357_hash_hmac_source_primitives',model_path)
HASH_MODEL=importlib.util.module_from_spec(model_spec);model_spec.loader.exec_module(HASH_MODEL)
'''
h=edit(h,old_prefix,new_prefix,'helper')
for old,new in [
 ('Full current355 source/compile producer','New357 source/compile producer'),
 ("Path('/private/tmp/starling-node-compat/combined-native355-v1-source')",f"Path('{FRESH}-source')"),
 ("REPO/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/donor-inputs.json'","HERE/'donor-inputs.json'"),
 ("POLICY_SHA256='fc9c5e97594507513ed20efeced61dbf2be1a92ff038e7f1df1bcddd0b56a681'",f"POLICY_SHA256='{sha(OWN/'policy.json')}'"),
 ("AUTH_SHA256='c837e8eb61329370775e0a24b0c914a6efe6bfcb3e51a03a8ed2ecd41fa807db'",f"AUTH_SHA256='{sha(OWN/'donor-inputs.json')}'"),
 ("assert len(rows)==len({r['path']for r in rows})==355","assert len(rows)==len({r['path']for r in rows})==357"),("len(cpp)==62","len(cpp)==63"),
 ("(5 if web else 4)+int(metadata['zlibEnabled'])","(5 if web else 4)+int(metadata['zlibEnabled'])+int(metadata['nodeCryptoHashHmacEnabled'])"),
 ("def decorate(metadata,repo,source_dir,entries,embedding_commands,enabled):","def decorate(metadata,repo,source_dir,entries,embedding_commands,enabled,ninja_capture,ninja_text):"),
 ("normal-OFF combined355 producer","normal-OFF Hash/Hmac357 producer"),
 ("==68","==69"),("len(native)==62","len(native)==63"),("len(private)==6","len(private)==7"),
 ("'actualCompileDatabaseRows':68","'actualCompileDatabaseRows':69"),
 ("'ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'","'ACTUAL_FRESH_HASH_HMAC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'"),
 ("Actual355 source/command observations; parent342/306 are immutable ancestry, never projected metadata.","Actual new357 source/command observations; parent355/342/306 are immutable ancestry, never projected metadata."),
 ("Exact combined355 initial normal-OFF source policy verified","Exact new357 Hash/Hmac initial normal-OFF source policy verified")]: h=edit(h,old,new,'helper')
h=edit(h,"    authenticate_inputs()\n    return metadata",'''    metadata['nodeCryptoHashHmacPolicy']=HASH_MODEL.observe_hash_hmac(
        metadata,POLICY,repo,entries,embedding_commands,install_text,
        dict(path=str(install),sha256=digest(install),bytes=install.stat().st_size),
        manifest_values,ninja_capture,ninja_text)
    authenticate_inputs()
    assert digest(model_path)==POLICY['hashHmacModelSha256']
    return metadata''','helper')
# Physical OWN is honest, prior to any custom imports.
h=edit(h,"# Own literal configured-native context; never mutate an imported donor namespace.",f"assert HERE==Path('{OWN}'), 'Exact active source helper context required'\n# Own literal configured-native context; never mutate an imported donor namespace.",'helper')
(OWN/'layer-policy.py').write_text(h)
r=(DONOR/'build-engine.sh').read_text()
for old,new in [
 (str(DONOR),str(OWN)),
 ('/private/tmp/starling-node-compat/combined-native355-v1-source',FRESH+'-source'),
 ('/private/tmp/starling-node-compat/combined-native355-v2-build',FRESH+'-build'),
 ('combined355-v2','hash-hmac357-v1'),
 ('combined355','Hash/Hmac357'),
 ('complete355','complete357'),
 ('ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1','ACTUAL_FRESH_HASH_HMAC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'),
 ('4e30750fc8967514493b26096e814929ac4e567f1a01d86bc6a140f3bcecf609',sha(OWN/'layer-policy.py')),
 ('fc9c5e97594507513ed20efeced61dbf2be1a92ff038e7f1df1bcddd0b56a681',sha(OWN/'policy.json')),
 ('FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1','FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1'),
 ('nativeFiles=355','nativeFiles=357')]: r=edit(r,old,new,'recipe')
r=edit(r,'consumers_enabled="${NODE_COMPAT_STREAM_CONSUMERS:-0}"', '''consumers_enabled="${NODE_COMPAT_STREAM_CONSUMERS:-0}"
hash_hmac_enabled="${NODE_COMPAT_CRYPTO_HASH_HMAC:-0}"
borrow_enabled="${NODE_CRYPTO_AUDITED_BORROW:-0}"
[[ "$hash_hmac_enabled" == 1 && "$borrow_enabled" == 0 ]] || { echo 'Named experimental recipe requires HASH_HMAC=1 and COPY-only BORROW=0; global defaults remain OFF' >&2; exit 1; }''','recipe')
r=edit(r,'-DENABLE_JS_DEBUGGER=OFF -DENABLE_BUILTIN_WPT_SUPPORT=OFF -DNODE_COMPAT_LOCKED_RUST=ON', '-DNODE_COMPAT_CRYPTO_HASH_HMAC=ON -DNODE_CRYPTO_AUDITED_BORROW=OFF \\\n  -DENABLE_JS_DEBUGGER=OFF -DENABLE_BUILTIN_WPT_SUPPORT=OFF -DNODE_COMPAT_LOCKED_RUST=ON','recipe')
r=edit(r,"    'NODE_COMPAT_STREAM_CONSUMERS': 'ON' if consumers_enabled == '1' else 'OFF',", "    'NODE_COMPAT_STREAM_CONSUMERS': 'ON' if consumers_enabled == '1' else 'OFF',\n    'NODE_COMPAT_CRYPTO_HASH_HMAC':'ON','NODE_CRYPTO_AUDITED_BORROW':'OFF',",'recipe')
r=edit(r,"selected_manifests = [{'path':path",f"manifest_paths.append('{manifest_rel}')\nselected_manifests = [{{'path':path",'recipe')
r=edit(r,"    'gcStress': stress == '1', 'oomTesting': oom == '1',", "    'gcStress': stress == '1', 'oomTesting': oom == '1',\n    'nodeCryptoHashHmacEnabled':True,'nodeCryptoAuditedBorrowEnabled':False,",'recipe')
# Retain entire Ninja listing and terminal before assertions. This is read-only when a later build is authorized.
r=edit(r,"rust_commands = [line for line in command('ninja','-C',build_dir,'-t','commands').splitlines() if 'cargo rustc --lib' in line]",'''ninja_executable=shutil.which('ninja')
assert ninja_executable and pathlib.Path(ninja_executable).is_absolute()
ninja_executable=str(pathlib.Path(ninja_executable).resolve())
ninja_tool=dict(path=ninja_executable,sha256=digest(ninja_executable),bytes=pathlib.Path(ninja_executable).stat().st_size)
ninja_argv=[ninja_executable,'-C',build_dir,'-t','commands']
ninja_stem=pathlib.Path(work)/('full-ninja-'+pathlib.Path(artifact).name)
try:
    ninja_result=subprocess.run(ninja_argv,cwd=repo,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,check=False)
    ninja_out,ninja_err=ninja_result.stdout,ninja_result.stderr
    ninja_exit,ninja_timeout=ninja_result.returncode,False
except subprocess.TimeoutExpired as failure:
    ninja_out,ninja_err=failure.stdout or b'',failure.stderr or b''
    ninja_exit,ninja_timeout=None,True
for suffix,payload in [('.stdout',ninja_out),('.stderr',ninja_err)]:
    with open(str(ninja_stem)+suffix,'xb') as file:file.write(payload);file.flush();os.fsync(file.fileno())
def captured_descriptor(suffix):
    path=pathlib.Path(str(ninja_stem)+suffix)
    return dict(path=str(path),sha256=digest(path),bytes=path.stat().st_size)
ninja_capture=dict(argv=ninja_argv,tool=ninja_tool,rawExitCode=ninja_exit,timeout=ninja_timeout,stdout=captured_descriptor('.stdout'),stderr=captured_descriptor('.stderr'))
with open(str(ninja_stem)+'.terminal.json','x') as file:json.dump(ninja_capture,file,indent=2);file.write('\\n');file.flush();os.fsync(file.fileno())
assert digest(ninja_executable)==ninja_tool['sha256']
assert ninja_exit==0 and not ninja_timeout and ninja_err==b''
ninja_text=ninja_out.decode('utf-8',errors='strict')
rust_commands = [line for line in ninja_text.splitlines() if 'cargo rustc --lib' in line]''','recipe')
# Embedded producer imports existing stdlib only.
r=edit(r,'import datetime, hashlib, json, os, pathlib, subprocess, sys', 'import datetime, hashlib, json, os, pathlib, subprocess, sys, shutil','recipe')
r=edit(r,"metadata = layer.decorate(metadata,repo,source_dir,json.loads(compile_commands),embedding_commands,ticks_enabled == '1')", "metadata = layer.decorate(metadata,repo,source_dir,json.loads(compile_commands),embedding_commands,ticks_enabled == '1',ninja_capture,ninja_text)",'recipe')
start=r.index("before_rustup=pathlib.Path(work)/'private-rustup-settings-before-install.json'")
end=r.index("with open(artifact + '.build.json'",start)
rust=r[start:end]
r=edit(r,rust,'','recipe')
r=edit(r,'# New355-only raw metadata shape gate,',rust+'# New357-only raw metadata shape gate,','recipe')
# Exclusive durable sidecar publication after full shape proof and final helper bookend.
r=edit(r,"    json.dump(metadata, output, indent=2); output.write('\\n')", "    json.dump(metadata, output, indent=2); output.write('\\n'); output.flush(); os.fsync(output.fileno())",'recipe')
(OWN/'build-engine.sh').write_text(r)
write('tooling-derivations.json',dict(schemaVersion=1,donors=[desc(DONOR/n)for n in ['policy.json','layer-policy.py','build-engine.sh','native-admission-model.py']],edits=changes,outputs=[desc(OWN/n)for n in ['policy.json','layer-policy.py','build-engine.sh','native-admission-model.py']],scope='Source derivation only; no native build or metadata conversion'))
print(json.dumps({'state':'SOURCE_GENERATION_ONLY','nativeSources':len(after),'selectedManifests':len(p['selectedModuleManifests']),'edits':len(changes),'actionsInvoked':False}))
