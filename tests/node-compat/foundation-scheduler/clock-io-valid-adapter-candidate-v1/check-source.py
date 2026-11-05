"""Source/pure synthetic ownership models. No original module or pruner runs."""
from pathlib import Path,PurePosixPath
import ast,copy,hashlib,json,stat,types
HERE=Path(__file__).resolve().parent;refs=json.loads((HERE/'references.json').read_text());checks=[]
def check(v,n):assert v,n;checks.append(n)
def refuses(fn,n):
    try:fn()
    except(AssertionError,ValueError,TypeError,KeyError,OSError):checks.append(n);return
    raise AssertionError('Expected refusal '+n)
# Own decoder is pure Source; importing no owner module.
ctx={};exec(compile((HERE/'core_audit.py').read_text(),'<own pure core DATA decoder>','exec'),ctx)
original=Path(refs['originalAdapter']['path']).read_bytes();a=ctx['decode'](original);check(hashlib.sha256(original).hexdigest()==refs['originalAdapter']['sha256'],'original988 current bytes DATA');check(len(a['imports'])==64 and len(a['types'])==35 and len(a['functionTypes'])==93 and len(a['exports'])==52,'complete actual pinned core metadata decoded as DATA')
af=copy.deepcopy([x for x in a['imports']if x['kind']==0]);af=[dict(x,typeIndex=0)for x in af]
for i,x in enumerate(af):x['functionIndex']=i
base=dict(types=[dict(params=[],results=[])],imports=af+[dict(module='env',name='memory',kind=2,limits=[0,0])],functionTypes=[0],tables=[],memories=[],globals=[],exports=[dict(name='run',kind=0,index=63)],bodies=[dict(locals=[],ops=[[0x10,[0]],[0x0b,[]]])],custom=[dict(name='name',data=b''),dict(name='component-type:synthetic',data=b'UNTOUCHED')])
targets=[x for x in af if ctx['target'](x)];keep=[x for x in af if not ctx['target'](x)];mapping={x['functionIndex']:i for i,x in enumerate(keep+targets)};mapping[63]=63
out=copy.deepcopy(base);out['imports']=[dict(x,functionIndex=i)for i,x in enumerate(keep)]+[base['imports'][-1]];out['functionTypes']=[0]*15;out['bodies']=[dict(locals=[],ops=[[0,[]],[0x0b,[]]])for _ in range(14)]+[dict(locals=[],ops=ctx['mapped_ops'](base['bodies'][0]['ops'],mapping))]
result=ctx['compare_decoded'](base,out);check(result['convertedTargetImports']==14 and result['clocksPreserved']==6 and result['pollImportsPreserved']==2,'actual comparison function accepts only planned synthetic14changes with sixclock/twopoll')
for key in ['import','clock','type','export','call','stub','locals','body-count','custom']:
    bad=copy.deepcopy(out)
    if key in ['import','clock']:bad['imports'][0 if key=='import'else next(i for i,x in enumerate(bad['imports'])if x['module'].startswith('wasi:clocks/'))]['name']='CHANGED'
    elif key=='type':bad['types'][0]['params']=[0x7f]
    elif key=='export':bad['exports'][0]['index']=62
    elif key=='call':bad['bodies'][-1]['ops'][0][1]=[1]
    elif key=='stub':bad['bodies'][0]['ops'][0]=[1,[]]
    elif key=='locals':bad['bodies'][-1]['locals']=[0x7f]
    elif key=='body-count':bad['bodies'].pop()
    else:bad['custom'][1]['data']=b'ALIASES CHANGED'
    refuses(lambda:ctx['compare_decoded'](base,bad),'encoded reference/type/import/body model refuses '+key)
refuses(lambda:ctx['audit_pair'](b'UNKNOWN',b'UNKNOWN'),'production normalized hash guard never weakened for synthetic tests')
refuses(lambda:ctx['decode'](original[:-1]),'truncated original module refuses')
refuses(lambda:ctx['ops'](ctx['Reader'](b'\xfe\x00')),'unreviewed opcode refuses rather than skipped')

