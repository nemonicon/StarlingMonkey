"""Seal Source-only v3; no helper, entry, monitor or API invocation."""
from pathlib import Path
import ast,hashlib,json,os,re
HERE=Path(__file__).resolve().parent
snapshots={}

def d(path):
    p=Path(path);assert p.is_file()and not p.is_symlink();a=p.stat();h=hashlib.sha256()
    with p.open('rb')as stream:
        for b in iter(lambda:stream.read(4*1024*1024),b''):h.update(b)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns);assert identity(a)==identity(z)
    row=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size);current=(row,identity(z),str(p.resolve()))
    if str(p)in snapshots:assert snapshots[str(p)]==current
    snapshots[str(p)]=current
    return row

def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def family(index,all_rows):
    assert d(index['path'])==index;all_rows[index['path']]=index;root=Path(index['path']).parent;v=json.loads(Path(index['path']).read_bytes());names={'index.json'}
    for r in v['files']:
        name=r['path'];assert name not in names and not name.startswith('/')and all(x not in['','.','..']for x in name.split('/'));names.add(name);row=dict(r,path=str(root/name));assert d(row['path'])==row;all_rows[row['path']]=row
    assert{str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in root.rglob('*'))

def patch_model(source,patch,reverse=False):
    old=source.splitlines(keepends=True);lines=patch.splitlines(keepends=True);out=[];cursor=0;i=0
    while i<len(lines):
        m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i])
        if not m:i+=1;continue
        start=int(m[3]if reverse else m[1])-1;assert start>=cursor;out.extend(old[cursor:start]);cursor=start;i+=1
        while i<len(lines)and not lines[i].startswith('@@'):
            line=lines[i];i+=1
            if line.startswith(('---','+++')):continue
            sign=line[:1];value=line[1:]
            if reverse:sign={'+':'-','-':'+',' ':' '}.get(sign,sign)
            assert sign in[' ','+','-']
            if sign in[' ','-']:assert old[cursor]==value;cursor+=1
            if sign in[' ','+']:out.append(value)
    return ''.join(out+old[cursor:])

