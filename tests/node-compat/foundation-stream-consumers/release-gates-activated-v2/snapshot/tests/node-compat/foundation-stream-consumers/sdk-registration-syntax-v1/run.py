"""Authorized two-command SDK frontend check only; no linking, engine or JS execution."""
from pathlib import Path
import difflib
import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
SOURCE=HERE.parent/'production-text-json-candidate-v2'
PEER=HERE.parent/'independent-production-text-json-v2-source-review-v1'
FROZEN=Path('/tmp/starling-node-compat/production-zlib-v4/native-freeze')
OUTPUT=Path('/tmp/starling-node-compat/consumers-sdk-registration-syntax-v1')
SDK=Path('/tmp/starling-node-compat/zlib-v4-build/cache/wasi-sdk/85e6')
SOURCE_SHA='eedeef581d961030b9aac3bf87c43e0f58cfe5516c5b04d997eb095c6df7ef7a'
PEER_SHA='01f432678d2408d7645d35afea5abd73f192206c6dd3d4197f4ad7a83a0ad9d1'
METADATA_SHA='59942584d9aed799776913f158904abf6b4beb8feac04b56f28a813dfdced46e'
FREEZE_SHA='e5e705c886392bc5db137581b3492d72080e101460ec670f27281a1dbd964f11'
seen={}

def sha(value):return hashlib.sha256(value).hexdigest()
def data(path):
    path=Path(path);before=path.stat();value=path.read_bytes();after=path.stat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),path
    row={'path':str(path),'realpath':str(path.resolve()),'bytes':len(value),'sha256':sha(value),'symlink':path.is_symlink()}
    key=str(path.resolve())
    if key in seen:assert seen[key]['sha256']==row['sha256'] and seen[key]['bytes']==row['bytes'],path
    else:seen[key]=row
    return value
def describe(path):data(path);return dict(seen[str(Path(path).resolve())])
def load(path):return json.loads(data(path))
def dump(path,value):
    with Path(path).open('x') as output:json.dump(value,output,indent=2);output.write('\n')
def indexed(root,digest):
    value=data(root/'index.json');assert sha(value)==digest
    result=json.loads(value)
    for row in result['files']:
        path=root/row['path'];assert not path.is_symlink()
        value=data(path);assert len(value)==row['bytes'] and sha(value)==row['sha256']
    return result

