"""Prepare genuine v3 Source bindings; no operational imports or actions."""
from pathlib import Path
import ast,difflib,hashlib,json
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'ownership-secret-artifact-tooling-candidate-v2'
HOLD=HERE.parent/'independent-ownership-secret-artifact-tooling-source-review-v2'

def d(path):
    p=Path(path);assert p.is_file()and not p.is_symlink();a=p.stat();h=hashlib.sha256()
    with p.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)

def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')

def family(index,rows):
    assert d(index['path'])==index;rows[index['path']]=index;root=Path(index['path']).parent;value=json.loads(Path(index['path']).read_bytes());names={'index.json'}
    for r in value['files']:
        n=r['path'];assert n not in names and not n.startswith('/')and all(x not in['','.','..']for x in n.split('/'));names.add(n);row=dict(r,path=str(root/n));assert d(row['path'])==row;rows[row['path']]=row
    assert {str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in root.rglob('*'))

def main():
    assert not(HERE/'index.json').exists();old_index=d(OLD/'index.json');assert old_index['sha256']=='8ebec1f8dd19af71a64faefd9527263054445704ae7f6595c78156e4567d1259'
    held=d(HOLD/'index.json');assert held['sha256']=='a682a56227daf43fcbafb7ff07bc81e350fbc8fcee2afc5f23015e9b201f9d55'
    refs=json.loads((HERE/'references.json').read_bytes());refs.update(schemaVersion=3,state='SECRET_OWNER355_ARTIFACT_TOOLING_FIXED_REFERENCES_V3',originalToolingRoot=str(HERE),heldPredecessor=dict(index=old_index,result=d(OLD/'results.json')),sourceCorrectionHold=dict(index=held,result=d(HOLD/'results.json')),sourceCorrectionContract=d(HOLD/'required-correction-contract.json'))
    for ix in[old_index,held]:
        if ix not in refs['families']:refs['families'].append(ix)
    for key in['sourceIndependentReview','rootAuthority','actualExport','reviewedPins','actualBootstrap','runtimeAuthority']:
        if key in refs:assert refs[key]is None
    write('references.json',refs)
    original=json.loads((OLD/'source-inputs.json').read_bytes());additional={r['path']:r for r in original['files']}
    for ix in refs['families']:family(ix,additional)
    for r in additional.values():assert d(r['path'])==r
    protected=refs['protectedInputLedger'];assert d(protected['path'])==protected;ledger=json.loads(Path(protected['path']).read_bytes());expanded={}
    for r in ledger['files']:
        row={k:r[k]for k in['path','sha256','bytes']};assert d(row['path'])==row;expanded[row['path']]=row
    assert len(expanded)==27729
    for path,row in additional.items():assert expanded.get(path,row)==row;expanded[path]=row
    assert not any(Path(path).is_relative_to(HERE)for path in additional)
    write('source-inputs.json',dict(schemaVersion=1,files=list(additional.values()),completeFamilies=refs['families'],protectedInputLedger=protected,expandedProtectedRows=27729,expandedUniquePaths=len(expanded),expandedLogicalBytes=sum(r['bytes']for r in expanded.values()),externalInputsReadAsDataOnly=True,originalSourcesOrHelpersInvoked=False,runtimeAuthenticatesEveryOwnDeclaredFile=True))
    copies=json.loads((OLD/'derivations.json').read_bytes());changes=[];patch=[]
    names=['artifact_tooling.py','bootstrap.mjs','pin_model.py','check-source.py','api-contract.json','future-source-review-contract.json','future-export-review-contract.json','future-config.template.json','future-reviewed-pins.template.json','future-root-pin-review.template.json','future-root-authority.template.json','references.json']
    for name in names:
        before=d(OLD/name);after=d(HERE/name);changes.append(dict(path=name,before=before,after=after))
        patch.extend(difflib.unified_diff((OLD/name).read_text().splitlines(keepends=True),(HERE/name).read_text().splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
    (HERE/'predecessor-to-v3.UNAPPLIED.patch').write_text(''.join(patch))
    write('derivations.json',dict(schemaVersion=1,predecessor=old_index,sourceHold=held,requiredCorrectionContract=refs['sourceCorrectionContract'],donors=copies['donors'],exactFunctionCopies=copies['exactFunctionCopies'],pinModel='Original secret355 whole-frame model; own v3 protocol/context changes only, genuine e872/f894/native/frozen fields unaltered',changedPredecessorFiles=changes,addedSourceFiles=['prepare-source.py','seal-source.py','README.md','preparation-history.json','correction-models.json','source-inputs.json','pure-results.json'],corrections=['M1 full own indexed source-inputs.files captured in Python and JS before custom imports/action and retained for final/failure/recheck','M2 observed child-kill primitive distinct from unknown/unproved timeout cause; every error/overflow/incomplete path still refused'],rootOrSourcePeerIssued=False,operationalSemanticsOrMetadataProjected=False))
    print(json.dumps(dict(sourceDataPrepared=True,additionalDeclaredFiles=len(additional),completeFamilies=len(refs['families']),expandedUniquePaths=len(expanded),oldSourceModified=False,actionsInvoked=False)))

if __name__=='__main__':main()
