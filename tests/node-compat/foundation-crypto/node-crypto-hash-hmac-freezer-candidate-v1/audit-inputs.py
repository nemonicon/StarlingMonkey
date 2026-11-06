"""Read/hash Source intake; no bootstrap/admission/freezer/monitor calls."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys,time
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def main():
    started=time.monotonic();s=importlib.util.spec_from_file_location('own_inert_freezer_readonly_primitives',OWN/'entry.py');e=importlib.util.module_from_spec(s);s.loader.exec_module(e)
    refs=read(OWN/'references.json');inputs=e.read(refs['sourceInputs']);rows={};ids={}
    def add(d):
        if d['path']in rows:assert rows[d['path']]==d
        else:rows[d['path']]=d
    for d in inputs['files']:add(d)
    for ix in inputs['families']:
        for d in e.family(ix):add(d)
    for d in e.read(refs['artifactLedger'])['files']:add(d)
    for d in e.read(refs['referenceAdditions'])['files']:add(d)
    for d in rows.values():p=e.checked(d);ids[d['path']]=e.identity(p)
    trees=e.read(refs['artifactTrees'])['trees'];e.trees(trees,rows)
    aliases=e.read(refs['referenceAliases'])
    for a in aliases['symlinks']:assert Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve(strict=True))==a['resolved']
    for a in aliases['archiveHardlinks']:
        x=Path(a['path']).stat();y=Path(a['target']).stat();assert(x.st_dev,x.st_ino)==(y.st_dev,y.st_ino)
    index=refs['indexException']['currentActual'];assert stat.S_IMODE(e.checked(index).stat().st_mode)==0o600
    # This is the existing pure current-index DATA decoder, not an operational
    # adapter bootstrap, helper, Git command, or model-global substitution.
    spec=importlib.util.spec_from_file_location('original_current_index_DATA_only',e.checked(refs['indexModel']));model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    semantics=model.decode(e.checked(index).read_bytes(),e.checked(refs['baselineTreeTransport']).read_bytes());assert semantics['entries']==742
    for d in rows.values():assert e.identity(e.physical(d['path']))==ids[d['path']]
    result=dict(schemaVersion=1,state='HASH_HMAC357_FREEZER_SOURCE_FULL_CURRENT_INPUT_INTAKE_PASSED_V1',uniqueFiles=len(rows),logicalBytes=sum(d['bytes']for d in rows.values()),families=len(inputs['families']),historicalCurrentLedgerFiles=21451,completeTrees=len(trees),allTreeRegularFilesInCheckedClosure=True,additionalTreeReferenceFiles=len(e.read(refs['referenceAdditions'])['files']),symlinkAliases=len(aliases['symlinks']),archiveHardlinks=len(aliases['archiveHardlinks']),currentIndexMode=0o600,currentIndexBaselineEntries=742,originalIndexPreimageRetained=False,indexStatOnlyDeltaProved=False,originalBuildAccepted=False,allReadIdentitiesStable=True,elapsedOperationalSeconds=time.monotonic()-started,producerOrAdmissionOrFreezeOrEngineGuestCryptoInvoked=False)
    (OWN/'input-audit-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
