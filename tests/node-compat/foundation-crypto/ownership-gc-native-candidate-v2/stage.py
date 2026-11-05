"""Future exclusive source publication; never called during source preparation."""
from pathlib import Path
import json,os,shutil,stat,subprocess,sys
import context as C,guard
from data_io import read,regular,write
def stage(config):
    frame=guard.authorize(config,'stage');dest=Path(C.SOURCE)
    assert not dest.exists()and not dest.is_symlink()and not Path(C.JOURNAL).exists()
    assert shutil.disk_usage(dest.parent).free>=2*1024**3
    assert (Path(C.NORMAL_SOURCE)/'.git/HEAD').read_text()==C.BASE+'\n'
    assert not(Path(C.NORMAL_SOURCE)/'.git/objects/info/alternates').exists()
    result=dict(schemaVersion=1,state='CRYPTO_OWNER355_GC_SOURCE_STAGE_STARTED',sourceIndexSha256=frame['sourceIndex']['sha256'],destination=C.SOURCE,commands=[],nativeBuildOrRuntimeInvoked=False)
    try:
        for command in [['git','clone','--no-local','--no-checkout',C.NORMAL_SOURCE,C.SOURCE],['git','-C',C.SOURCE,'checkout','--detach',C.BASE]]:
            p=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
            result['commands'].append(dict(argv=command,rawExitCode=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()));assert p.returncode==0
        assert not(dest/'.git/objects/info/alternates').exists()
        for r in frame['stageInputs']['files']:
            original=regular(r['original']);target=dest/r['path']
            for q in [target,*target.parents]:assert not q.is_symlink()
            target.parent.mkdir(parents=True,exist_ok=True)
            with original.open('rb')as src,target.open('wb'if target.exists()else'xb')as out:shutil.copyfileobj(src,out,1024*1024);out.flush();os.fsync(out.fileno())
            target.chmod(r['mode']);assert target.stat().st_ino!=original.stat().st_ino
            regular({**r['original'],'path':str(target)})
        guard.recheck(frame)
        result.update(state='CRYPTO_OWNER355_GC_SOURCE_STAGE_COMPLETE_UNREVIEWED_V1',copiedPaths=len(frame['stageInputs']['files']),nativeSourceFiles=355,toolRows=922,sourceIndexSha256=frame['sourceIndex']['sha256'],metadataProjected=False,operationalAdmission=False)
    except BaseException as error:result.update(state='FAILED_GC_SOURCE_STAGE_PARTIAL_RETAINED',errorType=type(error).__name__);raise
    finally:write(C.JOURNAL,result)
    return result
if __name__=='__main__':
    assert len(sys.argv)==2;print(json.dumps(stage(json.loads(sys.argv[1]))))
