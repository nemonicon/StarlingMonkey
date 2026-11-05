"""Source/hash/AST/in-memory tests only; never publish or run a Rust/guest tool."""
from pathlib import Path,PurePosixPath
from types import SimpleNamespace
import ast,copy,hashlib,io,itertools,json,os,re,stat,tarfile
HERE=Path(__file__).resolve().parent
seen={};checks=0;cases=[]


def need(value,message='check'):
    global checks
    checks+=1
    assert value,message


def file(path,sha=None,size=None,force=False):
    p=Path(path);need(p.is_absolute()and p.is_file()and not p.is_symlink(),str(p));a=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns);real=str(p.resolve())
    if str(p)not in seen or force:
        h=hashlib.sha256()
        with p.open('rb')as stream:
            for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
        z=p.stat();need(identity(a)==identity(z)and real==str(p.resolve()));row=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
        if str(p)in seen:need(seen[str(p)]==(row,identity(z),real))
        seen[str(p)]=(row,identity(z),real)
    row,prior,resolved=seen[str(p)];need(identity(a)==prior and real==resolved)
    if sha is not None:need(row['sha256']==sha,str(p))
    if size is not None:need(row['bytes']==size,str(p))
    return row


def verify(row,force=False):return file(row['path'],row['sha256'],row['bytes'],force)
def load(path):file(path);return json.loads(Path(path).read_bytes())
def read(row):verify(row);return json.loads(Path(row['path']).read_bytes())
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def family(index):
    value=read(index);root=Path(index['path']).parent;names={'index.json'};rows=[index]
    for row in value['files']:
        name=row['path'];need(name not in names and not name.startswith('/')and all(x not in['','.','..']for x in name.split('/')));names.add(name);actual=dict(row,path=str(root/name));verify(actual);rows.append(actual)
    need({str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in root.rglob('*')))
    return rows


def extract(text,names,env):
    nodes=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name in names];need(len(nodes)==len(names))
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<Source pure/injected functions>','exec'),env)
    return env


def case(name,call,reject=False):
    failed=False
    try:call()
    except(ValueError,UnicodeDecodeError,OSError,AssertionError):failed=True
    need(failed==reject,name);cases.append(dict(name=name,passed=True,expectedReject=reject))


def apply_diff(source,patch,reverse=False):
    old=source.splitlines(keepends=True);lines=patch.splitlines(keepends=True);out=[];cursor=0;i=0
    while i<len(lines):
        match=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i])
        if not match:i+=1;continue
        start=int(match[3]if reverse else match[1])-1;need(start>=cursor);out.extend(old[cursor:start]);cursor=start;i+=1
        while i<len(lines)and not lines[i].startswith('@@'):
            line=lines[i];i+=1
            if line.startswith(('---','+++')):continue
            sign=line[0];text=line[1:]
            if reverse:sign={'+':'-','-':'+',' ':' '}.get(sign,sign)
            need(sign in[' ','+','-'])
            if sign in[' ','-']:need(old[cursor]==text);cursor+=1
            if sign in[' ','+']:out.append(text)
    return ''.join(out+old[cursor:])


def rust_function(text,name):
    start=re.search(r'(?m)^(?:pub )?fn '+re.escape(name)+r'\b',text).start();next_fn=re.search(r'(?m)^(?:pub )?fn ',text[start+1:]);return text[start:start+1+next_fn.start()]if next_fn else text[start:]


def wasi_calls(text):return re.findall(r'stub_wasi_imports\(\s*module,\s*"([^"]+)",\s*"([^"]+)"',text)


def tree(value):
    root=Path(value['root']);expected=set()
    for row in value['files']:verify(row['descriptor']);need(row['descriptor']['path']==str(root/row['relativePath'])and stat.S_IMODE(Path(row['descriptor']['path']).stat().st_mode)==row['mode']);expected.add(row['relativePath'])
    for row in value['symlinks']:
        p=root/row['path'];need(p.is_symlink()and os.readlink(p)==row['target']and str(p.resolve())==row['resolved']['path']);verify(row['resolved']);expected.add(row['path'])
    need({str(p.relative_to(root))for p in root.rglob('*')if p.is_file()or p.is_symlink()}==expected)


