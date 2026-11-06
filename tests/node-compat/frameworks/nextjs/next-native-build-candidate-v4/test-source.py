"""Source/model tests only. Never invokes the build caller, tools or utilities.
CMake -P tests replace execute_process/CPM only in a disposable test program.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,subprocess,tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('inert_next_intl_build',HERE/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def check(name,fn):
 fn();checks.append(name)
def refuse(fn):
 try:fn()
 except (AssertionError,KeyError,TypeError,ValueError):return
 raise AssertionError('unexpected acceptance')

p=json.loads((HERE/'plan.json').read_bytes());base=m.read(p['basePlan']);before=json.loads((HERE/'preinstalled-rust-mapping.json').read_bytes());cmake=next(x['executable']['path']for x in base['hostTools']if x['name']=='cmake');m.checked(next(x['executable']for x in base['hostTools']if x['name']=='cmake'))
source=(HERE/'run.py').read_text();nodes={n.name:ast.get_source_segment(source,n)for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
parent=m.checked(p['baseRunner']).read_text();old={n.name:ast.get_source_segment(parent,n)for n in ast.parse(parent).body if isinstance(n,ast.FunctionDef)}
for name in ['descriptor','checked','read','save','copy_exclusive','confined','selected_manifests','load_utility','safe_extract','phase_succeeded','cache_values']:
 check('genuine original function '+name,lambda n=name: (_ for _ in ()).throw(AssertionError(n))if nodes[n]!=old[n]else None)
check('exact disk3GiB1GiB',lambda: None if p['disk']==dict(startBytes=3*1024**3,stopBytes=1024**3)else (_ for _ in ()).throw(AssertionError()))
for k in ['SPIDERMONKEY_INTL','NODE_COMPAT_PREINSTALLED_RUST','CPM_LOCAL_PACKAGES_ONLY']:
 check('explicit '+k,lambda k=k:None if p['cmakeAdditions'][k]=='ON'else (_ for _ in ()).throw(AssertionError()))
check('no rustup resolution',lambda:None if p['cmakeAdditions']['Rust_RESOLVE_RUSTUP_TOOLCHAINS']=='OFF'else (_ for _ in ()).throw(AssertionError()))
check('authority absent',lambda:refuse(lambda:m.validate_authority({})))
root=dict(schemaVersion=1,state='ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1',buildAllowed=True,configureAllowed=True,coherentPatchedIntlLibraryAndHeaders=True,engineOrGuestExecutionAllowed=False,freezeAllowed=False,networkAllowed=False,rustupAllowed=False,workRoot='/private/tmp/starling-node-compat/next-native-intl-build-model-only')
for k in ['entry','plan','callerIndex','composition','installedGeneratorResult','intlLockfile','offlineCargoConfig','intlCargoAudit','spidermonkeyEvidence','savedFramePatchIndex']:root[k]={}
check('pure complete authority shape',lambda:m.validate_authority(root))
for key,value in [('state','ROOT_EXPERIMENTAL_NEXT_NATIVE_BUILD_AUTHORITY_V1'),('buildAllowed',False),('configureAllowed',False),('coherentPatchedIntlLibraryAndHeaders',False),('engineOrGuestExecutionAllowed',True),('freezeAllowed',True),('networkAllowed',True),('rustupAllowed',True),('workRoot','/tmp/escape')]:
 check('refuse '+key,lambda key=key,value=value:refuse(lambda:m.validate_authority({**root,key:value})))
record=dict(rawExitCode=0,outerRawExitCode=0,ownedGone=True,innerOwnedClean=True,timeout=False,forcedCleanup=False,errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[])
check('clean owned phase',lambda:None if m.phase_succeeded(record)else (_ for _ in ()).throw(AssertionError()))
for k,v in [('rawExitCode',1),('outerRawExitCode',1),('ownedGone',False),('innerOwnedClean',False),('timeout',True),('forcedCleanup',True),('errors',['x']),('signals',[2]),('interruptedSignals',[15]),('remainingObservedPids',[1])]:
 check('phase refuses '+k,lambda k=k,v=v:None if not m.phase_succeeded({**record,k:v})else (_ for _ in ()).throw(AssertionError()))
with tempfile.TemporaryDirectory(prefix='next-build-v4-source-',dir='/private/tmp')as temp:
 t=Path(temp);tree=t/'tree';tree.mkdir();(tree/'a').write_text('a');(tree/'d').mkdir();(tree/'d/b').write_text('b');(tree/'alias').symlink_to('d/b');snap=m.tree_snapshot(tree);inv=t/'inventory.json';inv.write_text(json.dumps(snap));row=m.descriptor(inv)
 check('real small complete tree inventory',lambda:m.authenticate_tree(dict(root=str(tree),inventory=row)))
 check('safe link retained',lambda:None if next(x for x in snap['entries']if x['path']=='alias')['kind']=='symlink'else (_ for _ in ()).throw(AssertionError()))
 (tree/'a').write_text('changed');check('changed bytes refused',lambda:refuse(lambda:m.authenticate_tree(dict(root=str(tree),inventory=row))));(tree/'a').write_text('a')
 (tree/'extra').write_text('x');check('extra member refused',lambda:refuse(lambda:m.authenticate_tree(dict(root=str(tree),inventory=row))));(tree/'extra').unlink()
 stable=m.tree_snapshot(tree);(tree/'replacement').write_bytes((tree/'a').read_bytes());os.replace(tree/'replacement',tree/'a');changed=m.tree_snapshot(tree)
 check('identical bytes new inode refused by runtime bookend',lambda:None if m.tree_content(stable)==m.tree_content(changed)and stable!=changed else (_ for _ in ()).throw(AssertionError()))
 (tree/'alias').unlink();(tree/'alias').symlink_to('../inventory.json');check('escaping link refused',lambda:refuse(lambda:m.tree_snapshot(tree)));(tree/'alias').unlink()
 (tree/'alias').symlink_to(str(tree/'a'));check('absolute link refused',lambda:refuse(lambda:m.tree_snapshot(tree)))
 # Execute only the real CMake decision code; replace side effects with recording
 # functions. There is no project()/enable_language()/package/compiler call.
 tools=t/'tools';tools.mkdir();(tools/'rustc').touch();(tools/'cargo').touch();(tools/'proxy').symlink_to('rustc');(t/'rust-toolchain.toml').write_text('[toolchain]\nchannel = "1.88.0"\n')
 actual=m.checked(before['after']).read_text();cmake_cases=[]
 for name,settings,ok,calls in [
  ('default-off',{},True,2),('explicit-off',{'NODE_COMPAT_PREINSTALLED_RUST':'OFF'},True,2),
  ('direct-on',{'NODE_COMPAT_PREINSTALLED_RUST':'ON','Rust_COMPILER':str(tools/'rustc'),'Rust_CARGO':str(tools/'cargo'),'Rust_RESOLVE_RUSTUP_TOOLCHAINS':'OFF'},True,0),
  ('relative-tool',{'NODE_COMPAT_PREINSTALLED_RUST':'ON','Rust_COMPILER':'rustc','Rust_CARGO':str(tools/'cargo'),'Rust_RESOLVE_RUSTUP_TOOLCHAINS':'OFF'},False,0),
  ('missing-tool',{'NODE_COMPAT_PREINSTALLED_RUST':'ON','Rust_COMPILER':str(tools/'missing'),'Rust_CARGO':str(tools/'cargo'),'Rust_RESOLVE_RUSTUP_TOOLCHAINS':'OFF'},False,0),
  ('directory-tool',{'NODE_COMPAT_PREINSTALLED_RUST':'ON','Rust_COMPILER':str(tools),'Rust_CARGO':str(tools/'cargo'),'Rust_RESOLVE_RUSTUP_TOOLCHAINS':'OFF'},False,0),
  ('symlink-tool',{'NODE_COMPAT_PREINSTALLED_RUST':'ON','Rust_COMPILER':str(tools/'proxy'),'Rust_CARGO':str(tools/'cargo'),'Rust_RESOLVE_RUSTUP_TOOLCHAINS':'OFF'},False,0),
  ('resolve-on',{'NODE_COMPAT_PREINSTALLED_RUST':'ON','Rust_COMPILER':str(tools/'rustc'),'Rust_CARGO':str(tools/'cargo'),'Rust_RESOLVE_RUSTUP_TOOLCHAINS':'ON'},False,0),
  ('resolve-absent',{'NODE_COMPAT_PREINSTALLED_RUST':'ON','Rust_COMPILER':str(tools/'rustc'),'Rust_CARGO':str(tools/'cargo')},False,0)]:
  prefix='''cmake_minimum_required(VERSION 3.27)
function(execute_process)
set_property(GLOBAL APPEND PROPERTY RECORDED_COMMANDS "${ARGV}")
endfunction()
function(CPMAddPackage)
set_property(GLOBAL PROPERTY CPM_CALLED TRUE)
endfunction()
set(Rust_CARGO_HOST_ARCH aarch64)
'''
  prefix+=''.join('set('+k+' "'+v+'")\n'for k,v in settings.items())
  suffix='''
get_property(commands GLOBAL PROPERTY RECORDED_COMMANDS)
get_property(cpm GLOBAL PROPERTY CPM_CALLED)
if(NOT cpm)
 message(FATAL_ERROR "real CPM seam lost")
endif()
'''
  if name=='direct-on':suffix+='''if(DEFINED Rust_TOOLCHAIN OR DEFINED CACHE{Rust_TOOLCHAIN} OR DEFINED Rust_RUSTUP OR DEFINED CACHE{Rust_RUSTUP} OR NOT NODE_COMPAT_PREINSTALLED_RUST_CHANNEL STREQUAL "1.88.0" OR commands)
 message(FATAL_ERROR "direct branch leaked toolchain/setup")
endif()
'''
  elif ok:suffix+='''if(NOT commands STREQUAL "COMMAND;rustup;toolchain;install;1.88.0;COMMAND;rustup;target;add;--toolchain;1.88.0;wasm32-wasip1")
 message(FATAL_ERROR "default setup changed: ${commands}")
endif()
'''
  script=t/(name+'.cmake');script.write_text(prefix+actual+suffix);r=subprocess.run([cmake,'-P',str(script)],cwd=t,capture_output=True,timeout=10)
  assert (r.returncode==0)==ok,(name,r.stdout,r.stderr);checks.append('actual CMake branch '+name);cmake_cases.append(dict(name=name,rawExitCode=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode(),expectedSetupCalls=calls,executeProcessStubOnly=True,compilerOrRustupInvoked=False))
# Command/environment rendering is pure: no selected binary is executed here.
model_trees={k:{'root':v['root'] or '/private/tmp/model-patched-sm'}for k,v in p['reusedTrees'].items()}
model_a=dict(reusedTrees=model_trees,cargo=dict(path=model_trees['rust']['root']+'/bin/cargo'),rustc=dict(path=model_trees['rust']['root']+'/bin/rustc'),intlLockfile=dict(path='/private/tmp/model84/Cargo.lock'))
model_p={**base,'cmakeFlags':{**base['cmakeFlags'],**p['cmakeAdditions']},'timeouts':p['timeouts']}
model_work=Path('/private/tmp/starling-node-compat/next-native-intl-build-model-only')
commands,flags=m.command_plan(model_a,model_p,model_work);env=m.environment(model_p,model_a,model_work)
check('fixed five commands before read-only harvest',lambda:None if [x[0]for x in commands]==['rust-version','cargo-version','rust-sysroot','configure','build']else (_ for _ in ()).throw(AssertionError()))
check('no rustup commands',lambda:None if all(Path(c[1][0]).name!='rustup'and 'toolchain'not in c[1]for c in commands)else (_ for _ in ()).throw(AssertionError()))
check('direct compilers passed to CMake',lambda:None if flags['Rust_COMPILER']==model_a['rustc']['path']and flags['Rust_CARGO']==model_a['cargo']['path']else (_ for _ in ()).throw(AssertionError()))
check('private OpenSSL only',lambda:None if flags['CPM_OpenSSL_SOURCE'].startswith(str(model_work)+'/private-openssl/')else (_ for _ in ()).throw(AssertionError()))
for key in ['CARGO_BUILD_JOBS','CARGO_INCREMENTAL','CCACHE_DISABLE','SCCACHE_DISABLE','CARGO_NET_OFFLINE','CARGO_NET_GIT_FETCH_WITH_CLI']:
 check('environment '+key,lambda key=key:None if env[key]=={'CARGO_BUILD_JOBS':'1','CARGO_INCREMENTAL':'0','CCACHE_DISABLE':'1','SCCACHE_DISABLE':'1','CARGO_NET_OFFLINE':'true','CARGO_NET_GIT_FETCH_WITH_CLI':'false'}[key]else (_ for _ in ()).throw(AssertionError()))
check('HOME inherited',lambda:None if env.get('HOME')==os.environ.get('HOME')else (_ for _ in ()).throw(AssertionError()))
check('no rustup environment',lambda:None if not any(k.startswith('RUSTUP_')for k in env)else (_ for _ in ()).throw(AssertionError()))
check('fresh outputs',lambda:None if all(env[k].startswith(str(model_work)+'/')for k in ['CARGO_HOME','CARGO_TARGET_DIR','TMPDIR','CPM_SOURCE_CACHE'])else (_ for _ in ()).throw(AssertionError()))
check('unchanged base CMake policies',lambda:None if all(flags[k]==v for k,v in base['cmakeFlags'].items())else (_ for _ in ()).throw(AssertionError()))
check('no eager operational top-level',lambda:None if all(not isinstance(n,ast.Expr)or not isinstance(n.value,ast.Call)for n in ast.parse(source).body)else (_ for _ in ()).throw(AssertionError()))
m.checked(next(x['executable']for x in base['hostTools']if x['name']=='cmake'))
result=dict(sourceInputs=[m.descriptor(HERE/n)for n in ['run.py','plan.json','test-source.py','after/cmake/init-corrosion.cmake']],schemaVersion=1,state='NEXT_INTL_NATIVE_BUILD_CALLER_SOURCE_MODELS_PASSED_V4',checks=len(checks),caseNames=checks,cmakeExecutable=next(x['executable']for x in base['hostTools']if x['name']=='cmake'),cmakeDecisionCases=cmake_cases,actualBuildOrConfigureInvoked=False,actualRustupOrCargoInvoked=False,operationalSourceTreeCopied=False,engineOrGuestInvoked=False,wholeSharedToolTreesAuthenticated=False,operationalInputsRemainUnissued=True)
print(json.dumps(result,indent=2))
