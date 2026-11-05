"""Source-only closure sealer. Does not import controller or run any tool."""
from pathlib import Path
import ast,hashlib,json,os,stat

HERE=Path(__file__).resolve().parent
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def fingerprint(path):
    p=Path(path);a=p.stat();need=p.is_file()and not p.is_symlink();assert need
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert identity(a)==identity(z)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z)
def main():
    refs=json.loads((HERE/'references.json').read_text());pure=json.loads((HERE/'pure-results.json').read_text());assert pure['checks']>=219
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
    family(refs['sourceIndex']);family(refs['monitorIndex'])
    inputs=read(refs['sourceInputs'])
    for r in inputs['files']:capture(r)
    host=read(refs['hostContext'])
    for k in ['sdkSettings','hostLinkerDriver','appleLinker','wasmLinker','xcodeVersionPlist','python']:capture(host[k])
    cut=read(refs['sourceCut']);tools=read(refs['toolReferences']);plan=read(refs['originalBuildPlan'])
    aliases=[]
    for r in tools['jsToolchain']['symlinks']:
        p=Path(tools['jsToolchain']['root'])/r['path'];assert p.is_symlink()and os.readlink(p)==r['target']and str(p.resolve())==r['resolved']['path'];capture(r['resolved']);aliases.append(dict(path=str(p),target=r['target'],resolved=r['resolved']))
    for r in cut['baseline']['files']:assert stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode)==r['mode']
    for r in tools['jsToolchain']['files']:assert stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode)==r['mode']
    # Exact saved draft -> current text derivation, explicit per-edit offsets.
    import difflib
    before=(HERE/'history/root-draft.py').read_text();after=(HERE/'controller.py').read_text();edits=[]
    for tag,i,j,a,b in difflib.SequenceMatcher(None,before,after,autojunk=False).get_opcodes():
        if tag!='equal':edits.append(dict(beforeStart=i,beforeEnd=j,afterStart=a,afterEnd=b,old=before[i:j],new=after[a:b]))
    forward=before
    for e in reversed(edits):assert forward[e['beforeStart']:e['beforeEnd']]==e['old'];forward=forward[:e['beforeStart']]+e['new']+forward[e['beforeEnd']:]
    reverse=after
    for e in reversed(edits):assert reverse[e['afterStart']:e['afterEnd']]==e['new'];reverse=reverse[:e['afterStart']]+e['old']+reverse[e['afterEnd']:]
    assert forward==after and reverse==before
    write('derivations.json',dict(schemaVersion=1,donor='history/root-draft.py',beforeSha256=hashlib.sha256(before.encode()).hexdigest(),afterSha256=hashlib.sha256(after.encode()).hexdigest(),edits=edits,forwardAndReverseExact=True,monitorSourceCopiedOrChanged=False,originalProposalMutated=False,commandDerivation='Four original plans +four named unit filters; two Jco entry paths explicitly rebased to declared private node_modules',toolRootMetadataMap={'package.json':'.toolchain-metadata/package.json','package-lock.json':'.toolchain-metadata/package-lock.json'}))
    for p in HERE.rglob('*.py'):ast.parse(p.read_text())
    for path,identity in identities.items():
        p=Path(path);s=p.stat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==identity
    for f in families:
        base=Path(f['index']['path']).parent;assert{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==set(f['memberNames'])and not any(p.is_symlink()for p in base.rglob('*'))
    write('source-inputs.json',dict(schemaVersion=1,files=list(captured.values()),families=families,links=aliases,originalModesVerified=True,fullContentHashThenFinalIdentityStability=True,readOnlyData=True,operationalHelpersOrToolsInvoked=False))
    result=dict(schemaVersion=1,state='CLOCK_IO_BUILD_CONTROLLER_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,sourceIndex=refs['sourceIndex'],pureDataChecks=pure['checks'],isolatedRawStepCases=9,isolatedPreworkFailureCases=2,isolatedMainCallerCases=2,cachedArchiveHeadersParsed=118,missingArchivesFetched=0,fullSourceInputsHashed=len(captured),logicalInputBytes=sum(r['bytes']for r in captured.values()),originalJsAliasesVerified=len(aliases),exactDraftReversalEdits=len(edits),pythonAstFiles=len(list(HERE.rglob('*.py'))),sourceCopies=0,vendorExtractions=0,networkOrMonitorOrCompilerOrNodeOrJcoActionsInvoked=False,actualStage=None,actualBuild=None,actualUnitResults=None,prunerFunctionInvokedByRefusalUnitTest=None,validAdapterPruningRun=False,adapterArtifactPublished=False,adapterCliPruneCommandInvoked=False,sourcePeer=None,rootAuthority=None,operationalAdmission=False,runtimeAcceptanceClaim=False)
    write('results.json',result)
    write('source-receipt.json',dict(schemaVersion=1,state='SOURCE_ONLY_CLOCK_IO_BUILD_CONTROLLER_RECEIPT_V1',sourceRoot=str(HERE),sourceIndex=refs['sourceIndex'],fullInputs=len(captured),pureChecks=pure['checks'],draftReversals=len(edits),actualActionsInvoked=False,allFutureEffectiveActionsNull=True))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file()and p!=HERE/'index.json':
            r,_=fingerprint(p);r['path']=p.relative_to(HERE).as_posix();rows.append(r)
    write('index.json',dict(schemaVersion=1,files=rows))
    for r in rows:
        actual,_=fingerprint(HERE/r['path']);assert actual['sha256']==r['sha256']and actual['bytes']==r['bytes']
    ix,_=fingerprint(HERE/'index.json');print(json.dumps(dict(index=ix,members=len(rows),inputs=len(captured),pureChecks=pure['checks'])))
if __name__=='__main__':main()
