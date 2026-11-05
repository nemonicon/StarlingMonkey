"""Extract only named pure/injected definitions; no complete controller import."""
from pathlib import Path
import ast,copy,json,re,types
HERE=Path(__file__).resolve().parent
code=(HERE/'controller.py').read_text();tree=ast.parse(code);checks=[]
names={'native_argv','tokens','full_wit_observations','clean_terminal','collect_terminal','write'}
defs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names]
assert {n.name for n in defs}==names
scope={'Path':Path,'re':re,'json':json}
exec(compile(ast.Module(body=defs,type_ignores=[]),'<extracted-pure-and-injected-only>','exec'),scope)
def test(value,name):assert value,name;checks.append(name)
def refuses(fn,name):
    try:fn()
    except (AssertionError,ValueError,UnicodeDecodeError,FileExistsError,OSError):checks.append(name)
    else:raise AssertionError('Expected refusal: '+name)
refs=json.loads((HERE/'references.json').read_text());expected=refs['expectedWitDeclarations']
bodies={
 'wasi:io/error@0.2.0':'resource error;',
 'wasi:io/poll@0.2.0':'resource pollable;',
 'wasi:io/streams@0.2.0':'use error.{error};use poll.{pollable};resource input-stream;resource output-stream;',
 'wasi:cli/stdin@0.2.0':'use wasi:io/streams@0.2.0.{input-stream};',
 'wasi:cli/stdout@0.2.0':'use wasi:io/streams@0.2.0.{output-stream};',
 'wasi:cli/stderr@0.2.0':'use wasi:io/streams@0.2.0.{output-stream};',
 'wasi:clocks/monotonic-clock@0.2.0':'use wasi:io/poll@0.2.0.{pollable};',
}
def pkg_body(package):
    prefix,version=package.split('@');parts=[]
    for key in expected['declarations']:
        if key.startswith(prefix+'/')and key.endswith('@'+version):
            name=key.split('/')[1].split('@')[0];kind='world'if name=='imports'else'interface'
            parts.append(kind+' '+name+' {'+bodies.get(key,'')+'}')
    return '\n'.join(parts)
fixture=('package wasi:cli@0.2.0;\n'+pkg_body('wasi:cli@0.2.0')+'\n'+'\n'.join('package '+p+' {'+pkg_body(p)+'}'for p in expected['packages']if p!='wasi:cli@0.2.0')).encode()
observe=scope['full_wit_observations'];model=observe(fixture,expected)
test(model['packages']==expected['packages']and len(model['declarations'])==28,'All six package/28 declaration lexical model')
test(len(model['observedResourceAliasClauses'])==10,'Ten bounded resource/alias observations')
test(observe(b'// package fake:x@0.2.0;\n/*outer /* nested */ comment */\n'+fixture,expected)['packages']==expected['packages'],'Comments do not invent declarations')
for fragment in [b'package wasi:io@0.2.0',b'interface stdout',b'resource pollable',b'resource input-stream',b'resource output-stream',b'use error.{error}',b'use poll.{pollable}',b'use wasi:io/streams@0.2.0.{input-stream}',b'use wasi:io/poll@0.2.0.{pollable}']:
    refuses(lambda f=fragment:observe(fixture.replace(f,f.replace(b'i',b'x',1)if b'i'in f else b'changed'),expected),'Missing/changed '+fragment.decode())
for raw,name in [(b'','Empty'),(fixture[:-1],'Unclosed package'),(fixture+b'package wasi:io@0.2.0 {}','Duplicate package'),(fixture+b'interface extra {}','Extra declaration'),(fixture+b'\x1b','ANSI'),(fixture+b'\0','NUL'),(fixture+b'\xff','Invalid UTF8'),(fixture+b'/*','Unclosed comment')]:
    refuses(lambda b=raw:observe(b,expected),name+' refuses')
argv=scope['native_argv'](refs)
test(argv==[refs['wasmTools']['path'],'component','wit',refs['metadataPayload']['path']],'One native package-aware exact argv; no rewriting/selecting flags')
test(not any(s in argv for s in ['--importize','--world','--out-dir','--json','--no-docs']),'Default complete nested-package WIT renderer')
authority={'path':'/SYNTHETIC/root','sha256':'a'*64,'bytes':1}
terminal=dict(rawExitCode=0,authority=authority,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,timeout=False,forcedCleanup=False,errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[],finalGroups=[dict(alive=False)],stderr=dict(bytes=0))
scope['clean_terminal'](terminal,authority);checks.append('Clean owned terminal accepted')
for key,value in [('rawExitCode',1),('rawExitCode',None),('parentOwnedGroupGone',False),('allObservedOwnedGroupsGone',False),('timeout',True),('forcedCleanup',True),('errors',['x']),('signals',['SIGTERM']),('interruptedSignals',['SIGINT']),('remainingObservedPids',[1]),('finalGroups',[dict(alive=True)]),('stderr',dict(bytes=1)),('authority',{})]:
    t=copy.deepcopy(terminal);t[key]=value;refuses(lambda:scope['clean_terminal'](t,authority),'Terminal refuses '+key+'='+str(value))
