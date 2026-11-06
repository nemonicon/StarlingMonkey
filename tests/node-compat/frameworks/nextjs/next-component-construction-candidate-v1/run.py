"""Late-Root-owned raw ESM construction and DATA validation, never HTTP serving."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, sys, traceback
HERE=Path(__file__).resolve().parent

def row(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def checked(r):
    p=Path(r['path']);assert p.is_absolute()and'..'not in p.parts
    assert all(not x.is_symlink()for x in(p,*p.parents))
    assert row(p)=={k:r[k]for k in('path','sha256','bytes')};return p
def read(r):return json.loads(checked(r).read_text())
def write(p,v):
    data=v if isinstance(v,bytes)else(json.dumps(v,indent=2)+'\n').encode()
    with Path(p).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(data);f.flush();os.fsync(f.fileno())
def clean(t):
    return t['rawExitCode']==0 and t['timeout']is False and t['forcedCleanup']is False and t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True and all(t[k]==[]for k in('errors','signals','interruptedSignals','remainingObservedPids'))
def family(r):
    p=checked(r);j=json.loads(p.read_text());assert len(j['files'])==len({x['path']for x in j['files']})
    assert{r['path']for r in j['files']}=={str(x.relative_to(p.parent))for x in p.parent.rglob('*')if x.is_file()and x!=p}
    assert not any(x.is_symlink()for x in p.parent.rglob('*'))
    for x in j['files']:checked(dict(x,path=str(p.parent/x['path'])))
def audit_wit(text,selected):
    imports=re.findall(r'^\s*import ([^;\n]+);$',text,re.M);exports=re.findall(r'^\s*export ([^;\n]+);$',text,re.M)
    assert len(imports)==len(re.findall(r'^\s*import\b',text,re.M))and len(exports)==len(re.findall(r'^\s*export\b',text,re.M))
    assert len(imports)==len(set(imports))and set(imports)<=set(selected)
    assert all(x.endswith('@0.2.10')for x in imports)and exports==['wasi:http/incoming-handler@0.2.10']
    return dict(emittedImports=imports,exports=exports,selectedInterfaces=selected,unusedSelectedInterfaces=sorted(set(selected)-set(imports)))
def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--authority',required=True);parser.add_argument('--sha256',required=True);args=parser.parse_args()
    ar=row(Path(args.authority));assert ar['sha256']==args.sha256;a=read(ar)
    p=json.loads((HERE/'plan.json').read_text());pr=row(HERE/'plan.json')
    assert a['schemaVersion']==1 and a['state']=='ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V1'
    assert a['callerIndex']['path']==str(HERE/'index.json');family(a['callerIndex']);family(p['inputSourceIndex'])
    assert a['entryMode']in p['entries']and re.fullmatch('[a-z0-9][a-z0-9-]{0,48}',a['runId'])
    output=Path(p['outputPrefix']+'-'+a['entryMode']+'-'+a['runId']);assert str(output)==a['outputRoot']and not output.exists()
    assert a['componentizeInitAllowed']is True and a['nativeBuildReviewedForConstruction']is True
    for k in('ordinaryExportsAllowed','httpServingAllowed','networkAllowed','nativeBuildAllowed','packageMutationAllowed','globalPinMutationAllowed','debugAllowed','applicationMountAtInitAllowed','deployedResnapshotAllowed'):assert a[k]is False,k
    assert a['engineBuildEvidence']and a['newSourceEvidence']and a['nativeProfileLabel']
    metadata=read(a['nativeMetadata']);assert isinstance(metadata,dict)and a['metadataExpectedFixedValues']
    assert all(metadata[k]==v for k,v in a['metadataExpectedFixedValues'].items())
    def recheck():
        checked(ar);assert row(HERE/'plan.json')==pr;family(a['callerIndex']);family(p['inputSourceIndex'])
        for r in list(p['pins'].values())+[p['packageInventory'],a['engine'],a['nativeMetadata']]+a['engineBuildEvidence']+a['newSourceEvidence']:checked(r)
    recheck();os.umask(0o077);output.mkdir(mode=0o700);(output/'tmp').mkdir(mode=0o700)
    write(output/'input-roles.json',dict(rootAuthority=ar,callerIndex=a['callerIndex'],inputSourceIndex=p['inputSourceIndex'],packageInventory=p['packageInventory'],
      engine=a['engine'],nativeMetadata=a['nativeMetadata'],engineBuildEvidence=a['engineBuildEvidence'],newSourceEvidence=a['newSourceEvidence'],
      metadataExpectedFixedValues=a['metadataExpectedFixedValues'],oldMetadataFrameAdapted=False))
    s=importlib.util.spec_from_file_location('genuine_original_owned_monitor',checked(p['pins']['monitor']));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    env={k:os.environ[k]for k in('HOME','USER','LOGNAME')if k in os.environ};env.update(PATH='/usr/bin:/bin',LC_ALL='C',LANG='C',TMPDIR=str(output/'tmp'),UV_THREADPOOL_SIZE='1',RAYON_NUM_THREADS='1')
    commands=[];error=None;final=None;artifacts=None
    def command(label,argv,cap):
        recheck();logs=output/label;logs.mkdir(mode=0o700);t=m.monitor(argv,str(output),env,logs,cap,ar)
        r=dict(label=label,argv=argv,capSeconds=cap,terminal=row(logs/'terminal.json'),stdout=row(logs/'stdout.log'),stderr=row(logs/'stderr.log'),rawExitCode=t['rawExitCode'],clean=clean(t))
        commands.append(r);write(output/(label+'-observation.json'),r);recheck();assert clean(t),label+' failed; raw preserved';return r
    try:
        command('componentize-init',[p['pins']['node']['path'],str(HERE/'entry.mjs'),str(args.authority),args.sha256,pr['sha256']],1800)
        node=read(row(output/'api-return/node-result.json'));assert node['entryMode']==a['entryMode']and node['ordinaryExportsInvoked']is False
        assert node['inputEntry']==p['entries'][a['entryMode']]and node['inputSourceIndex']==p['inputSourceIndex']
        artifacts=node['artifacts'];component=checked(artifacts['component'])
        validate=command('component-validate',[p['pins']['wasmTools']['path'],'validate',str(component)],120)
        wit=command('component-wit',[p['pins']['wasmTools']['path'],'component','wit',str(component)],120)
        graph=audit_wit(checked(wit['stdout']).read_text(),p['selectedInterfaces'])
        audit=dict(schemaVersion=1,state='NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1',passed=True,component=artifacts['component'],
          allEmittedVersion='0.2.10',noExternalPreview1OrCustomImports=True,validateTerminal=validate['terminal'],witTerminal=wit['terminal'],
          engine=a['engine'],nativeMetadata=a['nativeMetadata'],entryMode=a['entryMode'],**graph)
        write(output/'component-audit.json',audit)
        artifacts.update(componentAudit=row(output/'component-audit.json'),engine=a['engine'],nativeMetadata=a['nativeMetadata'],
                         engineBuildEvidence=a['engineBuildEvidence'],inputSourceIndex=p['inputSourceIndex'],inputEntry=p['entries'][a['entryMode']],adapter=p['pins']['adapter'])
    except BaseException as e:error=dict(type=type(e).__name__,message=str(e),stack=traceback.format_exc())
    finally:
        try:recheck();final=dict(unchanged=True)
        except BaseException as e:final=dict(unchanged=False,type=type(e).__name__,message=str(e),stack=traceback.format_exc())
        passed=error is None and final['unchanged']is True
        result=dict(schemaVersion=1,state='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V1'if passed else'NEXT_NATIVE_COMPONENT_CONSTRUCTION_FAILURE_PRESERVED_V1',
          passed=passed,entryMode=a['entryMode'],rootAuthority=ar,callerIndex=a['callerIndex'],plan=pr,artifacts=artifacts,commands=commands,error=error,finalProtection=final,
          metadataFrameProjected=False,ordinaryExportsInvoked=False,httpServed=False,appMountedAtInit=False,productionProfilePromoted=False)
        write(output/'result.json',result);print(json.dumps(dict(result=row(output/'result.json'),passed=passed,error=error)),flush=True)
    return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
