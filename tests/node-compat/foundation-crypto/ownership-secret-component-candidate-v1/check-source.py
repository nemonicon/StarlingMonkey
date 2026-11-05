"""Read/hash/JSON/Python AST Source preparation only. No JS/tool/helper import."""
from pathlib import Path
import ast,hashlib,json,os,stat
HERE=Path(__file__).resolve().parent
assert not(HERE/'index.json').exists()
def read(p):return json.loads(Path(p).read_bytes())
def identity(p):
    s=p.lstat();assert stat.S_ISREG(s.st_mode)
    return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),str(p.resolve()))
def row(p):
    p=Path(p);i=identity(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    assert i==identity(p);return dict(path=str(p),sha256=h.hexdigest(),bytes=i[2]),i
def tree(p):
    assert p.is_dir()and not p.is_symlink();names=[]
    for q in p.rglob('*'):
        assert not q.is_symlink()and(q.is_dir()or q.is_file())
        if q.is_file():names.append(q.relative_to(p).as_posix())
    return sorted(names)
refs=read(HERE/'references.json');inputs=read(HERE/'source-inputs.json');deriv=read(HERE/'derivations.json');pure=read(HERE/'pure-results.json')
assert len(inputs['files'])==33290 and len(inputs['families'])==24 and pure['checks']==45
captured={};files={}
for d in inputs['files']:
    assert set(d)=={'path','sha256','bytes'}and type(d['bytes'])is int and d['bytes']>=0
    assert Path(d['path']).is_absolute()and str(Path(d['path']))==d['path']and d['path']not in captured
    actual,i=row(d['path']);assert actual==d;captured[d['path']]=i;files[d['path']]=d
for ix in inputs['families']:
    assert files[ix['path']]==ix;v=read(ix['path']);base=Path(ix['path']).parent;names=['index.json']
    assert v['schemaVersion']==1 and 0<len(v['files'])<=2048
    for m in v['files']:
        n=m['path'];assert n and not n.startswith('/')and '\\'not in n and all(s not in('','.','..')for s in n.split('/'))
        names.append(n);assert files[str(base/n)]==dict(m,path=str(base/n))
    assert len(names)==len(set(names))and tree(base)==sorted(names)
for local,key in [('guest.mjs','guestDonor'),('public-abi.wit','witDonor')]:
    assert (HERE/local).read_bytes()==Path(deriv[key]['path']).read_bytes()
donor=Path(deriv['primitiveDonor']['path']).read_text();d=deriv['primitiveBlock'];block=donor[d['start']:d['end']]
assert row(deriv['primitiveDonor']['path'])[0]==deriv['primitiveDonor']and len(block.encode())==d['bytes']and hashlib.sha256(block.encode()).hexdigest()==d['sha256']
prefix=(HERE/'caller-primitives.mjs').read_text();body=(HERE/'caller-body.mjs').read_text();source=(HERE/'build.mjs').read_text()
assert prefix.endswith(block)and source==prefix+body and source[:-len(body)]==prefix and source[len(prefix):]==body
assert "ORIGINAL='"+str(HERE)+"'"in source
assert source.count('record=await api.retainedSecretBootstrapPreflight(')==1 and source.count('await selected.componentize(bundle.code,options)')==1
assert 'selectedManifestsForEngine('not in source and 'secretArtifactBootstrapPreflight('not in source and 'cryptoOwnerBootstrapPreflight('not in source
assert "await record.recheck();"in source and "if(record)await record.recheck();"in source and 'finalProtectionErrors:finalErrors'in source
assert "builtinManifests:h.selectedManifests,virtualModules:{}"in source and 'builtinMap(h.selectedManifests)'in source
pack=read(refs['packagingMap']['path']);publication=read(pack['publicationIndex']['path'])
assert pack['state']=='EXACT_EXISTING_PACKAGING_PHYSICAL_ROLES_NOT_NATIVE_AUTHORITY'and pack['originalZlibNativeFactsConsumed']is pack['costActionStatesReused']is False
assert len(pack['files'])==4934 and len(pack['links'])==22 and pack['toolFiles']==4890 and pack['packagingFiles']==44
pubfiles={r['path']:r for r in publication['files']}
expected={r['path']:r for r in pack['files']};links={r['destination']:r for r in pack['links']};found=set();foundlinks=set();root=Path(pack['publicationRoot'])
rs=root.stat();assert rs.st_dev==pack['rootIdentity']['device']and rs.st_ino==pack['rootIdentity']['inode']and stat.S_IMODE(rs.st_mode)==0o700
for role in pack['roleRoots']:
    p=root/role;assert p.is_dir()and not p.is_symlink()
    for q in p.rglob('*'):
        n=q.relative_to(root).as_posix();s=q.lstat()
        if q.is_symlink():
            link=links[n];assert os.readlink(q)==link['newLinkText']and str(q.resolve())==str(root/link['mappedTarget']);foundlinks.add(n)
        elif q.is_dir():assert stat.S_IMODE(s.st_mode)==0o700
        else:
            m=expected[n];assert s.st_nlink==1 and stat.S_IMODE(s.st_mode)==m['mode'];assert {k:pubfiles[n][k]for k in ['path','sha256','bytes','mode']}==m;assert files[str(q)]==dict(path=str(q),sha256=m['sha256'],bytes=m['bytes']);found.add(n)
assert found==set(expected)and foundlinks==set(links)
schema=next(r for r in pack['files']if r['path']=='packaging/builtins/node-compat/manifest.schema.json');assert refs['manifestSchema']['sha256']==schema['sha256']
record=read(refs['actualRetainedRecordData']['path']);h=record['historicalBootstrap']
assert h['componentizeSourceRoot']==refs['physicalRoles']['frozenEmbeddingSourceRoot']and h['sourceRoot']==refs['physicalRoles']['frozenNativeSourceRoot']
assert len(set(refs['physicalRoles'].values()))==len(refs['physicalRoles'])
assert h['engine']==refs['engine']and h['metadataDescriptor']==refs['metadata']and h['freezeReceipt']==refs['freezeReceipt']
assert len(h['selectedManifests'])==11 and len(h['metadata'])==75 and h['nativeSourceFiles']==355 and h['externalEmbeddingSources']==3
for p in [Path(refs['outputRoot']),Path(refs['externalRoot'])]:assert not p.exists()and not p.is_symlink()
authority=read(HERE/'future-root-authority.template.json');config=read(HERE/'future-config.template.json');peer=read(HERE/'future-source-review-contract.json')
for k in ['state','phase','sourceIndex','entry','sourceIndependentReview','componentBuildAllowed','componentInitializationAllowed','retainedReadOnlyApiAllowed','retainedConfig','actualComponentReview','actualRuntimeAuthority']:assert authority[k]is None
assert config['sourceIndex']is config['rootAuthority']is peer['componentSourceIndexSha256']is None
astfiles=[]
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes());astfiles.append(p.name)
for path,i in captured.items():assert identity(Path(path))==i
for ix in inputs['families']:
    v=read(ix['path']);assert tree(Path(ix['path']).parent)==sorted(['index.json']+[m['path']for m in v['files']])
