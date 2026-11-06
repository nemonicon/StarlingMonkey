"""Delegated Root C-only adapter control. No JS engine or Next application."""
from pathlib import Path
import hashlib, importlib.util, json, os, re, stat, sys, traceback

HERE = Path(__file__).resolve().parent
BUILD = Path('/private/tmp/starling-node-compat/next-adapter-probe-v1-build')
HOST = Path('/private/tmp/starling-node-compat/next-adapter-probe-v1-wasmtime')

def row(path):
    path = Path(path); h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024**2), b''): h.update(block)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size)

def checked(record):
    path = Path(record['path'])
    assert path.is_absolute() and '..' not in path.parts
    assert all(not ancestor.is_symlink() for ancestor in (path, *path.parents))
    assert path.is_file() and row(path) == record
    return path

def write(path, value):
    data = value if isinstance(value, bytes) else (json.dumps(value, indent=2)+'\n').encode()
    with Path(path).open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600); stream.write(data); stream.flush(); os.fsync(stream.fileno())

def tree(root):
    root = Path(root); assert root.is_dir() and not root.is_symlink()
    result = dict(root=str(root), files={}, links={}, directories=[])
    for path in sorted(root.rglob('*')):
        relative = str(path.relative_to(root)); s = path.lstat()
        if path.is_symlink():
            target = path.resolve(strict=True); assert target.is_relative_to(root)
            result['links'][relative] = dict(target=os.readlink(path), physical=str(target), inode=s.st_ino, mode=stat.S_IMODE(s.st_mode))
        elif path.is_file():
            result['files'][relative] = dict(descriptor=row(path), inode=s.st_ino, device=s.st_dev, mode=stat.S_IMODE(s.st_mode), nlink=s.st_nlink)
        elif path.is_dir(): result['directories'].append(relative)
        else: raise AssertionError('Unsupported input kind: '+str(path))
    return result

def clean(terminal):
    return (terminal['rawExitCode'] == 0 and terminal['timeout'] is False
            and terminal['forcedCleanup'] is False and terminal['parentOwnedGroupGone'] is True
            and terminal['allObservedOwnedGroupsGone'] is True
            and all(terminal[key] == [] for key in ('signals','interruptedSignals','errors','remainingObservedPids')))

