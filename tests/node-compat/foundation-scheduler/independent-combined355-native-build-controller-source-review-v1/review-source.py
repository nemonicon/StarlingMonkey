"""Independent Source read/hash/AST and pure environment model; no actions."""
from pathlib import Path
import ast,hashlib,json,os,shutil,stat
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'combined-native-build-controller-candidate-v1'
checks=0
def check(v):
    global checks
    assert v;checks+=1
def row(p):
    p=Path(p);a=p.stat();check(p.is_file()and not p.is_symlink());h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    check(key(a)==key(z));return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def verify(r):check(row(r['path'])==r)
def load(p):return json.loads(Path(p).read_bytes())
def family(ix):
    verify(ix);base=Path(ix['path']).parent;names={'index.json'}
    for r in load(ix['path'])['files']:
        check(not r['path'].startswith('/')and '..'not in Path(r['path']).parts and r['path']not in names);names.add(r['path']);verify(dict(path=str(base/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    check({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names)
    check(not any(p.is_symlink()for p in base.rglob('*')))
ix=row(SOURCE/'index.json');check(ix['sha256']=='d646d2ec64aedbfa59a077abf76d0c6267d710fbc0590d9b71007f88ef740a8c');family(ix)
refs=load(SOURCE/'references.json');inputs=load(SOURCE/'source-inputs.json')
check(len(inputs['files'])==len(inputs['modeRows'])==3403)
for r in inputs['files']:verify(r)
for r in inputs['modeRows']:check(stat.S_IMODE(Path(r['file']['path']).stat().st_mode)==r['mode'])
for f in refs['families']:family(f)
check(len(refs['families'])==8)
stage=load(refs['actualStageReview']['result']['path']);check(stage['verifiedPassed']is True and stage['sourceIndexSha256']==refs['integrationIndex']['sha256'])
journal=load(refs['stageResult']['path']);plan=load(refs['stageCopyPlan']['path'])['files'];check(journal['copies']==journal['copiesCompleted']==plan and len(plan)==1613)
ids=set();original_ids=set();target=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
for r in plan:
    verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']));verify(dict(path=str(target/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    a=Path(r['original']).stat();b=(target/r['path']).stat();check(stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)==r['sourceMode']and b.st_nlink==1)
    original_ids.add((a.st_dev,a.st_ino));ids.add((b.st_dev,b.st_ino))
check(len(ids)==1613 and not ids&original_ids)
for r in refs['hostTools']:check(str(Path(shutil.which(r['name'],path=refs['hostPath'])).resolve())==r['executable']['path']);verify(r['executable'])
text=(SOURCE/'controller.py').read_text();tree=ast.parse(text)
for d in load(SOURCE/'derivations.json')['functions']:
    donor=Path(d['donorPath']).read_text();n=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==d['symbol'])
    old=''.join(donor.splitlines(keepends=True)[d['firstLine']-1:d['lastLine']])+'\n';new=''.join(text.splitlines(keepends=True)[n.lineno-1:n.end_lineno])+'\n'
    check(new==old and len(old.encode())==d['bytes']and hashlib.sha256(old.encode()).hexdigest()==d['sha256'])
for p in SOURCE.glob('*.py'):ast.parse(p.read_text());check(True)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='build_environment');ns={'WORK':Path('/private/tmp/starling-node-compat/combined-native355-v1-build')}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pure inherited env DATA model>','exec'),ns)
policy=dict(schemaVersion=1,mandatoryBeforeControllerSpawn=True,removePrefixes=['BASH_FUNC_'],removeExactNames=['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE'],preserveExactNames=['HOME','home','CODEX_HOME'],rootAuthorityMustBindPolicy=True,rootLauncherMustEnforcePolicy=True,actualChildMustContainNoRemovedEntries=True,recordRemovedVariableNamesOnly=True,recordEnvironmentValues=False,scope='Known inherited Bash function and startup controls; not an OS or universal environment sandbox')
model=dict(HOME='/PURE/home',home='/PURE/lower-home',CODEX_HOME='/PURE/codex')
for name in ['BASH_FUNC_rustup%%','BASH_FUNC_cargo%%','BASH_FUNC_cmake%%','BASH_FUNC_cbindgen%%']:model[name]='() { :; }'
unclean=ns['build_environment'](model,refs);retained=[k for k in model if k.startswith('BASH_FUNC_')and k in unclean];check(len(retained)==4)
clean={k:v for k,v in model.items()if not any(k.startswith(p)for p in policy['removePrefixes'])and k not in policy['removeExactNames']}
after=ns['build_environment'](clean,refs);check(not any(k.startswith('BASH_FUNC_')or k in policy['removeExactNames']for k in after))
check(all(after[k]==model[k]for k in policy['preserveExactNames']))
check(after['RUSTUP_HOME']==str(ns['WORK']/'rustup-home')and after['CARGO_HOME']==str(ns['WORK']/'cargo-home')and after['RUSTUP_TOOLCHAIN']=='1.88.0')
check(refs['buildEnvironment']['NODE_COMPAT_BUILD_TYPE']=='Release'and refs['buildEnvironment']['NODE_COMPAT_ENTROPY_MODE']=='OFF'and refs['buildEnvironment']['NODE_COMPAT_GC_STRESS']==refs['buildEnvironment']['NODE_COMPAT_OOM_TESTING']=='0')
check(all(refs['buildEnvironment']['NODE_COMPAT_'+n]=='1'for n in ['PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB','INTERNAL_TICKS','CLASSIC_STREAMS','ZLIB','STREAM_CONSUMERS']))
recipe=Path(refs['recipe']['path']).read_text();sdk=(target/'cmake/wasi-sdk.cmake').read_text();cpm=(target/'cmake/CPM.cmake').read_text()
check('rustup toolchain install 1.88.0 --profile minimal'in recipe and 'rustup target add --toolchain 1.88.0 wasm32-wasip1'in recipe)
check('export CPM_SOURCE_CACHE="$work_root/cache"'in recipe and '-DCMAKE_C_COMPILER_LAUNCHER= -DCMAKE_CXX_COMPILER_LAUNCHER='in recipe)
check('CPMAddPackage(NAME wasi-sdk URL ${WASI_SDK_URL})'in sdk and 'URL_HASH'not in sdk and 'WASI_SDK_VERSION 30'in sdk)
check('EXPECTED_HASH SHA256=${CPM_HASH_SUM}'in cpm)
cmake_download=Path('/opt/homebrew/Cellar/cmake/4.3.3/share/cmake/Modules/ExternalProject/download.cmake.in')
check('if("@ALGO@" STREQUAL "")'in cmake_download.read_text()and '# No check'in cmake_download.read_text())
worker_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='worker');worker_source=ast.get_source_segment(text,worker_node)
check(worker_source.index("if result.get('rawChildExitCode')==0:")<worker_source.index('validate_metadata(value,policy,refs)'))
cache=load(SOURCE/'cache-plan.json');check(len(cache['copies'])==4 and cache['totalCopyBytes']==205865445 and cache['sdkTreeOrBuildObjectsReused']is False)
for r in cache['copies']:check(stat.S_IMODE(Path(r['source']['path']).stat().st_mode)==r['sourceMode'])
stored=load(SOURCE/'source-check-results.json');check(stored['checks']==13715 and stored['pureCases']==66)
for key in ['configuredSourceRoot','workRoot','freezeRoot']:check(key in load(SOURCE/'root-authority.template.json'))
for p in ['/private/tmp/starling-node-compat/combined-native355-v1-build','/private/tmp/starling-node-compat/combined-native355-v1-freeze','/private/tmp/starling-node-compat/combined-native355-v1-normal-off-build-root','/private/tmp/starling-node-compat/combined-native355-v1-normal-off-build-external-root']:check(not Path(p).exists()and not Path(p).is_symlink())
family(ix)
(HERE/'required-root-environment-policy.json').write_text(json.dumps(policy,indent=2)+'\n')
(HERE/'counterexample.json').write_text(json.dumps(dict(schemaVersion=1,kind='PURE_EXPORTED_BASH_FUNCTION_TRANSPORT_COUNTEREXAMPLE',actualRootEnvironmentContaminationClaimed=False,unfilteredSourceRetainsNames=retained,valuesNotRecorded=True,mandatoryRootPolicyClosesThisTransport=True,shellOrNativeProgramExecuted=False),indent=2)+'\n')
out=dict(schemaVersion=1,sourceIndex=ix,checks=checks,sourceMembers=22,declaredInputsVerified=3403,logicalInputBytes=sum(r['bytes']for r in inputs['files']),fixedFamiliesVerified=8,stageCopiesVerified=1613,stageModeAndDistinctInodeChecksPassed=True,exactGenericFunctions=8,storedOwnerPureCasesAuthenticatedNotRerun=66,mandatoryRootEnvironmentCleaning=True,sdkArchiveDigestCheckAfterBuildOnly=True,sdkPreExtractDigestGuardPresent=False,cmakeSdkPolicy=row(target/'cmake/wasi-sdk.cmake'),cmakeCpmBootstrap=row(target/'cmake/CPM.cmake'),cmakeDownloadSemantics=row(cmake_download),ownerOperationalFunctionsInvoked=False,cacheCopiesExecuted=False,monitorOrLifecycleExecuted=False,compilerOrNativeBuildInvoked=False,engineOrGuestInvoked=False)
(HERE/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
