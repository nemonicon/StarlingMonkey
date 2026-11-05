"""Dormant export/bootstrap action; two separate future phases, zero engine calls."""
from pathlib import Path
import hashlib,importlib.util,json,sys,os
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-gc-pin-tooling-candidate-v1')
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

def action(config_row,phase):
    assert phase in ('export','bootstrap') and __debug__ and sys.dont_write_bytecode
    assert not any(os.environ.get(k)for k in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH'))
    config=primitive_read(config_row);ix=config['toolingIndex'];assert ix['path']==str(OWN/'index.json')
    index=primitive_read(ix);names=set()
    for r in index['files']:
        name=r['path'];assert name not in names and name and not name.startswith('/') and all(p not in ('','.','..')for p in name.split('/'))
        names.add(name);primitive(dict(path=str(OWN/name),sha256=r['sha256'],bytes=r['bytes']))
    assert not any(p.is_symlink()for p in OWN.rglob('*'))
    assert {p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}==names|{'index.json'}
    spec=importlib.util.spec_from_file_location('crypto_gc_pin_tooling_guard',OWN/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    frame=guard.authorize(config_row,phase)
    try:
        common=guard.load_common(frame)
        if phase=='export':
            return export_phase(frame,common,guard)
        spec=importlib.util.spec_from_file_location('genuine_gc_readonly_bootstrap_body',OWN/'bootstrap-body.py')
        body=importlib.util.module_from_spec(spec);spec.loader.exec_module(body)
        return body.bootstrap(frame,common,guard)
    finally:
        guard.recheck_frame(frame)


def export_phase(frame,common,guard):
    spec=importlib.util.spec_from_file_location('genuine_gc_unreviewed_candidate_body',OWN/'export-body.py')
    body=importlib.util.module_from_spec(spec);spec.loader.exec_module(body)
    candidate=body.candidate('gc-off',Path(guard.FREEZE),common)
    native=frame['_nativeGuard'];native.C.metadata_model(json.loads(common.checked(Path(guard.FREEZE)/'gc-off.engine.wasm.build.json',candidate['receiptSha256']).read_bytes()))
    document=dict(schemaVersion=1,state='UNREVIEWED_CRYPTO_OWNER355_ISOLATED_GC_PIN_CANDIDATE_V1',variants={n:candidate if n=='gc-off'else None for n in ('normal-off','normal-runtime','gc-off','disabled-off')},requiresIndependentReviewAndNewRootNativeReview=True,consumerPinsModified=False,guestExecutedByExporter=False,toolingProvenance=guard.provenance(frame))
    output=frame['root']['pinCandidateOutput'];assert output==guard.BUILD_OUTPUT+'/gc-pin.UNREVIEWED.json'
    guard.recheck_frame(frame)
    from data_io import write
    created=write(output,document)  # Genuine exclusive 'x' output; never adopt a pin.
    frame['toolingFrame']['expectedCandidate']=created
    guard.recheck_frame(frame);return document

if __name__=='__main__':
    assert len(sys.argv)==3
    print(json.dumps(action(json.loads(sys.argv[2]),sys.argv[1])))