def main():
    need(not(HERE/'index.json').exists());refs=load(HERE/'references.json');deriv=load(HERE/'source-derivation.json');cut=load(HERE/'source-cut.json');tools=load(HERE/'tool-cut-references.json');plan=load(HERE/'future-build-plan.json')
    for name in['provenanceReport','independentDesignNotes']:
        rows=family(refs[name]['index']);need(refs[name]['result']in rows)
    need(refs['provenanceReport']['index']['sha256']=='dd49f61424b0285a590bc4a5f2ccc765d810b02f12919ed9470f5d3ad3a09433'and refs['independentDesignNotes']['index']['sha256']=='8a069abcd6d798bf81098685ad6435e1c2ae3436cf1714faf56dc23310915bb3')
    for name in['baselineSourceArchive','baselineArchiveShaText','baselineSourceObservation','baselineBuildLog','adapter','rootPureNormalizerObservation']:verify(refs[name])
    alias=refs['baselineSourceArchiveAlias'];p=Path(alias['path']);need(p.is_symlink()and os.readlink(p)==alias['target']and str(p.resolve())==alias['resolved']['path'])
    need(Path(refs['baselineArchiveShaText']['path']).read_text().strip()==refs['baselineSourceArchive']['sha256'])
    tree(cut['baseline']);need(cut['sourceFiles']==271 and cut['changedFiles']==4 and cut['unchangedFiles']==267 and len(cut['files'])==271)
    patch=(HERE/'io-policy.patch').read_text();file(HERE/'io-policy.patch');patches={part.splitlines()[0][6:]:part for part in re.split(r'(?m)(?=^--- a/)',patch)if part.startswith('--- a/')};need(len(patches)==4)
    for row in deriv['files']:
        verify(row['before']);verify(dict(row['after'],path=str(HERE/row['after']['path'])));before=Path(row['before']['path']).read_text();after=(HERE/row['after']['path']).read_text()
        need(apply_diff(before,patches[row['path']])==after and apply_diff(after,patches[row['path']],True)==before)
    need(deriv['cliBaseline']==deriv['files'][1]['before']and deriv['cliAfter']==deriv['files'][1]['after'])
    changed={r['path']:r for r in deriv['files']}
    for row in cut['files']:
        need(row['futureConfiguredPath']==str(Path(cut['futureSourceRoot'])/row['path']));payload=changed[row['path']]['after']if row['path']in changed else row['baseline'];need(row['sha256']==payload['sha256']and row['bytes']==payload['bytes'])
    for row in tools['rustBinAndLibFiles']:verify(row)
    for row in tools['lockedRegistryArchives']:verify(row['descriptor'])
    tree(tools['jsToolchain']);verify(tools['node']);verify(tools['jcoEntry']);need(len(tools['rustBinAndLibFiles'])==270 and len(tools['lockedRegistryArchives'])==118 and len(tools['missingLockedRegistryArchives'])==3)
    for row in tools['missingLockedRegistryArchives']:need(not Path(row['expectedPath']).exists())
    status=tools['missingArchiveStatus'];need(status['globalSourceBlocker']is status['offlineReadinessProved']is status['fetchPerformed']is False)
    for witness in status['directWindowsEdges']:
        verify(witness['archive'])
        with tarfile.open(witness['archive']['path'],'r:gz')as archive:value=archive.extractfile(witness['member']).read()
        need(hashlib.sha256(value).hexdigest()==witness['memberSha256']and witness['exactManifestHeading'].encode()in value)
    before_lock=Path(deriv['files'][3]['before']['path']).read_text();after_lock=(HERE/'after/Cargo.lock').read_text();need(after_lock.replace(' "sha2",\n','',1)==before_lock)
    cargo=(HERE/'after/crates/spidermonkey-embedding-splicer/Cargo.toml').read_text();need(cargo.replace('sha2 = { version = "=0.10.9", default-features = false }\n','')==Path(deriv['files'][2]['before']['path']).read_text())
    normalizer_text=(HERE/'normalize-adapter.py').read_text();file(HERE/'normalize-adapter.py');env=dict(Path=Path,hashlib=hashlib,os=os,stat=stat,EXPECTED_SHA256=refs['adapter']['sha256'],NORMALIZED_SHA256=deriv['normalizedAdapterInputSha256'])
    extract(normalizer_text,['need','u32','encode_u32','skip_name','normalize_import_payload','normalized_bytes'],env)
    encode=env['encode_u32'];normalize_payload=env['normalize_import_payload'];normalize=env['normalized_bytes']
    def name(s):b=s.encode();return encode(len(b))+b
    memory=name('env')+name('memory')+b'\x02\x00\x00';functions=[name('test:interface')+name('function-'+str(i))+b'\x00'+encode(128+i)for i in range(63)];payload=encode(64)+memory+b''.join(functions);expected=encode(64)+b''.join(functions)+memory
    case('memory moves after unchanged function byte entries',lambda:need(normalize_payload(payload)==expected))
    for label,data in[('wrong count',b'\x3f'+payload[1:]),('truncated',payload[:-1]),('trailing',payload+b'\0'),('memory already last',expected),('nonzero memory minimum',b'\x40'+memory[:-1]+b'\1'+b''.join(functions)),('memory max/shared flag',b'\x40'+name('env')+name('memory')+b'\x02\x01\x00\x01'+b''.join(functions)),('wrong kind',b'\x40'+name('env')+name('table')+b'\x01\x70\0\0'+b''.join(functions)),('duplicate memory',b'\x40'+memory+memory+b''.join(functions[:-1])),('invalid UTF8',b'\x40\x01\xff'+name('memory')+b'\x02\0\0'+b''.join(functions))]:case('payload rejects '+label,lambda v=data:normalize_payload(v),True)
    case('u32 range overflow',lambda:env['u32'](b'\xff\xff\xff\xff\x10',0),True);case('u32 continuation overflow',lambda:env['u32'](b'\x80'*6,0),True);case('u32 truncated',lambda:env['u32'](b'\x80',0),True)
    original=Path(refs['adapter']['path']).read_bytes();normalized=normalize(original);need(len(original)==len(normalized)==53512 and original!=normalized and hashlib.sha256(normalized).hexdigest()==deriv['normalizedAdapterInputSha256'])
    for label,data in[('wrong input size',original[:-1]),('tampered same-size input',bytes([original[0]^1])+original[1:]),('normalized input supplied twice',normalized),('appended input',original+b'\0')]:case('whole binary rejects '+label,lambda v=data:normalize(v),True)
    # Independently derived metadata reader only; no instruction decoder/import.
    notes=Path(refs['independentDesignNotes']['index']['path']).parent;reader=(notes/'audit.py').read_text();pure=extract(reader,['u32','name','core_metadata'],dict(hashlib=hashlib,need=need));a=pure['core_metadata'](original);b=pure['core_metadata'](normalized)
    need(a['types']==b['types']and a['exports']==b['exports']and len(a['sections'])==len(b['sections']))
    need(all(x==y for x,y in zip(a['sections'],b['sections'])if x['id']!=2))
    af=[r for r in a['imports']if r['kind']==0];bf=[r for r in b['imports']if r['kind']==0];need(len(af)==len(bf)==63)
    for x,y in zip(af,bf):need({k:v for k,v in x.items()if k!='importIndex'}=={k:v for k,v in y.items()if k!='importIndex'}and y['importIndex']==y['functionIndex'])
    need(b['imports'][-1]==dict(a['imports'][0],importIndex=63))
    def writer_model(mode):
        events=[];files={};source_stats=0;output='/private/source-test-only/out/normalized.wasm';input_path='/private/source-test-only/input.wasm'
        if mode=='existing':files[output]=b'original-existing'
        class MemoryPath:
            def __init__(self,value):self.value=str(value)
            def __str__(self):return self.value
            def is_absolute(self):return PurePosixPath(self.value).is_absolute()
            @property
            def parts(self):return PurePosixPath(self.value).parts
            @property
            def parents(self):return[MemoryPath(str(p))for p in PurePosixPath(self.value).parents]
            @property
            def parent(self):return MemoryPath(str(PurePosixPath(self.value).parent))
            def is_symlink(self):return mode=='symlink'and self.value==str(PurePosixPath(output).parent)
            def is_dir(self):return True
            def is_file(self):return self.value==input_path
            def stat(self):
                nonlocal source_stats
                if self.value==input_path:
                    source_stats+=1;return SimpleNamespace(st_mode=0o100600,st_dev=1,st_ino=2,st_size=53511 if mode=='bad input size'else 53512,st_mtime_ns=1,st_ctime_ns=source_stats if mode=='changed input'else 1)
                return SimpleNamespace(st_mode=0o40755 if mode=='public parent'else 0o40700)
            def read_bytes(self):events.append('input read');return original
        class MemoryStream:
            def __enter__(self):return self
            def __exit__(self,*args):events.append('closed')
            def write(self,data):
                events.append('write');files[output]=data[:37]if mode=='writer failure'else data[:-1]if mode=='short write'else data
                if mode=='writer failure':raise OSError('injected write failure')
                return len(files[output])
            def flush(self):events.append('flush')
            def fileno(self):return 7
        def opened(path,flags,permissions):
            need(str(path)==output and flags&os.O_EXCL and flags&os.O_CREAT and permissions==0o600);events.append('exclusive open')
            if output in files:raise FileExistsError('injected existing output')
            files[output]=b'';return 7
        def sync(fd):
            need(fd==7);events.append('fsync')
            if mode=='fsync failure':raise OSError('injected fsync failure')
        def wrapped(fd,kind,closefd):
            need(fd==7 and kind=='wb'and closefd is False)
            if mode=='fdopen failure':raise OSError('injected wrapper failure')
            return MemoryStream()
        def closed(fd):need(fd==7);events.append('fd closed')
        fake=SimpleNamespace(O_WRONLY=os.O_WRONLY,O_CREAT=os.O_CREAT,O_EXCL=os.O_EXCL,open=opened,fdopen=wrapped,close=closed,fsync=sync,fstat=lambda fd:SimpleNamespace(st_mode=0o100600,st_size=len(files[output])))
        injected=dict(env,Path=MemoryPath,os=fake);extract(normalizer_text,['write_normalized'],injected);accepted=False
        try:result=injected['write_normalized'](input_path,output);accepted=True
        except(ValueError,OSError):pass
        need(accepted==(mode=='success'))
        if accepted:need(result==dict(path=output,sha256=deriv['normalizedAdapterInputSha256'],bytes=53512)and files[output]==normalized and events.index('write')<events.index('flush')<events.index('fsync')<events.index('closed')<events.index('fd closed'))
        elif mode=='existing':need(files[output]==b'original-existing')
        elif mode in['writer failure','short write','fsync failure','fdopen failure']:need(output in files and events[-1]=='fd closed')
        else:need(output not in files)
        need(events.count('fd closed')==(1 if mode in['success','writer failure','short write','fsync failure','fdopen failure']else 0))
    for mode in['success','existing','public parent','symlink','bad input size','changed input','writer failure','short write','fsync failure','fdopen failure']:case('memory-only output lifetime '+mode,lambda m=mode:writer_model(m))
    rust=(HERE/'after/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs').read_text();base=Path(deriv['baselinePath']).read_text();pruner=rust_function(rust,'prune_clock_adapter_io');poll=wasi_calls(rust_function(rust,'stub_io_poll'));streams=wasi_calls(rust_function(rust,'stub_io_streams'));old=wasi_calls(rust_function(base,'stub_io'))
    need(len(poll)==4 and len(streams)==19 and sorted(poll+streams)==sorted(old)and len(set(old))==23)
    need(pruner.index('wasm.len() != 53512')<pruner.index('Module::parse')and deriv['normalizedAdapterInputSha256']in pruner)
    need(re.findall(r'(?m)^    (stub_[a-z_]+)\(&mut module\)\?;',pruner)==['stub_stdio','stub_io_streams'])
    need(not any(x+'('in pruner for x in['stub_wasi','stub_random','stub_clocks','stub_preview1','stub_filesystem','stub_cli','stub_io_poll']))
    clock=[r for r in bf if r['module'].startswith('wasi:clocks/')];actual_poll=[r for r in bf if(r['module'].split('@')[0],r['name'])in poll];actual_stream=[r for r in bf if(r['module'].split('@')[0],r['name'])in streams];stdio=[r for r in bf if r['module']in['wasi:cli/stdin@0.2.0','wasi:cli/stdout@0.2.0','wasi:cli/stderr@0.2.0']]
    need(len(clock)==6 and len(actual_poll)==2 and len(actual_stream)==11 and len(stdio)==3)
    policy=rust_function(rust,'io_requirements');target=rust_function(rust,'target_world_requires_io');target_names=set(re.findall(r'"(wasi:[^"]+)"',target));names=set(re.findall(r'"(wasi:[^"]+)"',policy));stream_names=names-{'wasi:io/poll@0.2'};model_cases=0
    for bits in itertools.product([False,True],repeat=5):
        features={f for f,on in zip(['Clocks','Stdio','Http','FetchEvent','Random'],bits)if on}
        for world in[set()]+[{n}for n in sorted(target_names|names)]:
            stream=bool(features&{'Stdio','Http','FetchEvent'}or world&(target_names|stream_names));p=stream or 'Clocks'in features or 'wasi:io/poll@0.2'in world;need(not stream or p)
            if features=={'Clocks'}and not world:need(p and not stream)
            model_cases+=1
    need(model_cases==672 and rust.count('#[test]')==4)
    cli=(HERE/'after/crates/spidermonkey-embedding-splicer/src/bin/splicer.rs').read_text();branch=cli.split('Commands::PruneClockAdapterIo { input, output } => {',1)[1].split('Commands::StubWasi',1)[0]
    need('stub_wasi::prune_clock_adapter_io(wasm)?'in branch and '.create_new(true)'in branch and 'options.mode(0o600)'in branch and 'file.write_all(&result)?'in branch and 'file.sync_all()?'in branch and 'fs::write('not in branch)
    wirm=next(r['descriptor']for r in tools['lockedRegistryArchives']if r['name']=='wirm'and r['version']=='5.0.0');registry=Path('/Users/dan/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/wirm-5.0.0')
    with tarfile.open(wirm['path'],'r:gz')as archive:
        for name in['src/ir/function.rs','src/ir/module/module_imports.rs','src/ir/module/module_functions.rs','src/ir/module/mod.rs']:
            row=file(registry/name);need(archive.extractfile('wirm-5.0.0/'+name).read()==Path(row['path']).read_bytes())
    need(plan['controllerImplemented']is plan['allActionsAllowed']is False and plan['futureEnvironment']['CARGO_HOME']is None and plan['futureEnvironment']['hostLinkerAndSdk']is None)
    for field in['sourceIndependentReview','rootAuthority','stageAction','buildAction','normalizationPublication','pruningAction','actualPackage','actualPrunedAdapter','componentAction','runtimeAction']:need(refs[field]is None)
    for path in[cut['futureSourceRoot'],cut['futureWorkRoot'],cut['futurePackageRoot']]:need(not Path(path).exists())
    ast_files=0
    for path in HERE.rglob('*'):
        if path.is_file()and path.name not in['source-inputs.json','check-results.json','pure-results.json','adapter-metadata-model.json']:
            file(path)
            if path.suffix=='.py':ast.parse(path.read_text());ast_files+=1
            if path.suffix=='.json':json.loads(path.read_bytes())
    snapshots=[v[0]for v in seen.values()]
    for row in snapshots:verify(row,True)
    write('source-inputs.json',dict(schemaVersion=1,files=snapshots,initialAndFinalHashesAndIdentityVerified=True,mutableExternalSourceOrToolFilesWritten=False))
    write('pure-results.json',dict(schemaVersion=1,cases=cases,independentBooleanPolicyCases=model_cases,rustUnitTestDefinitions=4,rustUnitTestsExecuted=False,writerSeamsMemoryOnly=True,actualNormalizedBytesComputedInMemory=True,normalizedArtifactPublished=False,adapterPrunerExecuted=False))
    write('adapter-metadata-model.json',dict(schemaVersion=1,originalAdapter=refs['adapter'],normalizedInMemorySha256=deriv['normalizedAdapterInputSha256'],bytes=53512,functionTypes=a['types'],exports=a['exports'],originalImports=a['imports'],normalizedInMemoryImports=b['imports'],unchangedNonImportSections=True,instructionsDecoded=False,sixClockImports=clock,twoPollImports=actual_poll,elevenPresentStreamErrorTargets=actual_stream,threePresentStdioTargets=stdio,expectedActualPruneTargets=14,expectedPostPruneImports=dict(functions=49,memory=1),adapterPrunerExecuted=False,actualPrunedArtifact=None))
    write('check-results.json',dict(schemaVersion=1,state='CLOCK_IO_PRUNING_UNCOMPILED_SOURCE_CHECKS_PASSED_V1',sourceOnly=True,sourceChecksPassed=True,checks=checks,inputPaths=len(snapshots),pureCases=len(cases),independentBooleanPolicyCases=model_cases,pythonAstFiles=ast_files,forwardReverseFiles=4,baselineSourceFiles=271,unchangedSourceFiles=267,changedSourceFiles=4,rustToolFiles=270,jsToolFiles=4862,lockedArchiveFiles=118,missingLockedArchiveFiles=3,missingArchiveIsGlobalSourceBlocker=False,offlineReadinessProved=False,actualNormalizedBytesComputedInMemory=True,normalizedArtifactPublished=False,adapterPrunerExecuted=False,normalizerWriterExecutedWithRealFilesystem=False,rustCompiled=False,rustUnitTestsExecuted=False,nodeOrWizerOrEngineOrComponentOrGuestExecuted=False,sourceIndependentReview=None,rootAuthority=None,grantsActionAuthority=False))
    print(json.dumps(dict(checks=checks,inputPaths=len(snapshots),pureCases=len(cases),policyCases=model_cases,astFiles=ast_files,rustCompiled=False,adapterArtifactPublished=False)))


if __name__=='__main__':main()
