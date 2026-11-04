#!/usr/bin/env python3
"""Approved isolated Release SDK syntax ONLY. Never builds an engine or invokes a guest."""
from pathlib import Path
import hashlib,json,shlex,subprocess
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PACKET=HERE.parent/'taskqueue-owner-v2'
FREEZE=Path('/tmp/starling-node-compat/foundations-v11/native-freeze')
ROOT=Path('/tmp/starling-node-compat/scheduler-taskqueue-v2-syntax-v1')
STAGE=ROOT/'stage'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p): return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def regular(p,root):
    assert p.is_file() and not p.is_symlink(),p
    for q in p.relative_to(root).parents:
        assert not (root/q).is_symlink(),p
assert sha(PACKET/'index.json')=='7d46543bc27bac3f7a1ff20b91446043fd15203283af4455b6a8425fc06f0f4a'
index=json.loads((PACKET/'index.json').read_text())
assert len(index['files'])==17
for item in index['files']:
    p=PACKET/item['path'];regular(p,PACKET);assert sha(p)==item['sha256'],p
meta_path=FREEZE/'off-foundations.engine.wasm.build.json'
meta=json.loads(meta_path.read_text());commands_path=FREEZE/'off-foundations-compile_commands.json'
assert meta['engineSha256']=='1eb2b55a391e2bc83478fefee124a6f282cfed148cc0623754125f6c5e9b0458'
assert sha(commands_path)==meta['compileCommandsSha256']
assert meta['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release'
assert meta['observedCMakeOptions']['NODE_COMPAT_GC_STRESS']=='OFF'
assert meta['observedCMakeOptions']['NODE_COMPAT_OOM_TESTING']=='OFF'
assert meta['observedCMakeOptions']['ENABLE_JS_DEBUGGER']=='OFF'
assert len(meta['sourceManifest'])==304
frozen=FREEZE/'source'
for item in meta['sourceManifest']:
    p=frozen/item['path'];regular(p,frozen);assert sha(p)==item['sha256'],p
manifest=[{'path':i['path'],'sha256':i['sha256']} for i in sorted(meta['sourceManifest'],key=lambda i:i['path'])]
assert hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()==json.loads((PACKET/'source-receipt.json').read_text())['expectedNativeInputListCanonicalSha256']
assert not ROOT.exists(),'Use a new versioned stage; never overwrite a prior syntax result'
STAGE.mkdir(parents=True)
base_paths=['runtime/event_loop.cpp','runtime/event_loop.h','runtime/engine.cpp','CMakeLists.txt','cmake/builtins.cmake','builtins/web/timers.h']
copies=[]
for name in base_paths:
    src=frozen/name;dst=STAGE/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
    copies.append({'source':pin(src),'stage':str(dst),'role':'exact frozen input before patch'})
componentize=FREEZE/'componentize-source'
for name in ['embedding/embedding.cpp','embedding/embedding.h']:
    src=componentize/name;regular(src,componentize)
    assert sha(src)==next(i['sha256'] for i in meta['componentizeSourceManifest'] if i['path']==name)
    dst=STAGE/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
    copies.append({'source':pin(src),'stage':str(dst),'role':'exact frozen embedding input before patch'})
patches=[]
for name in ['starling-taskqueue-ticks.UNAPPLIED.patch','componentize-taskqueue-ticks.UNAPPLIED.patch']:
    command=['git','apply',str(PACKET/name)]
    result=subprocess.run(command,cwd=STAGE,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    patches.append({'patch':pin(PACKET/name),'command':command,'cwd':str(STAGE),'status':result.returncode})
diag=STAGE/'test-extension.UNCOMPILED.cpp';diag.write_bytes((PACKET/'test-extension.UNCOMPILED.cpp').read_bytes())
copies.append({'source':pin(PACKET/'test-extension.UNCOMPILED.cpp'),'stage':str(diag),'role':'frozen diagnostic source, unchanged'})
for item in json.loads((PACKET/'source-receipt.json').read_text())['changedNativeFiles']:
    assert sha(STAGE/item['path'])==item['afterSha256'],item['path']
assert sha(STAGE/'embedding/embedding.cpp')==json.loads((PACKET/'source-receipt.json').read_text())['embeddingAfterSha256']
commands=json.loads(commands_path.read_text())
def entry(suffix): return next(i for i in commands if i['file'].endswith(suffix))
engine_entry=entry('/runtime/engine.cpp');loop_entry=entry('/runtime/event_loop.cpp')
embedding_command=meta['actualEmbeddingCompileCommands'][0]
sdk=Path(shlex.split(embedding_command)[0]);assert sdk.name=='clang++'
assert '/wasi-sdk/85e6/bin/' in str(sdk)
original_wrapper=Path(shlex.split(loop_entry['command'])[0])
assert str(sdk) in original_wrapper.read_text()
assert 'PATH=' in original_wrapper.read_text()

def syntax_args(command,source):
    words=shlex.split(command);args=[];i=1
    while i<len(words):
        v=words[i]
        if v in ['-o','-MF','-MT','-MQ']:
            i+=2;continue
        if v in ['-c','-MD','-MMD','-MP']:
            i+=1;continue
        if v.endswith('.cpp'):
            i+=1;continue
        if v.startswith('-I'+str(REPO)):
            v='-I'+str(frozen)+v[len('-I'+str(REPO)):]
        assert str(REPO) not in v,('unrewritten live-source flag',v)
        args.append(v);i+=1
    assert '-DNDEBUG' in args and '-O3' in args and '-Werror' in args
    assert not any(v.startswith('-DDEBUG') or v.startswith('-DNODE_COMPAT_OOM_TESTING') for v in args)
    # Only changed/new headers overlay the exact frozen unchanged include tree.
    overlays=['-I'+str(STAGE),'-I'+str(STAGE/'runtime'),'-I'+str(STAGE/'include')]
    return [str(sdk),*overlays,*args,'-DNODE_COMPAT_INTERNAL_TICKS=1','-fsyntax-only',str(source)]

cases=[
 ('queue','runtime/node_tick_queue.cpp',loop_entry['command'],'new runtime source inherits existing runtime flags'),
 ('event-loop','runtime/event_loop.cpp',loop_entry['command'],'patched exact runtime TU'),
 ('engine','runtime/engine.cpp',engine_entry['command'],'patched exact runtime TU'),
 ('embedding','embedding/embedding.cpp',embedding_command,'patched exact embedding TU'),
 ('diagnostic','test-extension.UNCOMPILED.cpp',embedding_command,'new builtin uses actual existing builtin/extension API flag baseline; not an observed future CMake command')]
records=[]
for label,source,base_command,qualification in cases:
    args=syntax_args(base_command,STAGE/source)
    (ROOT/(label+'.command.json')).write_text(json.dumps(args,indent=2)+'\n')
    result=subprocess.run(args,cwd=STAGE,capture_output=True,text=True)
    out=ROOT/(label+'.stdout.log');err=ROOT/(label+'.stderr.log')
    out.write_text(result.stdout);err.write_text(result.stderr)
    records.append({'label':label,'source':pin(STAGE/source),'baseCommand':base_command,
                    'qualification':qualification,'command':args,'cwd':str(STAGE),
                    'status':result.returncode,'stdout':pin(out),'stderr':pin(err)})
    print(json.dumps({'label':label,'status':result.returncode,'stderrBytes':err.stat().st_size}),flush=True)
for item in index['files']: assert sha(PACKET/item['path'])==item['sha256'],item['path']
assert sha(PACKET/'index.json')=='7d46543bc27bac3f7a1ff20b91446043fd15203283af4455b6a8425fc06f0f4a'
for item in meta['sourceManifest']:assert sha(frozen/item['path'])==item['sha256'],item['path']
record={'schemaVersion':1,'status':'isolated-Release-SDK-syntax-only',
 'allPassed':all(i['status']==0 for i in records),'basePacketIndex':pin(PACKET/'index.json'),
 'frozenOffReceipt':pin(meta_path),'frozenCompileCommands':pin(commands_path),
 'frozenEngineSha256ReferencedNotExecuted':meta['engineSha256'],'frozenNativeInputsCheckedBeforeAndAfter':304,
 'compiler':pin(sdk),'compilerVersion':subprocess.check_output([str(sdk),'--version'],text=True),
 'originalRuntimeWrapper':pin(original_wrapper),
 'wrapperSubstitution':'direct same SDK compiler; original wrapper only prepends scripts to PATH for linker wasm-opt, irrelevant to fsyntax-only',
 'flags':'actual frozen Release/Werror/target flags retained; output/dependency/compile-mode flags removed; private macro ON; staged headers first, unchanged include roots rewritten to immutable v11 freeze',
 'sourceCopies':copies,'patches':patches,'stagedFiles':[pin(f) for f in sorted(STAGE.rglob('*')) if f.is_file()],
 'results':records,'oldV2PacketAll17FilesAndIndexByteIdentical':True,
 'diagnosticKnownLimitation':'v2 scheduleTask same-realm check missing; no cross-realm execution; reviewed v3 same-realm guard required before any guest',
 'resetSafeReuse':'OPEN; no cancellation/reset proof','sourceTreeCopied':False,
 'engineBuilt':False,'guestExecuted':False,'debugOrFaultTesting':False,'liveSourceApplied':False}
(ROOT/'results.json').write_text(json.dumps(record,indent=2)+'\n')
(HERE/'results.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'allPassed':record['allPassed'],'results':str(ROOT/'results.json'),'receiptSha256':sha(HERE/'results.json')}))
