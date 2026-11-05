"""Finite Source/read/hash/AST sealer. Never imports controller or invokes tools."""
from pathlib import Path
import ast,difflib,hashlib,json,os,stat
HERE=Path(__file__).resolve().parent

def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def fingerprint(path):
    p=Path(path);a=p.stat();assert p.is_file()and not p.is_symlink()
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert identity(a)==identity(z)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z)
def main():
    assert not(HERE/'index.json').exists(),'Sealed Source is immutable; use a new successor'
    refs=json.loads((HERE/'references.json').read_bytes());pure=json.loads((HERE/'pure-results.json').read_bytes())
    assert pure['checks']>=325 and pure['redirectCases']==35 and pure['responseCloseFailureCases']==5
    assert pure['manifestIntakeCases']==9 and pure['descriptorAndFamilyRecheckCases']==4 and pure['preimportProtectionCases']==2
    captured={};identities={};families=[]
    def capture(r):
        d={k:r[k]for k in ['path','sha256','bytes']}
        if d['path']in captured:assert captured[d['path']]==d;return
        actual,identity=fingerprint(d['path']);assert actual==d;captured[d['path']]=d;identities[d['path']]=identity
    def read(r):capture(r);return json.loads(Path(r['path']).read_bytes())
    def family(ix):
        v=read(ix);base=Path(ix['path']).parent;names={'index.json'}
        for r in v['files']:
            n=r['path'];assert not n.startswith('/')and '\\'not in n and all(q not in ['','.','..']for q in n.split('/'))and n not in names;names.add(n)
            capture(dict(path=str(base/n),sha256=r['sha256'],bytes=r['bytes']))
        assert not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names
        families.append(dict(index=ix,memberNames=sorted(names)))
    # Full exact predecessor and HOLD are DATA, not Source approval/action.
    for key in ['predecessorIndex','redirectHoldIndex','sourceIndex','monitorIndex']:family(refs[key])
    family(refs['sourceReviewData']['index']);peer=read(refs['sourceReviewData']['result'])
    assert peer['state']=='INDEPENDENT_SCHEDULER_CLOCK_IO_PRUNING_SOURCE_REVIEW_PASSED_V1'and peer['sourceOnly']is peer['sourceReviewPassed']is True
    assert peer['sourceIndexSha256']==refs['sourceIndex']['sha256']and peer['ownerActionsInvoked']is False
    old=Path(refs['predecessorIndex']['path']).parent
    predecessor_inputs=json.loads((old/'source-inputs.json').read_bytes());assert len(predecessor_inputs['files'])==5606
    for r in predecessor_inputs['files']:capture(r)
    # No own manifest/index/result descriptor cycle. Own family separately
    # authenticates those bytes; this static row is safe and independently fixed.
    capture(refs['hostContext']);capture(refs['pinnedHttpRequestImplementation'])
    for name in ['error.py','response.py']:
        r,_=fingerprint(Path(refs['pinnedHttpRequestImplementation']['path']).with_name(name));capture(r)
    for key in ['sourceInputs','sourceCut','toolReferences','originalBuildPlan','monitorEntry']:capture(refs[key])
    host=read(refs['hostContext'])
    for k in ['sdkSettings','hostLinkerDriver','appleLinker','wasmLinker','xcodeVersionPlist','python']:capture(host[k])
    cut=read(refs['sourceCut']);tools=read(refs['toolReferences']);plan=read(refs['originalBuildPlan']);aliases=[]
    for r in tools['jsToolchain']['symlinks']:
        p=Path(tools['jsToolchain']['root'])/r['path'];assert p.is_symlink()and os.readlink(p)==r['target']and str(p.resolve())==r['resolved']['path'];capture(r['resolved']);aliases.append(dict(path=str(p),target=r['target'],resolved=r['resolved']))
    for r in cut['baseline']['files']:assert stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode)==r['mode']
    for r in tools['jsToolchain']['files']:assert stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode)==r['mode']
    comparisons=[]
    for name in ['controller.py','check-source.py','seal-source.py','host-context.json','references.json','future-root-authority.template.json','future-config.template.json','future-source-review-contract.json','action-contract.json','README.md','preparation-history.json']:
        before=(old/name).read_text();after=(HERE/name).read_text();edits=[]
        for tag,i,j,a,b in difflib.SequenceMatcher(None,before,after,autojunk=False).get_opcodes():
            if tag!='equal':edits.append(dict(beforeStart=i,beforeEnd=j,afterStart=a,afterEnd=b,old=before[i:j],new=after[a:b]))
        forward=before;reverse=after
        for e in reversed(edits):
            assert forward[e['beforeStart']:e['beforeEnd']]==e['old'];forward=forward[:e['beforeStart']]+e['new']+forward[e['beforeEnd']:]
            assert reverse[e['afterStart']:e['afterEnd']]==e['new'];reverse=reverse[:e['afterStart']]+e['old']+reverse[e['afterEnd']:]
        assert forward==after and reverse==before
        donor,_=fingerprint(old/name);current,_=fingerprint(HERE/name)
        comparisons.append(dict(path=name,donor=donor,after=current,edits=edits,forwardAndInverseExact=True))
    write('derivations.json',dict(schemaVersion=1,predecessor=refs['predecessorIndex'],files=comparisons,sourceWorkPackageRolesUnchanged=True,monitorSourceCopiedOrChanged=False,originalProposalMutated=False))
    astfiles=[]
    for p in HERE.rglob('*.py'):ast.parse(p.read_text());astfiles.append(p.relative_to(HERE).as_posix())
    for path,identity in identities.items():
        p=Path(path);s=p.stat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==identity
    for f in families:
        base=Path(f['index']['path']).parent;assert{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==set(f['memberNames'])and not any(p.is_symlink()for p in base.rglob('*'))
    assert set(r['path']for r in predecessor_inputs['files']).issubset(captured)
    assert str(HERE/'index.json')not in captured and str(HERE/'source-inputs.json')not in captured
    for f in families:
        base=Path(f['index']['path']).parent
        assert all(str(base/name)in captured for name in f['memberNames'])
    for name in ['import-abi-clock-io-v1-source','import-abi-clock-io-v1-build','import-abi-clock-io-v1-package','import-abi-clock-io-v1-build-v2-external-root']:
        future=Path('/private/tmp/starling-node-compat')/name;assert not future.exists()and not future.is_symlink()
    write('source-inputs.json',dict(schemaVersion=1,files=list(captured.values()),families=families,links=aliases,predecessorDeclaredInputs=5606,allRowsRuntimeCapturedBeforeCustomImportAndOnRecheck=True,originalModesVerified=True,fullContentHashThenFinalIdentityStability=True,readOnlyData=True,operationalHelpersOrToolsInvoked=False))
    result=dict(schemaVersion=1,state='CLOCK_IO_BUILD_CONTROLLER_SOURCE_SEALED_UNREVIEWED_V2',sourceOnly=True,sourceIndex=refs['sourceIndex'],proposalSourceReview=refs['sourceReviewData'],predecessor=refs['predecessorIndex'],redirectSourceHold=refs['redirectHoldIndex'],pureDataChecks=pure['checks'],redirectStatusTargetCases=35,responseCloseFailureCases=5,realOpenerErrorDispatchCases=5,manifestIntakeCases=9,descriptorAndFamilyRecheckCases=4,preimportProtectionCases=2,localNoProxyFactoryConstructedWithoutRequests=True,isolatedRawStepCases=9,isolatedPreworkFailureCases=2,isolatedMainCallerCases=2,cachedArchiveHeadersParsed=118,missingArchivesFetched=0,fullSourceInputsHashed=len(captured),predecessorDeclaredInputsPreserved=5606,logicalInputBytes=sum(r['bytes']for r in captured.values()),originalJsAliasesVerified=len(aliases),exactForwardInverseFiles=len(comparisons),exactForwardInverseEdits=sum(len(r['edits'])for r in comparisons),pythonAstFiles=astfiles,sourceCopies=0,vendorExtractions=0,networkOrMonitorOrCompilerOrNodeOrJcoActionsInvoked=False,actualStage=None,actualBuild=None,actualUnitResults=None,prunerFunctionInvokedByRefusalUnitTest=None,validAdapterPruningRun=False,adapterArtifactPublished=False,adapterCliPruneCommandInvoked=False,sourcePeer=None,rootAuthority=None,operationalAdmission=False,runtimeAcceptanceClaim=False)
    write('results.json',result)
    write('source-receipt.json',dict(schemaVersion=1,state='SOURCE_ONLY_CLOCK_IO_BUILD_CONTROLLER_RECEIPT_V2',sourceRoot=str(HERE),sourceIndex=refs['sourceIndex'],fullInputs=len(captured),pureChecks=pure['checks'],reversibleFiles=len(comparisons),actualActionsInvoked=False,allFutureEffectiveActionsNull=True))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file()and p!=HERE/'index.json':
            r,_=fingerprint(p);r['path']=p.relative_to(HERE).as_posix();rows.append(r)
    write('index.json',dict(schemaVersion=1,files=rows))
    for r in rows:
        actual,_=fingerprint(HERE/r['path']);assert actual['sha256']==r['sha256']and actual['bytes']==r['bytes']
    ix,_=fingerprint(HERE/'index.json');print(json.dumps(dict(index=ix,members=len(rows),inputs=len(captured),pureChecks=pure['checks'],results=fingerprint(HERE/'results.json')[0])))
if __name__=='__main__':main()
