"""Actual SDK syntax-only proof in an owned proposal tree; never a link/build."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import os
import shlex
import subprocess
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
CANDIDATE=HERE.parent/'implementation-candidate-v1'
AMENDMENT=HERE.parent/'implementation-candidate-v1-allocation-order-amendment'
FREEZE=Path('/tmp/starling-node-compat/production-scheduler-artifacts-v1/native-freeze')
WORK=Path('/tmp/starling-node-compat/classic-syntax-v1')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(path,expected):
    path=Path(path);assert path.is_file() and not path.is_symlink(),path
    assert sha(path)==expected,path
    return path
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as out:out.write(data)
def main():
    if not __debug__:raise RuntimeError('Validation requires assertions')
    assert not WORK.exists(),'Fresh owned output required'
    require(CANDIDATE/'index.json','743037e278438d7947c871f17b8b9195dc26088ddc054a2293d1e6c4ef2f72f8')
    require(AMENDMENT/'index.json','f723d0c997bb59bfcbbe6f82fcc5797ab45e82fa7ac416bd8367d4f73fd0db72')
    for base in [CANDIDATE,AMENDMENT]:
        for row in json.loads((base/'index.json').read_bytes())['files']:require(base/row['path'],row['sha256'])
    amendment=json.loads((AMENDMENT/'source-receipt.json').read_bytes())
    require(AMENDMENT/'native-integration.corrected.UNAPPLIED.patch','0574b88e1126e616e4adaac2d7dea4435657c70e2d07a429531218aff24bd73c')
    receipt=json.loads((FREEZE/'normal-off-freeze-receipt.json').read_bytes())
    metadata_path=require(FREEZE/'normal-off.engine.wasm.build.json',receipt['receiptSha256'])
    metadata=json.loads(metadata_path.read_bytes())
    assert metadata['buildRecipeSha256']=='869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'
    assert metadata.get('diagnosticOnly',False) is False and 'internalTickDiagnosticPolicy'not in metadata
    assert metadata['entropyPolicy']=='off' and metadata['gcStress'] is False
    assert len(metadata['sourceManifest'])==306
    for row in metadata['sourceManifest']:
        require(FREEZE/'source'/row['path'],row['sha256']);require(REPO/row['path'],row['sha256'])
    db_path=require(FREEZE/'normal-off-compile_commands.json',metadata['compileCommandsSha256'])
    cache_path=require(FREEZE/'normal-off-CMakeCache.txt',metadata['cmakeCacheSha256'])
    rows=[row for row in json.loads(db_path.read_bytes())if row['file']==str(REPO/'builtins/node-compat/register.cpp')]
    assert len(rows)==1;row=rows[0];base_args=shlex.split(row['command'])
    assert '-O3'in base_args and '-DNDEBUG'in base_args and '-flto=thin'in base_args
    for flag in ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_EVENTS','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_STRING_DECODER']:
        assert '-D'+flag+'=1'in base_args
    assert not any('NODE_COMPAT_CLASSIC_STREAMS'in word for word in base_args)
    assert '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1'not in base_args
    mapping=json.loads((CANDIDATE/'integration/new-files.json').read_bytes())['files']
    assert len(mapping)==len({item['proposedPath']for item in mapping})==36
    proposal=WORK/'proposal-root';source_rows=[]
    for item in mapping:
        source=require(CANDIDATE/item['candidatePath'],item['sha256']);destination=proposal/item['proposedPath']
        write(destination,source.read_bytes());source_rows.append({'path':str(destination.relative_to(proposal)),'sha256':sha(destination)})
    register=proposal/'builtins/node-compat/register.cpp'
    write(register,require(AMENDMENT/'register.cpp',amendment['correctedRegistrySha256']).read_bytes())
    cmake=CANDIDATE/'integration/cmake/builtins.cmake'
    write(proposal/'cmake/builtins.cmake',cmake.read_bytes())
    assert len(list(proposal.rglob('*.*')))==38
    args=[];index=0
    while index<len(base_args):
        if base_args[index]in('-c','-o'):
            assert index+1<len(base_args);index+=2
        else:args.append(base_args[index]);index+=1
    # Retain every original include. The extra frozen fallback resolves the
    # existing adjacent factory/event headers from this new source directory.
    args[1:1]=['-I'+str(proposal),'-I'+str(FREEZE/'source/builtins/node-compat')]
    args+=['-DNODE_COMPAT_CLASSIC_STREAMS=1','-fsyntax-only','-MD','-MF',str(WORK/'headers.d'),'-MT','classic-register-syntax',str(register)]
    assert '-c'not in args and '-o'not in args
    wrapper=Path(base_args[0]);wrapper_hash=sha(wrapper)
    sdk=Path('/tmp/starling-node-compat/improved-build/cache/wasi-sdk/85e6')
    compiler=(sdk/'bin/clang++').resolve(strict=True)
    assert str(sdk/'bin/clang++')in wrapper.read_text()
    compiler_hash=sha(compiler)
    sm=Path('/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include')
    sm_header=sm/'js-confdefs.h';sm_header_hash=sha(sm_header)
    assert metadata['archivePins']['spiderMonkeySha256']=='c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b'
    version=(sdk/'VERSION').read_text();assert '30.0\n'in version and 'llvm-version: 21.1.4'in version
    write(WORK/'command.json',json.dumps({'argv':args,'cwd':row['directory'],'base':row},indent=2).encode()+b'\n')
    process=subprocess.run(args,cwd=row['directory'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    write(WORK/'stdout.txt',process.stdout);write(WORK/'stderr.txt',process.stderr)
    headers=[]
    if (WORK/'headers.d').exists():
        raw=(WORK/'headers.d').read_text().replace('\\\n',' ')
        names=shlex.split(raw.split(':',1)[1])
        for name in sorted(set(names)):
            path=Path(name);path=path if path.is_absolute()else Path(row['directory'])/path
            assert path.is_file();headers.append({'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size})
    assert sha(wrapper)==wrapper_hash and sha(compiler)==compiler_hash and sha(sm_header)==sm_header_hash
    for item in metadata['sourceManifest']:require(REPO/item['path'],item['sha256'])
    assert not list(WORK.rglob('*.obj'))and not list(WORK.rglob('*.o'))and not list(WORK.rglob('*.wasm'))
    result={'schemaVersion':1,'state':'ACTUAL_SDK_CLASSIC_REGISTRATION_SYNTAX_PASSED'if process.returncode==0 else'ACTUAL_SDK_CLASSIC_REGISTRATION_SYNTAX_FAILED',
        'observedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':process.returncode,'command':args,'cwd':row['directory'],
        'baseFrozenMetadata':{'path':str(metadata_path),'sha256':sha(metadata_path),'engineSha256':metadata['engineSha256'],'sourceInputs':306},
        'baseFrozenCommands':{'path':str(db_path),'sha256':sha(db_path)},'baseFrozenCache':{'path':str(cache_path),'sha256':sha(cache_path)},
        'proposalRoot':str(proposal),'mappedNewFiles':36,'replacementFiles':2,'correctedRegistrySha256':sha(register),
        'correctedPatchSha256':sha(AMENDMENT/'native-integration.corrected.UNAPPLIED.patch'),
        'wrapper':{'path':str(wrapper),'sha256':wrapper_hash},'sdk':{'version':version,'compilerInvokedPath':str(sdk/'bin/clang++'),'compilerCanonicalPath':str(compiler),'sha256':compiler_hash},
        'spiderMonkey':{'tag':'FIREFOX_147_0_4_RELEASE_STARLING','archiveSha256':metadata['archivePins']['spiderMonkeySha256'],'jsConfdefs':{'path':str(sm_header),'sha256':sm_header_hash}},
        'headers':headers,'stdoutPath':str(WORK/'stdout.txt'),'stdoutSha256':sha(WORK/'stdout.txt'),'stderrPath':str(WORK/'stderr.txt'),'stderrSha256':sha(WORK/'stderr.txt'),
        'originalIncludesRetained':True,'addedIncludes':[str(proposal),str(FREEZE/'source/builtins/node-compat')],
        'flagsAdded':['NODE_COMPAT_CLASSIC_STREAMS=1'],'syntaxOnly':True,'compilerExecuted':True,'objectGenerated':False,'linkerExecuted':False,
        'fullNativeBuildExecuted':False,'guestExecuted':False,'faultTestingExecuted':False,'liveNativeSourceFilesChanged':False,'engineMetadataModified':False}
    write(WORK/'results.json',json.dumps(result,indent=2).encode()+b'\n')
    print(json.dumps({'state':result['state'],'exitCode':process.returncode,'headers':len(headers),'result':str(WORK/'results.json')}))
    return process.returncode

if __name__=='__main__':sys.exit(main())
