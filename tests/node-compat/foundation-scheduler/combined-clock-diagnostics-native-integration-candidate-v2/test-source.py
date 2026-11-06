"""Inert-module/pure/AST and tiny owned host-I/O tests only. No producer APIs."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,re,shlex,stat,struct,subprocess,sys,tempfile
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
def row(p):
 b=Path(p).read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
checks=[]
def check(name,condition):assert condition,name;checks.append(name)
def reject(name,fn):
 try:fn()
 except(AssertionError,ValueError,KeyError):checks.append(name);return
 raise AssertionError('Did not refuse '+name)
def main():
 refs=read(OWN/'references.json');spec=read(OWN/'policy.json')
 for key in ['controller','recipe','helper','policy','metadataModel','copyPlan','cachePlan','protectedInputs']:
  check('own literal reference '+key,row(refs[key]['path'])==refs[key])
 assert row(spec['basePolicy']['path'])==spec['basePolicy']
 check('inert own controller module context',str(OWN)==str(load('clock357_controller',OWN/'controller.py').OWN))
 controller=load('clock357_controller_test',OWN/'controller.py')
 for key,attribute in [('sourceRoot','SOURCE'),('workRoot','WORK'),('freezeRoot','FREEZE'),('stageOutputRoot','STAGE_OUT'),('buildOutputRoot','BUILD_OUT'),('buildResultRoot','BUILD_RESULT'),('stageJournal','JOURNAL')]:check('real module context '+attribute,str(getattr(controller,attribute))==refs['contexts'][key])
 model=load('clock357_pure_model',OWN/'native-admission-model.py')
 policy=model.assemble_policy(spec,read(spec['basePolicy']['path']))
 check('genuine357 sourcepolicy assembled',len(policy['expectedNativeSourceManifest'])==357)
 check('selected11 unchanged',policy['selectedModuleManifests']==read(spec['basePolicy']['path'])['selectedModuleManifests'])
 for key in ['expectedNativeSourceManifest','diagnosticSourcePolicy']:
  bad=copy.deepcopy(spec)
  if key=='expectedNativeSourceManifest':bad[key].pop()
  else:bad[key]['changes'][0]['beforeSha256']='0'*64
  reject('sourcepolicy '+key+' mismatch',lambda:model.assemble_policy(bad,read(spec['basePolicy']['path'])))
 root=policy['contexts']['configuredSourceRoot'];work=policy['contexts']['workRoot']
 def command(path,diagnostic=False):return 'clang++ --target=wasm32-wasi -fno-exceptions -O3 -DNDEBUG '+('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1 'if diagnostic else'')+'-I'+root+'/include -c '+path
 cpp=[r['path']for r in policy['expectedNativeSourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))]
 check('63 actual source-inventory CPP paths',len(cpp)==63)
 shared=policy['diagnosticSourcePolicy']['sharedNativeTUs']
 entries=[dict(file=root+'/'+p,command=command(root+'/'+p,p in shared))for p in cpp]
 others=['host-apis/wasi-0.2.0/host_api.cpp','host-apis/wasi-0.2.0/worker.cpp','host-apis/wasi-0.2.0/error.cpp','host-apis/wasi-0.2.0/io.cpp','host-apis/wasi-0.2.0/fixture.c']
 entries+=[dict(file=root+'/'+p,command=command(root+'/'+p,p in shared))for p in others]
 null=work+'/engine/starling-raw.wasm/null.cpp';entries.append(dict(file=null,command=command(null)))
 embedding=[command(work+'/componentize/embedding/embedding.cpp',True)]
 requested={k:'ON'for k in ['NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE','ENABLE_BUILTIN_WEB_PERFORMANCE']}
 actual=model.classify_diagnostic_commands(policy,entries,embedding,requested,requested)
 check('six real native shared sites plus separate embedding classified',len(actual)==7)
 # A NEW synthetic Source-schema fixture, never a modified parent metadata
 # frame or an artifact/admission proof. No actual build/emitter is called.
 fixture={k:None for k in policy['expectedRawMetadataFields']}
 for k in ['profileEnabled','internalTicksEnabled','classicStreamsEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','zlibEnabled','streamConsumersEnabled','abiFixEnabled','bigIntFixEnabled','strictInitialization']:fixture[k]=True
 for k in ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled']:fixture[k]=False
 cmake=dict(requested,CMAKE_BUILD_TYPE='Release',WEVAL='OFF',USE_WASM_OPT='ON',ENABLE_BUILTIN_NODE_COMPAT='ON',ENABLE_BUILTIN_WEB_TIMERS='ON',ENABLE_BUILTIN_WEB_CRYPTO='ON',ENABLE_BUILTIN_WEB_TEXT_CODEC='ON',ENABLE_JS_DEBUGGER='OFF',ENABLE_BUILTIN_WPT_SUPPORT='OFF',NODE_COMPAT_LOCKED_RUST='ON',NODE_COMPAT_GC_STRESS='OFF',NODE_COMPAT_OOM_TESTING='OFF',NODE_COMPAT_ENTROPY_MODE='OFF',CMAKE_C_COMPILER_LAUNCHER='',CMAKE_CXX_COMPILER_LAUNCHER='')
 for flag in ['PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB','INTERNAL_TICKS','CLASSIC_STREAMS','ZLIB','STREAM_CONSUMERS']:cmake['NODE_COMPAT_'+flag]='ON'
 native_commands=[r['command']for r in entries[:63]];other_commands=[r['command']for r in entries[63:68]]
 private=[next(r['command']for r in entries if r['file']==root+'/'+p)for p in policy['privateTargetCpp']]
 fresh=dict(state='ACTUAL_FRESH_CLOCK_DIAGNOSTIC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V2',configuredSourceRoot=root,workRoot=work,sourceDir=work+'/componentize',buildDir=work+'/engine',artifact=work+'/artifacts/'+refs['artifactBasename'],sourceDirExisted=False,buildDirExisted=False,artifactExisted=False,compilerLauncherReuseAllowed=False,rustIncrementalReuseAllowed=False)
 fixture.update(buildRecipeSha256=refs['recipe']['sha256'],sourceManifest=policy['expectedNativeSourceManifest'],componentizeSourceManifest=policy['expectedComponentizeSourceManifest'],entropyPolicy='off',requestedCMakeOptions=cmake,observedCMakeOptions=dict(cmake),selectedModuleManifests=policy['selectedModuleManifests'],internalTickPolicy=dict(version=policy['version'],policyFileSha256=refs['policy']['sha256'],helperSha256=refs['helper']['sha256'],actualLayoutCompileCommands=native_commands),strictEventExceptionPolicy=dict(version=policy['strictPolicyVersion'],actualNativeCompileCommands=native_commands[:4]),protectedAbortListenerPolicy=dict(version=policy['protectedPolicyVersion']),classicStreamsPolicy=dict(actualPrivateTargetCompileCommands=private),cryptoKeyOwnershipPolicy=policy['cryptoKeyOwnershipSourcePolicy'],cryptoSecretFailureSourcePolicy=policy['cryptoSecretFailureSourcePolicy'],cryptoKeyOwnershipBuildEvidence=dict(cryptoBuiltinEnabled=True,installationSource=dict(count=1),changedNativeCompileCommands=native_commands[:3]),cryptoSecretFailureBuildEvidence=dict(cryptoBuiltinEnabled=True,changedNativeCompileCommands=native_commands[:2],faultInjectionObserved=False,runtimeValidation=None),resourceOwnershipPolicy=dict(sourcePolicy=policy['resourceOwnershipSourcePolicy'],policyFileSha256=refs['policy']['sha256'],helperSha256=refs['helper']['sha256'],timerInstallation=dict(webTimersEnabled='ON'),nativeRuntimeValidation=None,fullResetOrReuse=False),taskSelectionPolicy=dict(sourcePolicy=policy['taskSelectionSourcePolicy'],policyFileSha256=refs['policy']['sha256'],helperSha256=refs['helper']['sha256'],allNativeDependentsRequireRebuild=True,nativeAllInvalidRuntimeValidation=None,fullResetOrReuse=False,actualHostApiCompileCommands=[other_commands[0]],actualEventLoopCompileCommands=[next(r['command']for r in entries if r['file']==root+'/runtime/event_loop.cpp')]),zlibErrorSemanticsPolicy=dict(sourcePolicy=policy['zlibErrorSemanticsSourcePolicy'],policyFileSha256=refs['policy']['sha256'],helperSha256=refs['helper']['sha256'],runtimeValidation=None,remainingDeviationsApproved=False,remainingRecordedDifferences=15),zlibSelectedCodecInput=None,zlibPolicy=dict(moduleManifestSha256=policy['zlibManifestSha256'],runtimeBackendProof=dict(verified=False,version=None,vernum=None),codecWitness=dict(selectedCompileInput=None,runtimeBackendProof=dict(verified=False,version=None,vernum=None),sourceInputsCheckedBeforeAndAfterBuild=True,actualKernelCompileCommands=[native_commands[0]])),streamConsumersPolicy=dict(moduleManifestSha256=policy['streamConsumersSourcePolicy']['moduleManifestSha256'],installationOrder=dict(decoderBeforeNode=True)),combinedNativeSourcePolicy=dict(sourcePolicy=policy['combinedSourcePolicy'],policyFileSha256=refs['policy']['sha256'],helperSha256=refs['helper']['sha256'],configuredSourceRoot=root,workRoot=work,externalConfiguredSourceRoot=work+'/componentize',selectedManifests=policy['selectedManifestValues'],sourceManifestCheckedBeforeAndAfterBuild=True,actualCompileDatabaseRows=69,actualPolicyCppCompileCommands=native_commands,actualOtherConfiguredCompileCommands=other_commands,actualGeneratedNullCompileCommands=[entries[-1]['command']],actualSeparateEmbeddingCompileCommands=embedding,privateBackendEvidenceHookEnabled=False,freshAbiEvidence=fresh,runtimeValidation=None,operationalAdmission=False),actualEmbeddingCompileCommands=embedding,cmakeCachePath=work+'/engine/CMakeCache.txt',enginePath=fresh['artifact'],clockLifecycleDiagnosticSourcePolicy=policy['diagnosticSourcePolicy'],clockLifecycleDiagnosticBuildEvidence=dict(diagnosticOnly=True,actualSharedCompileCommands=actual,actualInstallation=dict(namespace='NS_DEF(diagnostics::clock_lifecycle)',count=1,performanceTargetEnabled=True),actualPolicyCpp=63,actualDatabaseRows=69,actualNodePrivateCpp=6,actualSeparateEmbeddingCpp=1,actualLinkedInlineStateIdentityProved=False,actualStrongGetterLinkProved=False,nativeClockOrSelectorRuntimeInvoked=False,fullSeventeenGateAccepted=False,operationalAdmission=False,runtimeValidation=None))
 def shape(value):return model.validate_metadata(value,policy,refs['policy']['sha256'],refs['helper']['sha256'],refs['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
 classified=shape(fixture);check('real own whole82 validator accepts new synthetic schema only',classified==dict(state='FINITE_CLOCK_DIAGNOSTIC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V2',nativeFiles=357,rawMetadataFields=82,engineRead=False,runtimeAccepted=False,grantsAuthority=False))
 for label,mutate in [('parent80shortframe',lambda v:[v.pop(k)for k in ['clockLifecycleDiagnosticSourcePolicy','clockLifecycleDiagnosticBuildEvidence']]),('Hash83extrafield',lambda v:v.update(nodeCryptoHashHmacEnabled=True)),('wrong357manifest',lambda v:v['sourceManifest'].pop()),('runtimeclaim',lambda v:v['clockLifecycleDiagnosticBuildEvidence'].update(fullSeventeenGateAccepted=True)),('wrong69DB',lambda v:v['combinedNativeSourcePolicy'].update(actualCompileDatabaseRows=68))]:
  bad=copy.deepcopy(fixture);mutate(bad);reject('whole metadata model '+label,lambda:shape(bad))
 for n in range(7):
  bad=copy.deepcopy(entries);emb=list(embedding)
  if n==6:emb[0]=emb[0].replace('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1','')
  else:
   selected=next(r for r in bad if r['file']==root+'/'+shared[n]);selected['command']=selected['command'].replace('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1','')
  reject('missing shared macro site '+str(n),lambda:model.classify_diagnostic_commands(policy,bad,emb,requested,requested))
 for suffix in [' -DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=0',' -UNODE_COMPAT_LIFECYCLE_DIAGNOSTICS',' -DNODE_COMPAT_GC_STRESS=1',' -DNODE_COMPAT_CRYPTO_HASH_HMAC=1',' -DDEBUG',' -fsyntax-only']:
  reject('shared command wrong flags '+suffix,lambda:model.classify_diagnostic_commands(policy,entries,[embedding[0]+suffix],requested,requested))
 reject('embedding original-source include missing',lambda:model.classify_diagnostic_commands(policy,entries,[embedding[0].replace('-I'+root+'/include','')],requested,requested))
 for field in requested:
  bad=dict(requested);bad[field]='OFF';reject('observed option '+field,lambda:model.classify_diagnostic_commands(policy,entries,embedding,requested,bad))
 reject('duplicate actual compile entry',lambda:model.classify_diagnostic_commands(policy,entries+[entries[0]],embedding,requested,requested))
 # Exact real recipe literal join predicates, not a separate desired-value list.
 recipe=(OWN/'build-engine.sh').read_text();helper=(OWN/'layer-policy.py').read_text()
 joins=re.findall(r"(?:sha256_file \"\$consumers_layer_root/(layer-policy\.py|policy\.json)\"\)\" == |digest\(layer_file\) == ')([0-9a-f]{64})",recipe)
 check('all seven literal helper/policy predicates discovered',len(joins)==7)
 for n,(name,digest)in enumerate(joins):
  name=name or'layer-policy.py';check('literal join '+str(n),row(OWN/name)['sha256']==digest)
  check('stale literal join rejects '+str(n),row(OWN/name)['sha256']!='0'*64)
 check('helper own policy selfhash',re.search(r"POLICY_SHA256='([0-9a-f]{64})'",helper).group(1)==row(OWN/'policy.json')['sha256'])
 check('helper verifies own model before loading',"assert digest(model_path)==SPEC['admissionModelSha256']"in helper and spec['admissionModelSha256']==row(OWN/'native-admission-model.py')['sha256'])
 fields=set();python_blocks=[]
 for match in re.finditer(r"<<'([A-Z][A-Z0-9_]*)'\n",recipe):
  end=recipe.index('\n'+match.group(1)+'\n',match.end());body=recipe[match.end():end];tree=ast.parse(body);python_blocks.append(body)
  for node in ast.walk(tree):
   if isinstance(node,ast.Assign):
    for target in node.targets:
     if isinstance(target,ast.Name)and target.id=='metadata'and isinstance(node.value,ast.Dict):fields.update(k.value for k in node.value.keys if isinstance(k,ast.Constant)and isinstance(k.value,str))
     if isinstance(target,ast.Subscript)and isinstance(target.value,ast.Name)and target.value.id=='metadata'and isinstance(target.slice,ast.Constant)and isinstance(target.slice.value,str):fields.add(target.slice.value)
 for node in ast.walk(ast.parse(helper)):
  if isinstance(node,ast.Assign):
   for target in node.targets:
    if isinstance(target,ast.Subscript)and isinstance(target.value,ast.Name)and target.value.id=='metadata'and isinstance(target.slice,ast.Constant)and isinstance(target.slice.value,str):fields.add(target.slice.value)
 check('fresh source-emitter fieldnames exact82',fields==set(spec['expectedRawMetadataFields'])and len(fields)==82)
 check('exact82 gate follows actual last Rustup field',recipe.index("metadata['privateRustupBootstrapPolicy']")<recipe.index("classification=model.validate_metadata(")<recipe.index("with open(artifact + '.build.json', 'x')"))
 result_fn=next(n for n in ast.parse((OWN/'native-admission-model.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='validate_metadata')
 result_return=ast.literal_eval(next(n for n in reversed(result_fn.body)if isinstance(n,ast.Return)).value)
 emitter_asserts=[n for body in python_blocks for n in ast.walk(ast.parse(body))if isinstance(n,ast.Assert)and isinstance(n.test,ast.Compare)and isinstance(n.test.left,ast.Name)and n.test.left.id=='classification']
 check('one actual emitter classification-return predicate',len(emitter_asserts)==1)
 expression=emitter_asserts[0].test.comparators[0];assert isinstance(expression,ast.Call)and expression.func.id=='dict'and not expression.args
 emitter_return={k.arg:ast.literal_eval(k.value)for k in expression.keywords}
 check('actual classifier and emitter result join exact357/82',emitter_return==result_return and emitter_return['nativeFiles']==357 and emitter_return['rawMetadataFields']==82)
 for p in OWN.glob('*.py'):ast.parse(p.read_text());checks.append('Python AST '+p.name)
 bash=refs['bash'];check('pinned Bash hash before grammar',row(bash['path'])==bash)
 grammar=subprocess.run([bash['path'],'-n',str(OWN/'build-engine.sh')],capture_output=True,timeout=30)
 (OWN/'bash-grammar.stdout.log').write_bytes(grammar.stdout);(OWN/'bash-grammar.stderr.log').write_bytes(grammar.stderr)
 check('actual Bash grammar only raw0',grammar.returncode==0 and not grammar.stdout and not grammar.stderr)
 for k in ['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE','BASH_FUNC_rustup%%']:
  parent={'HOME':'original-home','home':'lowercase','CODEX_HOME':'original-codex',k:'inherited'}
  cleaned,names=controller.clean_environment(parent);check('clean inherited '+k,k in names and k not in cleaned and all(cleaned[x]==parent[x]for x in ['HOME','home','CODEX_HOME']))
 env=controller.build_environment({'HOME':'original','RUSTC_WRAPPER':'bad','CARGO_ENCODED_RUSTFLAGS':'bad','NODE_OPTIONS':'bad','PATH':'bad'},refs)
 check('build command environment drops wrapper overrides',all(k not in env for k in ['RUSTC_WRAPPER','CARGO_ENCODED_RUSTFLAGS','NODE_OPTIONS'])and env['HOME']=='original'and env['CARGO_HOME'].startswith(work+'/'))
 commands=controller.git_commands(refs['git']['path']);fetch=commands[1]
 check('real private baseline-only command sequence',len(commands)==5 and '--depth=1'in fetch and '--no-tags'in fetch and fetch[-1]==controller.BASE and fetch[-2]==controller.REPO.as_uri())
 upload=next(x.split('=',1)[1]for x in fetch if x.startswith('--upload-pack='))
 check('real upload-pack tokens roundtrip shell quoting',shlex.split(upload)==controller.git_prefix(refs['git']['path'])+['-c','uploadpack.allowAnySHA1InWant=true','upload-pack'])
 gitenv=controller.git_environment({'HOME':'original','CODEX_HOME':'codex','GIT_CONFIG_PARAMETERS':'bad','GIT_SSH_COMMAND':'bad','BASH_ENV':'bad','BASH_FUNC_git%%':'bad'})
 check('Git and Bash inherited overrides removed',all(x not in gitenv for x in ['GIT_CONFIG_PARAMETERS','GIT_SSH_COMMAND','BASH_ENV','BASH_FUNC_git%%'])and gitenv['HOME']=='original'and gitenv['CODEX_HOME']=='codex'and gitenv['GIT_OPTIONAL_LOCKS']=='0')
 root_authority=read(OWN/'root-authority.template.json');own=dict(path=str(OWN/'index.json'),sha256='0'*64,bytes=1)
 for phase in ['stage','build']:
  r=copy.deepcopy(root_authority);r.update(phase=phase,sourceIndex=own,sourceStageAllowed=phase=='stage',nativeBuildAllowed=phase=='build',deadlineSeconds=600 if phase=='stage'else 7200)
  if phase=='build':r.update(actualStageReview={'index':{},'result':{}},actualStageResult={})
  controller.root_model(r,own,refs,phase);checks.append('actual Rootmodel '+phase)
  for k in ['engineExecutionAllowed','clockRuntimeAllowed','cryptoAllowed','gcAllowed','oomAllowed','debugAllowed','allSeventeenGatesAccepted']:
   bad=copy.deepcopy(r);bad[k]=True;reject('Root denies '+phase+' '+k,lambda:controller.root_model(bad,own,refs,phase))
  bad=copy.deepcopy(r);bad['deadlineSeconds']=7500;reject('Root deadline '+phase,lambda:controller.root_model(bad,own,refs,phase))
 # Benign real fchmod seam under077. No actual stage/cache/native source copied.
 with tempfile.TemporaryDirectory(prefix='clock357-source-copy-',dir='/private/tmp')as temporary:
  d=Path(temporary);old=os.umask(0o077)
  try:
   for mode in [0o644,0o755]:
    source=d/('source-'+str(mode));source.write_bytes(b'bounded host fixture\n');source.chmod(mode)
    buggy=d/('old-'+str(mode));fd=os.open(str(buggy),os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode);os.close(fd)
    check('old umask mode refusal '+str(mode),stat.S_IMODE(buggy.stat().st_mode)!=mode)
    target=d/('new-'+str(mode));controller.copy_regular(row(source),target,mode)
    check('genuine source-copy explicit mode '+str(mode),target.read_bytes()==source.read_bytes()and stat.S_IMODE(target.stat().st_mode)==mode and target.stat().st_ino!=source.stat().st_ino)
  finally:os.umask(old)
 def index_bytes(changed_stat=False,changed_oid=False):
  raw=b'DIRC'+struct.pack('>II',2,742)
  for i in range(742):
   name=('baseline-%04d.cpp'%i).encode();values=[0]*10;values[6]=0o100644
   if changed_stat:values[0]=123;values[1]=456
   oid=(b'Y'if changed_oid and i==17 else b'X')*20
   entry=struct.pack('>10I',*values)+oid+struct.pack('>H',len(name))+name+b'\0';entry+=b'\0'*((-len(entry))%8);raw+=entry
  return raw+hashlib.sha1(raw).digest()
 def observation(raw):return dict(file=dict(path='/synthetic/index',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),mode=0o600,device=1,inode=2,links=1,parsed=controller.parse_index(raw))
 a=observation(index_bytes());b=observation(index_bytes(True));classified=controller.index_stat_only(a,b)
 check('only Git index stat-cache changes admitted',classified['statCacheBytesChanged']and classified['semanticsAndFlagsExtensionsUnchanged'])
 replaced=copy.deepcopy(b);replaced['inode']=3;check('atomic index replacement retains honest identity limit',controller.index_stat_only(a,replaced)['originalIndexInodePreserved']is False)
 reject('Git object identity change refused',lambda:controller.index_stat_only(a,observation(index_bytes(changed_oid=True))))
 bad=copy.deepcopy(b);bad['mode']=0o644;reject('Git index mode change refused',lambda:controller.index_stat_only(a,bad))
 bad=copy.deepcopy(b);bad['parsed']['extensionsHex']='0000';reject('Git index extension change refused',lambda:controller.index_stat_only(a,bad))
 reject('Git corrupt index checksum refused',lambda:controller.parse_index(index_bytes()[:-1]+b'!'))
 output=dict(schemaVersion=1,state='SOURCE_PURE_GRAMMAR_AND_BENIGN_COPY_CHECKS_PASSED_V2',checks=len(checks),checkNames=checks,pythonHeredocsParsed=len(python_blocks),compilerOrStageOrProducerOrHelperInvoked=False,realBenignHostCopyCases=4,syntheticGitBaselineEntries=742,newMetadataProduced=False,rawMetadataSchemaProspective=82)
 (OWN/'test-results.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
if __name__=='__main__':main()
