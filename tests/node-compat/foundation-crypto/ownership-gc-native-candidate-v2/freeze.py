"""Future freezer wrapper; explicit-root donor calls, no global rebinding."""
from pathlib import Path
import importlib.util,json,sys
import context as C,guard
from data_io import read,regular,descriptor
def freeze(config):
    frame=guard.authorize(config,'freeze');root=frame['root'];metadata=read(root['metadata']);C.metadata_model(metadata)
    frame['captured'].append(root['metadata'])
    assert root['engine']['path'].startswith(C.WORK+'/artifacts/')and root['metadata']['path']==root['engine']['path']+'.build.json'
    assert metadata['engineSha256']==root['engine']['sha256']and metadata['engineBytes']==root['engine']['bytes']
    assert not Path(C.FREEZE).exists(),'GC freeze must be an absent, separate root'
    common=guard.load_common(frame)
    active=descriptor(Path(__file__).resolve());entry=Path(__file__).resolve();guard_path=entry.parent/'guard.py'
    frame.update(enginePath=root['engine']['path'],metadata=root['metadata'],active=active,donor=descriptor(Path(C.TOOLS)/'freeze-engine.py'),entryPath=str(entry),guardPath=str(guard_path))
    spec=importlib.util.spec_from_file_location('gc_explicit_root_freezer_body',entry.parent/'freezer-body.py');body=importlib.util.module_from_spec(spec);spec.loader.exec_module(body)
    try:return body.freeze(frame,common,guard)
    finally:guard.recheck(frame)
if __name__=='__main__':assert len(sys.argv)==2;freeze(json.loads(sys.argv[1]))