def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert sys.argv[1:] in (['build'], ['host'])
    phase = sys.argv[1]; plan = json.loads((HERE/'plan.json').read_text())
    authority_record=row(HERE/'authority.json')
    authority = json.loads((HERE/'authority.json').read_text())
    assert authority['plan'] == row(HERE/'plan.json')
    assert authority['engineJSNextExecutionAllowed'] is False
    for record in plan['sourceFiles'] + list(plan['pins'].values()): checked(record)
    assert checked(plan['pins']['monitor']).name == 'monitor.py'
    output = BUILD if phase == 'build' else HOST
    assert str(output) == plan['buildRoot' if phase == 'build' else 'hostRoot'] and not output.exists()
    before = tree(plan['sdkRoot'])
    assert before['links']['bin/clang']['physical'] == plan['pins']['clangPhysical']['path']
    os.umask(0o077); output.mkdir(mode=0o700); (output/'tmp').mkdir()
    write(output/'input-before.json', dict(sdk=before, sourceFiles=plan['sourceFiles'], pins=plan['pins']))
    spec = importlib.util.spec_from_file_location('original_owned_monitor', checked(plan['pins']['monitor']))
    monitor = importlib.util.module_from_spec(spec); spec.loader.exec_module(monitor)
    env = {key:os.environ[key] for key in ('HOME','USER','LOGNAME') if key in os.environ}
    env.update(PATH='/usr/bin:/bin', LC_ALL='C', LANG='C', TMPDIR=str(output/'tmp'))
    commands=[]; error=None; audit=None; final=None
    def recheck():
        assert tree(plan['sdkRoot']) == before
        assert row(HERE/'authority.json') == authority_record
        assert authority['plan'] == row(HERE/'plan.json')
        for record in plan['sourceFiles'] + list(plan['pins'].values()): checked(record)
    def command(label, argv, cap):
        recheck(); logs=output/label; logs.mkdir(mode=0o700)
        terminal=monitor.monitor(argv,str(output),env,logs,cap,row(HERE/'authority.json'))
        commands.append(dict(label=label,argv=argv,capSeconds=cap,terminal=row(logs/'terminal.json'),
                             stdout=row(logs/'stdout.log'),stderr=row(logs/'stderr.log'),clean=clean(terminal),rawExitCode=terminal['rawExitCode']))
        write(output/(label+'-observation.json'),commands[-1])
        recheck(); assert clean(terminal), label+' failed; raw evidence preserved'
    try:
        if phase == 'build':
            assert authority['cCompilerAndComponentDataToolsAllowed'] is True
            for label, argv in plan['buildCommands']: command(label,argv,120)
            wit=(output/'component-wit/stdout.log').read_text()
            imports=re.findall(r'^\s*import ([^;\n]+);$',wit,re.M)
            exports=re.findall(r'^\s*export ([^;\n]+);$',wit,re.M)
            assert len(imports)==len(set(imports)) and all(value in plan['selectedInterfaces'] for value in imports)
            assert all(value.endswith('@0.2.10') for value in imports)
            assert exports==['wasi:http/incoming-handler@0.2.10']
            core=(output/'core-print/stdout.log').read_text()
            core_imports=re.findall(r'^\s*\(import "([^"]+)" "([^"]+)"',core,re.M)
            p1=[name for module,name in core_imports if module=='wasi_snapshot_preview1']
            assert set(plan['requiredPreview1Functions']) <= set(p1)
            assert all(module=='wasi_snapshot_preview1' or module in plan['selectedInterfaces'] for module,_ in core_imports)
            audit=dict(schemaVersion=1,state='ACTUAL_NEXT_ADAPTER_C_COMPONENT_DATA_PASSED_V1',passed=True,
                       component=row(output/'probe.component.wasm'),core=row(output/'probe.core.wasm'),adapter=plan['pins']['adapter'],
                       imports=imports,exports=exports,unusedSelectedInterfaces=sorted(set(plan['selectedInterfaces'])-set(imports)),
                       coreImports=core_imports,actualPreview1CoreFunctions=p1,externalPreview1Imports=False,
                       exactSelectedVersionAndResourceCompositionValidated=True,guestExecuted=False,engineJSNextExecuted=False)
            write(output/'component-audit.json',audit)
        else:
            assert authority['conditionalThreeRequestStockWasmtimeAllowed'] is True
            audit=json.loads((BUILD/'component-audit.json').read_text())
            build_result=json.loads((BUILD/'result.json').read_text())
            assert build_result['passed'] is True and audit['passed'] is True
            assert build_result['componentAudit'] == row(BUILD/'component-audit.json')
            checked(audit['component']); checked(audit['adapter'])
            assert set(audit['imports']) <= set(plan['selectedInterfaces'])
            assert all(value.endswith('@0.2.10') for value in audit['imports'])
            command('stock-wasmtime-three-requests',[plan['pins']['node']['path'],str(HERE/'run-wasmtime.mjs'),str(output),str(BUILD)],180)
            host=json.loads((output/'host-result.json').read_text());assert host['passed'] is True
    except BaseException as caught:
        error=dict(type=type(caught).__name__,message=str(caught),stack=traceback.format_exc())
    finally:
        try:
            recheck(); final=dict(unchanged=True,sdkFiles=len(before['files']),sdkLinks=len(before['links']),sdkBytes=sum(r['descriptor']['bytes'] for r in before['files'].values()))
        except BaseException as caught:
            final=dict(unchanged=False,type=type(caught).__name__,message=str(caught),stack=traceback.format_exc())
        passed=error is None and final['unchanged'] is True
        result=dict(schemaVersion=1,state='NEXT_ADAPTER_C_'+phase.upper()+('_PASSED_V1' if passed else '_FAILURE_PRESERVED_V1'),
                    passed=passed,phase=phase,authority=row(HERE/'authority.json'),plan=row(HERE/'plan.json'),commands=commands,
                    error=error,initialProtection=dict(sdkFiles=len(before['files']),sdkLinks=len(before['links'])),finalProtection=final,
                    componentAudit=row(BUILD/'component-audit.json') if (BUILD/'component-audit.json').is_file() else None,
                    hostResult=row(HOST/'host-result.json') if (HOST/'host-result.json').is_file() else None,
                    engineJSNextExecuted=False,hostModified=False)
        write(output/'result.json',result)
        print(json.dumps(dict(result=row(output/'result.json'),passed=passed,error=error)),flush=True)
    return 0 if passed else 1

if __name__=='__main__': raise SystemExit(main())