def main():
    assert not(HERE/'index.json').exists();refs=json.loads((HERE/'references.json').read_bytes());inputs=json.loads((HERE/'source-inputs.json').read_bytes());pure=json.loads((HERE/'pure-results.json').read_bytes());models=json.loads((HERE/'correction-models.json').read_bytes());syntax=json.loads((HERE/'evidence/js-syntax/terminal.json').read_bytes());deriv=json.loads((HERE/'derivations.json').read_bytes())
    assert refs['schemaVersion']==3 and refs['originalToolingRoot']==str(HERE)
    assert pure['state']=='SECRET_ARTIFACT_TOOLING_SOURCE_PURE_DATA_CHECKS_PASSED_V3'and pure['operationalEntryBodiesInvoked']is pure['verifierOrMonitorInvoked']is pure['exportOrBootstrapInvoked']is False
    assert models['manifestRows']==241 and models['initialMissingOrBytesNegatives']==2 and models['finalFailureMissingBytesIdentityNegatives']==3 and len(models['terminalModels'])==6
    assert syntax['rawExitCode']==0 and syntax['syntaxCheckerUsed']is syntax['grammarOnly']is True and syntax['source']==d(HERE/'bootstrap.mjs')and syntax['node']==refs['node']
    for row in syntax['streams'].values():assert d(row['path'])==row and row['bytes']==0
    rows={}
    for row in inputs['files']:assert d(row['path'])==row;rows[row['path']]=row
    for ix in refs['families']:family(ix,rows)
    assert d(inputs['protectedInputLedger']['path'])==inputs['protectedInputLedger']==refs['protectedInputLedger']
    protected=json.loads(Path(inputs['protectedInputLedger']['path']).read_bytes());assert len(protected['files'])==27729
    for r in protected['files']:
        row={k:r[k]for k in['path','sha256','bytes']};assert d(row['path'])==row and rows.get(row['path'],row)==row;rows[row['path']]=row
    assert len(rows)==inputs['expandedUniquePaths']==27797
    for row in rows.values():assert d(row['path'])==row
    final_family_rows={}
    for ix in refs['families']:family(ix,final_family_rows)
    patch=(HERE/'predecessor-to-v3.UNAPPLIED.patch').read_text();patches={part.splitlines()[0][6:]:part for part in re.split(r'(?m)(?=^--- a/)',patch)if part.startswith('--- a/')};assert len(patches)==12
    for r in deriv['changedPredecessorFiles']:
        assert d(r['before']['path'])==r['before']and d(r['after']['path'])==r['after'];a=Path(r['before']['path']).read_text();b=Path(r['after']['path']).read_text();assert patch_model(a,patches[r['path']])==b and patch_model(b,patches[r['path']],True)==a
    asts=0
    for p in HERE.glob('*.py'):ast.parse(p.read_text());asts+=1
    for p in HERE.glob('*.json'):json.loads(p.read_bytes())
    assert asts==5
    for name in['future-config.template.json','future-reviewed-pins.template.json','future-root-authority.template.json','future-root-pin-review.template.json']:
        v=json.loads((HERE/name).read_bytes());assert v.get('rootAuthority')is None and v.get('actualProof')is None
    assert all(not Path(str(Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v3'))+suffix).exists()for suffix in['-export-normal-off','-export-normal-off-external-root','-bootstrap-normal-off','-bootstrap-normal-off-external-root','-bootstrap-js-normal-off'])
    write('closure-verification.json',dict(schemaVersion=1,additionalDeclaredFiles=241,protectedInputRows=27729,expandedExternalPaths=27797,logicalExternalBytes=sum(r['bytes']for r in rows.values()),completeSourceFamilies=len(refs['families']),initialAndFinalExternalHashRecheck=True,sourceInputCycles=False,exactPredecessorForwardReverseFiles=12,pythonAstFiles=5,syntaxCheckerUsed=True,nodeSyntaxRawExitCode=0,ownerActionsInvoked=False,hostActionsInvoked=False,exportOrBootstrapActionsInvoked=False))
    write('results.json',dict(schemaVersion=3,state='SECRET_OWNER355_ARTIFACT_TOOLING_SOURCE_CANDIDATE_SEALED_UNREVIEWED_V3',sourceOnly=True,sourcePeerRequired=True,heldPredecessor=refs['heldPredecessor'],sourceCorrectionHold=refs['sourceCorrectionHold'],sourceCorrectionContract=refs['sourceCorrectionContract'],sourceIndependentReview=None,rootAuthority=None,
        actualVerifierReview=refs['actualVerifierReview'],nativeSourceIndex=refs['nativeSourceIndex'],verifierSourceIndex=refs['verifierSourceIndex'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,rawMetadataFields=75,
        exportEntryImplemented=True,pinModelImplemented=True,pythonBootstrapCliImplemented=True,jsBootstrapHarnessApiImplemented=True,completeOwnDeclaredInputProtectionImplemented=True,unknownTimeoutCauseLabelsImplemented=True,
        pureChecks=pure['checks'],pythonAstFiles=asts,exactDonorFunctionCopies=7,exactPredecessorForwardReverseFiles=12,additionalDeclaredFiles=241,protectedInputRows=27729,fullyHashedUniqueExternalPaths=len(rows),logicalExternalBytes=sum(r['bytes']for r in rows.values()),externalSourceFamilies=refs['families'],fullInputLedgerRehash=True,finalExternalIdentityStabilityPassed=True,
        closureVerification=d(HERE/'closure-verification.json'),sourceInputs=d(HERE/'source-inputs.json'),pureModels=d(HERE/'pure-results.json'),correctionModels=d(HERE/'correction-models.json'),syntaxProof=d(HERE/'evidence/js-syntax/terminal.json'),syntaxCheckerUsed=True,nodeSyntaxRawExitCode=0,jsGrammarExecuted=True,nodeSyntaxOnly=True,
        ownerActionsInvoked=False,hostActionsInvoked=False,exportOrBootstrapActionsInvoked=False,operationalModulesImported=False,completeVerifierOrMonitorInvoked=False,actualExport=None,reviewedPins=None,actualBootstrap=None,runtimeAuthority=None,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False))
    write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNEXECUTED_SECRET_ARTIFACT_TOOLING_SOURCE_V3',result=d(HERE/'results.json'),closure=d(HERE/'closure-verification.json'),derivations=d(HERE/'derivations.json'),sourceInputs=d(HERE/'source-inputs.json'),history=d(HERE/'preparation-history.json'),syntaxProof=d(HERE/'evidence/js-syntax/terminal.json'),sourceOnly=True,sourceIndependentReview=None,rootAuthority=None,syntaxCheckerUsed=True,ownerActionsInvoked=False,hostActionsInvoked=False,exportOrBootstrapActionsInvoked=False,engineExecuted=False))
    members=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():row=d(p);members.append(dict(path=str(p.relative_to(HERE)),sha256=row['sha256'],bytes=row['bytes']))
    write('index.json',dict(schemaVersion=1,files=members))
    assert{r['path']for r in members}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for r in members:assert d(HERE/r['path'])==dict(r,path=str(HERE/r['path']))
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),receipt=d(HERE/'source-receipt.json'),members=len(members),actualExport=None,actualBootstrap=None,sourceIndependentReview=None)))

if __name__=='__main__':main()
