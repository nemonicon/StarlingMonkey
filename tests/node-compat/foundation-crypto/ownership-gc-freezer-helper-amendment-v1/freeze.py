"""Dormant amendment freezer entry. No action until explicit two-authority config."""
from pathlib import Path
import hashlib,importlib.util,json,sys,os
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-gc-freezer-helper-amendment-v1')

def primitive(row):
    path=Path(row['path']);assert path.is_absolute() and '..' not in path.parts
    for p in (path,*path.parents):assert not p.is_symlink()
    a=path.stat();assert path.is_file();h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=path.stat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    assert h.hexdigest()==row['sha256'] and a.st_size==row['bytes'];return path

def primitive_read(row):
    raw=primitive(row).read_bytes()
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
    return json.loads(raw)

def freeze(config_row):
    assert __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k) for k in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH'))
    config=primitive_read(config_row);ix=config['helperAmendmentIndex']
    assert ix['path']==str(OWN/'index.json')
    value=primitive_read(ix);names=set();rows=[config_row,ix]
    for r in value['files']:
        name=r['path'];assert name not in names and name and not name.startswith('/') and all(p not in ('','.','..') for p in name.split('/'))
        names.add(name);row=dict(path=str(OWN/name),sha256=r['sha256'],bytes=r['bytes']);primitive(row);rows.append(row)
    assert all(not p.is_symlink() for p in OWN.rglob('*'))
    assert {p.relative_to(OWN).as_posix() for p in OWN.rglob('*') if p.is_file()}==names|{'index.json'}
    spec=importlib.util.spec_from_file_location('gc_helper_amendment_controller',OWN/'controller.py')
    controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
    _,_,captured,_,families=controller.authorize(config_row)
    controller.recheck(captured,families)
    spec=importlib.util.spec_from_file_location('gc_helper_amendment_guard',OWN/'amendment-guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    frame=guard.authorize(config_row,controller)
    try:
        native=frame['_genuineNativeGuard'];root=frame['root'];metadata=controller.read(root['metadata']);native.C.metadata_model(metadata)
        frame['captured'].append(root['metadata'])
        assert root['engine']['path'].startswith(native.C.WORK+'/artifacts/') and root['metadata']['path']==root['engine']['path']+'.build.json'
        assert metadata['engineSha256']==root['engine']['sha256'] and metadata['engineBytes']==root['engine']['bytes']
        assert not Path(native.C.FREEZE).exists(),'GC freeze root must still be absent'
        common=guard.load_common(frame)
        active=next(r for r in captured if r['path']==str(OWN/'freeze.py'))
        donor_path=Path(native.C.TOOLS)/'freeze-engine.py'
        donor=next(r for r in frame['captured'] if r['path']==str(donor_path))
        frame.update(enginePath=root['engine']['path'],metadata=root['metadata'],active=active,donor=donor,entryPath=str(OWN/'freeze.py'),guardPath=str(OWN/'amendment-guard.py'))
        spec=importlib.util.spec_from_file_location('gc_helper_amendment_freezer_body',OWN/'freezer-body.py')
        body=importlib.util.module_from_spec(spec);spec.loader.exec_module(body)
        return body.freeze(frame,common,guard)
    finally:
        guard.recheck(frame)

if __name__=='__main__':
    assert len(sys.argv)==2
    freeze(json.loads(sys.argv[1]))
