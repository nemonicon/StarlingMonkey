"""Corrected host observer only; original completed build/Source remain intact."""
from pathlib import Path
import importlib.util, json, os, sys, traceback
HERE=Path(__file__).resolve().parent

def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==1
    # Standard-library authentication precedes this inert import of pure helpers.
    import hashlib
    def descriptor(p):
        p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
    hp=json.loads((HERE/'host-plan.json').read_text());ha=json.loads((HERE/'host-authority.json').read_text())
    assert ha['plan']==descriptor(HERE/'host-plan.json') and ha['threeRequestCGuestAllowed']is True
    assert ha['engineJSNextAllowed']is False
    for r in hp['additionalSourceFiles']:
        assert descriptor(r['path'])==r and all(not p.is_symlink()for p in(Path(r['path']),*Path(r['path']).parents))
    s=importlib.util.spec_from_file_location('actual_probe_data_helpers',HERE/'run.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
    authority_row=u.row(HERE/'host-authority.json');plan_row=u.row(HERE/'host-plan.json')
    base=json.loads(u.checked(hp['originalBuildPlan']).read_text())
    result=json.loads(u.checked(hp['actualBuildResult']).read_text());assert result['passed']is True
    audit=json.loads(u.checked(hp['actualComponentAudit']).read_text())
    assert result['componentAudit']==hp['actualComponentAudit'] and audit['passed']is True
    assert set(audit['imports'])<=set(base['selectedInterfaces']) and all(i.endswith('@0.2.10')for i in audit['imports'])
    assert audit['exports']==['wasi:http/incoming-handler@0.2.10']
    for r in list(base['pins'].values())+base['sourceFiles']:u.checked(r)
    assert hp['stdoutMarkerBytes']==hp['stderrMarkerBytes']==len(b'P1_STDOUT_OK\n')==len(b'P1_STDERR_OK\n')==13
    before=u.tree(base['sdkRoot']);output=Path(base['hostRoot']);assert not output.exists()
    os.umask(0o077);output.mkdir(mode=0o700);(output/'tmp').mkdir(mode=0o700)
    u.write(output/'input-before.json',dict(sdk=before,basePlan=hp['originalBuildPlan'],hostPlan=plan_row))
    def recheck():
        assert u.tree(base['sdkRoot'])==before and u.row(HERE/'host-authority.json')==authority_row and u.row(HERE/'host-plan.json')==plan_row
        for r in hp['additionalSourceFiles']+[hp['originalBuildPlan'],hp['actualBuildResult'],hp['actualComponentAudit'],audit['component'],audit['adapter']]+list(base['pins'].values())+base['sourceFiles']:u.checked(r)
    s=importlib.util.spec_from_file_location('original_owned_monitor',u.checked(base['pins']['monitor']));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    env={k:os.environ[k]for k in('HOME','USER','LOGNAME')if k in os.environ};env.update(PATH='/usr/bin:/bin',LC_ALL='C',LANG='C',TMPDIR=str(output/'tmp'))
    terminal=None;error=None;final=None
    argv=[base['pins']['node']['path'],str(HERE/'run-wasmtime-corrected.mjs'),str(output),base['buildRoot']]
    try:
        recheck();logs=output/'stock-wasmtime-three-requests';logs.mkdir(mode=0o700)
        terminal=m.monitor(argv,str(output),env,logs,180,authority_row)
        recheck();assert u.clean(terminal),'Host observer failed; complete raw evidence retained'
        host=json.loads((output/'host-result.json').read_text());assert host['passed']is True
    except BaseException as e:error=dict(type=type(e).__name__,message=str(e),stack=traceback.format_exc())
    finally:
        try:recheck();final=dict(unchanged=True,sdkFiles=len(before['files']),sdkLinks=len(before['links']))
        except BaseException as e:final=dict(unchanged=False,type=type(e).__name__,message=str(e),stack=traceback.format_exc())
        passed=error is None and final['unchanged']is True
        observation=dict(schemaVersion=1,state='NEXT_ADAPTER_C_HOST_PASSED_V1'if passed else'NEXT_ADAPTER_C_HOST_FAILURE_PRESERVED_V1',passed=passed,
                         hostPlan=plan_row,authority=authority_row,originalBuildPlan=hp['originalBuildPlan'],actualBuildResult=hp['actualBuildResult'],component=audit['component'],adapter=audit['adapter'],
                         argv=argv,capSeconds=180,terminal=u.row(output/'stock-wasmtime-three-requests/terminal.json')if terminal is not None else None,
                         rawExitCode=terminal['rawExitCode']if terminal is not None else None,cleanOwned=u.clean(terminal)if terminal is not None else False,
                         hostResult=u.row(output/'host-result.json')if(output/'host-result.json').is_file()else None,
                         error=error,finalProtection=final,engineJSNextExecuted=False)
        u.write(output/'result.json',observation);print(json.dumps(dict(result=u.row(output/'result.json'),passed=passed,error=error)),flush=True)
    return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