# Extract genuine original write_normalized BODY into an in-memory OS/Path
# harness. normalized_bytes is a synthetic payload seam, never actual input.
normal_source=Path(refs['normalizer']['path']).read_text();tree=ast.parse(normal_source);nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['need','write_normalized']];code=compile(ast.Module(body=nodes,type_ignores=[]),'<genuine writer body with injected memory endpoints>','exec')
def writer_case(failure=None):
    trace=[];state={'open':False,'closed':0,'payload':b'', 'source_stats':0}
    class P:
        def __init__(self,x):self.x=PurePosixPath(str(x))
        def __str__(self):return str(self.x)
        @property
        def parts(self):return self.x.parts
        @property
        def parent(self):return P(self.x.parent)
        @property
        def parents(self):return tuple(P(x)for x in self.x.parents)
        def is_absolute(self):return self.x.is_absolute()
        def is_symlink(self):return failure=='symlink'and str(self)=='/PURE/output'
        def is_dir(self):return str(self)!='/PURE/input'
        def is_file(self):return str(self)=='/PURE/input'
        def stat(self):
            source=str(self)=='/PURE/input';state['source_stats']+=int(source);return types.SimpleNamespace(st_mode=(stat.S_IFREG|0o600)if source else(stat.S_IFDIR|0o700),st_size=53512,st_dev=1,st_ino=2,st_mtime_ns=1+(1 if failure=='changed-input'and state['source_stats']>1 else 0),st_ctime_ns=1)
        def read_bytes(self):return b'SYNTHETIC_INPUT'
    class Stream:
        def __enter__(self):return self
        def __exit__(self,*args):trace.append('wrapper-exit-no-fd-close')
        def write(self,b):state['payload']=b;trace.append('write');return len(b)-(1 if failure=='short'else 0)
        def flush(self):
            trace.append('flush')
            if failure=='flush':raise OSError('injected flush')
        def fileno(self):return 77
    def opened(*args):
        if failure=='existing':raise FileExistsError('injected O_EXCL')
        state['open']=True;trace.append('open-owned77');return 77
    def wrapped(fd,mode,closefd):
        assert fd==77 and closefd is False
        if failure=='fdopen':raise OSError('injected wrapper creation')
        return Stream()
    def fsynced(fd):
        trace.append('fsync')
        if failure=='fsync':raise OSError('injected fsync')
    def closed(fd):assert fd==77 and state['open'];state['closed']+=1;trace.append('close-owner77')
    fake_os=types.SimpleNamespace(O_WRONLY=1,O_CREAT=2,O_EXCL=4,open=opened,fdopen=wrapped,fsync=fsynced,close=closed,fstat=lambda fd:types.SimpleNamespace(st_mode=stat.S_IFREG|0o600,st_size=len(state['payload'])))
    context=dict(Path=P,os=fake_os,stat=stat,hashlib=hashlib,normalized_bytes=lambda b:b'SYNTHETIC_NORMALIZED');exec(code,context)
    error=None
    try:context['write_normalized']('/PURE/input','/PURE/output')
    except(ValueError,OSError)as e:error=type(e).__name__
    return state,trace,error
state,trace,error=writer_case();check(error is None and state['closed']==1 and trace[-1]=='close-owner77','genuine writer owns fd exactly once on success')
for name in ['fdopen','short','flush','fsync']:
    state,trace,error=writer_case(name);check(error is not None and state['closed']==1 and state['open'],'partial failure retains model bytes and closes acquired descriptor '+name)
for name in ['existing','symlink','changed-input']:
    state,trace,error=writer_case(name);check(error is not None and state['closed']==0 and not state['open'],'pre-acquisition refusal closes no unowned descriptor '+name)
controller=(HERE/'controller.py').read_text();ast.parse(controller)
check(controller.count("'prune-clock-adapter-io'")==1 and ",300);terminals.append(row)"in controller,'one actual CLI call site with300 bound')
check("normalizer.write_normalized(refs['originalAdapter']['path'],str(normal))"in controller,'genuine exact original API call signature')
check(controller.index('frame[\'c\'].recheck()')<controller.index("normalizer=load_actual(refs['normalizer']"),'complete auth/recheck before original normalizer import')
check('finally:os.close(fd)'in controller and "'wb',closefd=False"in controller,'metadata private writer owns fd on wrapper failure')
node=(HERE/'validate-core.mjs').read_text();check(node.count('WebAssembly.validate(')==2 and not any(x in node for x in ['WebAssembly.compile(','WebAssembly.instantiate(','new WebAssembly.Module(']),'Node validator only validate; no compile/instantiate/exports')
for f in HERE.glob('*.py'):ast.parse(f.read_text());checks.append('Python AST '+f.name)
root=json.loads((HERE/'future-root-authority.template.json').read_text());check(all(root[k]is None for k in ['state','sourceIndex','sourceIndependentReview','normalizationAllowed','singlePrunerCallAllowed','coreValidationAllowed','metadataWitDecodeAllowed']),'all future effective grants unissued')
for k in ['outputRoot','externalRoot']:
    q=Path(refs[k]);check(not q.exists()and not q.is_symlink(),'future root absent '+k)
(HERE/'pure-results.json').write_text(json.dumps(dict(schemaVersion=1,checks=len(checks),checkNames=checks,ownCoreDataParserExecuted=True,originalCoreReadAsDataOnly=True,normalizerBodyExtractedOnlyForSyntheticMemoryModels=True,actualNormalizerImported=False,actualNormalizedFilePublished=False,actualPrunerInvoked=False,actualGuestExecuted=False),indent=2)+'\n');print(json.dumps(dict(checks=len(checks),sourceOnly=True)))
