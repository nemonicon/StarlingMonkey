"""Public dormant export/bootstrap entry. Standard-only own authentication before imports."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
OWN=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler/resource-pin-tooling-candidate-v1')
def initial(row):
 p=Path(row['path']);assert p.is_absolute()and str(p)==row['path']and '..'not in p.parts
 for q in(p,*p.parents):assert not q.is_symlink()
 a=p.stat();assert p.is_file();b=p.read_bytes();z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 assert len(b)==row['bytes']and hashlib.sha256(b).hexdigest()==row['sha256'];return b
def action(config_row,phase):
 assert __debug__ and sys.dont_write_bytecode and Path(__file__).resolve().parent==OWN
 config=json.loads(initial(config_row));index_row=config['toolingIndex'];assert index_row['path']==str(OWN/'index.json');index=json.loads(initial(index_row));names=set()
 for row in index['files']:
  name=row['path'];assert name and not name.startswith('/')and '\\'not in name and all(p not in('','.','..')for p in name.split('/'))and name not in names;names.add(name);initial(dict(path=str(OWN/name),sha256=row['sha256'],bytes=row['bytes']))
 assert not any(p.is_symlink()for p in OWN.rglob('*'))and{p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}==names|{'index.json'}
 spec=importlib.util.spec_from_file_location('resource_pin_phase_guard',OWN/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);frame=g.authorize(config_row,phase)
 try:
  model=g.load_exact(next(r for r in frame['ownRows']if r['path']==str(OWN/'pin_model.py')),'resource342_pin_data_model')
  expected=model.candidate(frame['receipt'],frame['metadata'],frame['refs'],config['toolingIndex'])
  if phase=='export':
   document=model.unreviewed_document(expected);g.recheck(frame)
   assert not g.EXPORT_ROOT.exists()and not g.EXPORT_ROOT.is_symlink();g.EXPORT_ROOT.mkdir(mode=0o700)
   directory=os.open(g.EXPORT_ROOT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
   try:
    identity=os.fstat(directory);fd=os.open(g.EXPORT_FILE.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
    with os.fdopen(fd,'w')as out:json.dump(document,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
    actual=g.EXPORT_ROOT.lstat();assert not g.EXPORT_ROOT.is_symlink()and(actual.st_dev,actual.st_ino)==(identity.st_dev,identity.st_ino)
   finally:os.close(directory)
   assert g.read(dict(path=str(g.EXPORT_FILE),sha256=hashlib.sha256(g.EXPORT_FILE.read_bytes()).hexdigest(),bytes=g.EXPORT_FILE.stat().st_size))==document
   return dict(schemaVersion=1,state='RESOURCE342_NORMAL_OFF_PIN_CANDIDATE_EXPORTED_UNREVIEWED_V1',candidate=dict(path=str(g.EXPORT_FILE),sha256=hashlib.sha256(g.EXPORT_FILE.read_bytes()).hexdigest(),bytes=g.EXPORT_FILE.stat().st_size),toolingIndex=config['toolingIndex'],resourceSourceIndex=config['resourceSourceIndex'],freezerIndex=config['freezerIndex'],rootAuthority=config['rootAuthority'],actualArtifactReview=frame['refs']['actualArtifactReview'],requiresIndependentExportAndNewRootValidationPinReview=True,engineExecuted=False,bootstrapInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
  root=frame['root'];pair=root['independentExportReview'];pin=frame['reviewedPin']
  return dict(schemaVersion=1,state='RESOURCE342_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V1',variant='normal-off',resourceSourceIndexSha256=g.RESOURCE_SHA,freezerSourceIndexSha256=g.FREEZER_SHA,toolingIndex=config['toolingIndex'],enginePath=pin['enginePath'],engine=frame['refs']['engine'],metadataDescriptor=frame['refs']['metadata'],metadata=frame['metadata'],pin=pin,selectedManifests=frame['selectedManifests'],selectedManifestPaths=[r['path']for r in frame['metadata']['selectedModuleManifests']],originalToolingRoot=str(OWN),configuredSourceRoot=str(g.SOURCE),sourceRoot=str(g.FROZEN/'source'),frozenSourceRoot=str(g.FROZEN/'source'),componentizeSourceRoot=frame['refs']['componentizeSourceRoot'],freezeRoot=str(g.FROZEN),rootAuthority=config['rootAuthority'],reviewedPinsSha256=root['reviewedPins']['sha256'],rootPinReviewSha256=root['rootPinReview']['sha256'],actualArtifactReview=frame['refs']['actualArtifactReview'],independentExportReview=pair,validationBootstrapOnly=True,operationalAdmission=False,engineExecuted=False,componentOrGuestExecuted=False,runtimeAcceptanceClaim=False)
 finally:g.recheck(frame)
if __name__=='__main__':assert len(sys.argv)==3;print(json.dumps(action(json.loads(sys.argv[2]),sys.argv[1])),flush=True)