def main():
    free=shutil.disk_usage('/tmp/starling-node-compat').free
    assert free>=2*1024**3,'Initial2GiB frontend-check capacity guard'
    assert not OUTPUT.exists(),'Fresh output only'
    source_index=indexed(SOURCE,SOURCE_SHA);peer_index=indexed(PEER,PEER_SHA)
    assert len(source_index['files'])==39 and len(peer_index['files'])==3
    assert sha(data(FROZEN/'normal-off-freeze-receipt.json'))==FREEZE_SHA
    freeze=load(FROZEN/'normal-off-freeze-receipt.json')
    assert sha(data(FROZEN/'normal-off.engine.wasm.build.json'))==METADATA_SHA
    metadata=load(FROZEN/'normal-off.engine.wasm.build.json')
    db_path=FROZEN/'normal-off-compile_commands.json'
    assert sha(data(db_path))==metadata['compileCommandsSha256']
    entries=load(db_path)
    rows=[row for row in entries if row['file'].endswith('/builtins/node-compat/register.cpp')]
    assert len(rows)==1;row=rows[0];original=shlex.split(row['command'])
    assert len(original)==50 and metadata['actualRegistrationCompileCommands']==[row['command']]
    assert freeze['state']=='immutable-zlib-release-engine-frozen' and freeze['nativeInputsVerified']==350
    assert metadata['oomTesting'] is False and metadata['gcStress'] is False
    assert '-O3' in original and '-DNDEBUG' in original and '-flto=thin' in original and '--target=wasm32-wasi' in original
    assert not any(x.startswith(('-DDEBUG','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_STREAM_CONSUMERS')) for x in original)
    configured=Path(row['file']).parents[2]
    assert configured.resolve()==Path('/tmp/starling-node-compat/zlib-source-v4').resolve()
    for native in metadata['sourceManifest']:
        assert sha(data(configured/native['path']))==native['sha256']
        assert sha(data(FROZEN/'source'/native['path']))==native['sha256']
    native_derivations=load(SOURCE/'native-derivations.json')
    proposed_paths=native_derivations['addedSources']+[x['path'] for x in native_derivations['changes']]
    assert len(proposed_paths)==7
    proposed_rows={x['path']:x['sha256'] for x in load(SOURCE/'expected-native-source-manifest.json')}
    for path in proposed_paths:assert sha(data(SOURCE/'proposed'/path))==proposed_rows[path]
    binary=SDK/'bin/clang++';wrapper=Path(original[0])
    expected_wrapper='#!/usr/bin/env bash\n\n# Clang doesn\'t support overriding where wasm-opt is found, and CMake doesn\'t allow overriding\n# $PATH for linker/compiler invocations. So we use this script to modify $PATH, and\n# scripts/wasm-opt to hide the real wasm-opt from clang.\nPATH="'+str(configured)+'/scripts:$PATH" '+str(binary)+' "$@"\n'
    assert data(wrapper).decode()==expected_wrapper
    compiler_before=describe(binary);wrapper_before=describe(wrapper)
    version_file=data(SDK/'VERSION').decode()
    assert 'llvm-version: 21.1.4' in version_file and metadata['wasiSdkVersionFiles'][0]['contents']==version_file
    for header in metadata['zlibSelectedCodecInput']['headers']:
        assert sha(data(header['path']))==header['sha256']
    base=[];removed=[];i=1
    while i<len(original):
        arg=original[i]
        if arg in ('-c','-o','-MF','-MT','-MQ','-MJ'):
            removed.append(original[i:i+2]);i+=2;continue
        if arg in ('-MD','-MMD','-MP','-MG','-M','-MM'):
            removed.append([arg]);i+=1;continue
        base.append(arg);i+=1
    assert removed==[['-o','starling-raw.wasm/CMakeFiles/builtin_node_compat.dir/builtins/node-compat/register.cpp.obj'],['-c',str(configured/'builtins/node-compat/register.cpp')]]
    assert base==[x for j,x in enumerate(original) if j not in {0,46,47,48,49}]
    # Snapshot candidate include files before the actual two checks. Afterwards
    # retain the compiler's actual selected dependency subset with equal hashes.
    include_roots=[SDK/'share/wasi-sysroot/include',SDK/'lib/clang/21/include']
    include_roots += [Path(x[2:]) for x in base if x.startswith('-I')]
    include_roots += [SOURCE/'proposed/builtins/node-compat',configured/'builtins/node-compat']
    excluded_include_roots=[]
    for root in include_roots:
        if not root.is_dir():excluded_include_roots.append(str(root));continue
        for path in sorted(root.rglob('*')):
            if path.is_file() and '.git' not in path.relative_to(root).parts and path.suffix in ('','.h','.hpp','.inc','.def'):
                data(path)
    input_snapshot={key:dict(value) for key,value in seen.items()}
    OUTPUT.mkdir()
    env=dict(os.environ)
    scrub=['CPATH','CPLUS_INCLUDE_PATH','C_INCLUDE_PATH','OBJC_INCLUDE_PATH','COMPILER_PATH','LIBRARY_PATH','SDKROOT','GCC_EXEC_PREFIX','CCC_OVERRIDE_OPTIONS','CFLAGS','CXXFLAGS','LDFLAGS']
    for key in scrub:env.pop(key,None)
    version=subprocess.run([str(binary),'--version'],cwd=OUTPUT,env=env,text=True,capture_output=True,timeout=30)
    (OUTPUT/'compiler-version.stdout.log').write_text(version.stdout);(OUTPUT/'compiler-version.stderr.log').write_text(version.stderr)
    assert version.returncode==0 and '21.1.4' in version.stdout
    dump(OUTPUT/'inputs-before.json',{'files':list(input_snapshot.values()),'missingOriginalIncludeRoots':excluded_include_roots})
    commands=[]
    candidate=SOURCE/'proposed/builtins/node-compat/register.cpp'
    for enabled in [True,False]:
        label='on' if enabled else 'off'
        dep=OUTPUT/(label+'.d')
        added=['-I'+str(SOURCE/'proposed/builtins/node-compat'),'-I'+str(configured/'builtins/node-compat')]
        if enabled:added.append('-DNODE_COMPAT_STREAM_CONSUMERS=1')
        added += ['-fsyntax-only','-MD','-MF',str(dep),'-MT','consumer-registration-'+label,str(candidate)]
        argv=[str(binary)]+base+added
        assert '-o' not in argv and '-c' not in argv and '--target=wasm32-wasi' in argv
        assert argv.count('-DNODE_COMPAT_STREAM_CONSUMERS=1')==int(enabled)
        record={'label':label,'consumerFlag':enabled,'originalArgv':original,'derivedArgv':argv,'removedArgvGroups':removed,'addedArgv':added,'cwd':str(OUTPUT),'wrapperBypassed':True,'sameSdkCompiler':str(binary),'syntaxOnly':True,'oldObjectWritten':False}
        dump(OUTPUT/(label+'-command.json'),record)
        start=time.monotonic();timed_out=False
        with (OUTPUT/(label+'.stdout.log')).open('xb') as out,(OUTPUT/(label+'.stderr.log')).open('xb') as err:
            child=subprocess.Popen(argv,cwd=OUTPUT,env=env,stdout=out,stderr=err,start_new_session=True)
            try:status=child.wait(timeout=600)
            except subprocess.TimeoutExpired:
                timed_out=True
                try:os.killpg(child.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                status=child.wait(timeout=10)
        record.update({'returncode':status,'signal':-status if status<0 else None,'timedOut':timed_out,'elapsedSeconds':time.monotonic()-start,'stdout':describe(OUTPUT/(label+'.stdout.log')),'stderr':describe(OUTPUT/(label+'.stderr.log'))})
        dump(OUTPUT/(label+'-terminal.json'),record)
        commands.append(record)
        if status!=0:
            dump(OUTPUT/'results.json',{'state':'CONSUMER_REGISTRATION_SDK_SYNTAX_FAILED','commands':commands,'nativeBuildOrGuestExecuted':False})
            raise SystemExit('Meaningful frontend failure preserved; stop before further commands/source changes')
        assert dep.is_file()
    dependencies=[]
    for label in ['on','off']:
        text=data(OUTPUT/(label+'.d')).decode().replace('\\\n',' ')
        target,body=text.split(':',1);assert target=='consumer-registration-'+label
        selected=[]
        for token in shlex.split(body):
            path=Path(token);path=path if path.is_absolute() else OUTPUT/path
            key=str(path.resolve());assert key in input_snapshot,'Actual include absent from before snapshot: '+str(path)
            now=describe(path);assert now['sha256']==input_snapshot[key]['sha256'] and now['bytes']==input_snapshot[key]['bytes']
            selected.append(now)
        dependencies.append({'label':label,'dependencyFile':describe(OUTPUT/(label+'.d')),'count':len(selected),'files':selected})
    for key,value in input_snapshot.items():
        after=describe(value['path']);assert after['sha256']==value['sha256'] and after['bytes']==value['bytes']
    assert describe(binary)['sha256']==compiler_before['sha256'] and describe(wrapper)['sha256']==wrapper_before['sha256']
    dump(OUTPUT/'dependencies.json',{'actualSelectedInputs':dependencies,'allBeforeInputsUnchanged':True})
    result={'schemaVersion':1,'state':'CONSUMER355_REGISTRATION_SDK_FRONTEND_ON_OFF_PASSED','sourceIndexSha256':SOURCE_SHA,'sourcePeerIndexSha256':PEER_SHA,
      'metadataSha256':METADATA_SHA,'freezeReceiptSha256':FREEZE_SHA,'compileDatabase':describe(db_path),'compiler':compiler_before,'wrapper':wrapper_before,
      'wrapperValidation':'Exact captured single SDK invocation; sole difference is scripts PATH for linker discovery. Bypassed for syntax only.','compilerVersion':version.stdout,
      'target':'wasm32-wasi','originalArgc':len(original),'commands':commands,'sourceInputsAuthenticated':350,'proposedNativeAfterimagesAuthenticated':7,
      'dependencyCounts':{x['label']:x['count'] for x in dependencies},'prehashedInputs':len(input_snapshot),'allInputBytesStableAfter':True,
      'initialFreeBytes':free,'finalFreeBytes':shutil.disk_usage('/tmp/starling-node-compat').free,'environmentVariablesRemoved':scrub,
      'scope':'SDK30/LLVM21.1.4 C++ registration and included generated-header frontend API check ONLY. No355 configure/build/link/install, JS factory, codec, guest/host, runtime admission or performance proof.'}
    dump(OUTPUT/'results.json',result)
    print(json.dumps({k:result[k] for k in ['state','originalArgc','dependencyCounts','prehashedInputs','sourceIndexSha256']}))

if __name__=='__main__':main()