out=dict(schemaVersion=1,state='SOURCE_ONLY_SECRET355_COMPONENT_CLOSURE_CHECKS_PASSED_V1',files=len(files),logicalBytes=sum(d['bytes']for d in files.values()),completeFamilies=24,allHashesAndFinalIdentitiesPassed=True,allFamilyMembershipsPassed=True,packagingRegularFiles=4934,packagingAliases=22,exactPackagingModesAndMembershipPassed=True,completePublicationIndexAlsoAuthenticated=True,primitiveBlockExactBytes=deriv['primitiveBlock']['bytes'],completeCallerAssemblyAndReversePassed=True,guestAndAbiByteExact=True,selectedManifests=11,metadataFields=75,nativeSourceFiles=355,externalEmbeddingSources=3,distinctPhysicalRolesVerified=True,pureDataSourceChecks=45,pythonAstFiles=astfiles,javascriptGrammarCheckerUsed=False,actualCompleteConstructorApiHelperToolOrGuestExecuted=False,newOutputRootsAbsent=True,sourcePeer=None,rootAuthority=None,actualComponent=None,operationalAdmission=False)
(HERE/'closure-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(files=len(files),families=24,logicalBytes=out['logicalBytes'],pureChecks=45,actions=0,jsGrammarChecked=False)))