class FakeCapture:
    def __init__(self,t):self.t=t;self.calls=[]
    def read(self,r):self.calls.append(('read',r));return self.t
    def file(self,r):self.calls.append(('file',r));return r
t=copy.deepcopy(terminal);t['stdout']=dict(path='/SYNTHETIC/stdout',sha256='b'*64,bytes=7);t['stderr']=dict(path='/SYNTHETIC/stderr',sha256='c'*64,bytes=0)
c=FakeCapture(t);r={'path':'/SYNTHETIC/terminal','sha256':'d'*64,'bytes':9};ob=scope['collect_terminal'](c,r,t)
test(c.calls==[('read',r),('file',t['stdout']),('file',t['stderr'])]and ob['rawExitCode']==0,'Whole terminal equality then both raw streams before acceptance')
refuses(lambda:scope['collect_terminal'](FakeCapture({}),r,t),'Whole returned terminal mismatch refuses')
# Genuine extracted writer with only injected, non-filesystem OS/stream objects.
for failure in [None,'open','fdopen','dump','flush','fsync']:
    events=[]
    class FakeStream:
        def __enter__(self):return self
        def __exit__(self,*a):events.append('stream-context-exit')
        def write(self,s):events.append('write')
        def flush(self):
            events.append('flush')
            if failure=='flush':raise OSError('injected flush')
        def fileno(self):return 37
    def open_file(path,flags,mode):
        events.append(('open',str(path),flags,mode))
        if failure=='open':raise FileExistsError('exclusive existing target')
        return 37
    def fdopen(fd,*args,**kwargs):
        events.append(('fdopen',fd,kwargs));assert kwargs=={'closefd':False}
        if failure=='fdopen':raise OSError('injected fdopen')
        return FakeStream()
    def dump(*args,**kwargs):
        events.append('dump')
        if failure=='dump':raise OSError('injected dump')
    def fsync(fd):
        events.append(('fsync',fd))
        if failure=='fsync':raise OSError('injected fsync')
    scope['os']=types.SimpleNamespace(open=open_file,fdopen=fdopen,close=lambda fd:events.append(('close',fd)),fsync=fsync,O_WRONLY=1,O_CREAT=2,O_EXCL=4,O_NOFOLLOW=8)
    scope['json']=types.SimpleNamespace(dump=dump);scope['fingerprint']=lambda p:('synthetic-row',None,None)
    if failure is None:test(scope['write']('/SYNTHETIC/output',{})=='synthetic-row','Injected genuine writer success only after fsync')
    else:refuses(lambda:scope['write']('/SYNTHETIC/output',{}),'Injected genuine writer '+failure+' refuses')
    test(events.count(('close',37))==(0 if failure=='open'else 1),'Writer '+str(failure)+' exact acquired-fd close')
    test(events[0]==('open','/SYNTHETIC/output',15,0o600),'Writer '+str(failure)+' private exclusive nofollow')
test(code.index('for r in inputs[\'files\']:c.file(r)')<code.index("    check_failed_phase(c,refs)\n")<code.index("monitor=load_actual(refs['monitor']"),'Full Source/dependency/failure-proof authentication before only custom import')
test("for p in [out,external]:assert not p.exists()and not p.is_symlink()"in code,'Both fresh roots mandatory')
test("normalizerOrPrunerRerun=False,nodeValidationRerun=False"in code and "previousPhasePassed=False"in code,'Old failed phase retained; no prior action repeated')
test(code.count('monitor.monitor(')==1 and 'prune-clock-adapter-io'not in code and 'WebAssembly'not in code,'One owned native metadata action seam only')
test("finally:frame['c'].recheck()"in code and 'finalProtectionError=protection_error'in code,'Final/failure protection determines refusal')
for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
result=dict(schemaVersion=1,state='PURE_EXTRACTED_METADATA_CONTINUATION_SOURCE_MODELS_PASSED_V1',checks=len(checks),checkNames=checks,syntheticObservationModelsNotWitSemanticProof=True,actualControllerImported=False,actualToolExecuted=False,actualDecoderExecuted=False,filesystemWriterInvoked=False,rootAction=None)
(HERE/'pure-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),actualActions=0)))
