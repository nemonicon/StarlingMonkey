"""Source/read/hash/extracted predicate checks; never import/call full verifier."""
from pathlib import Path
import ast,copy,hashlib,json,os,re,shlex,stat
HERE=Path(__file__).resolve().parent
observed={};checks=0;cases=[]


def need(value,reason='check'):
    global checks
    checks+=1
    assert value,reason


def record(path,sha=None,size=None):
    s=str(path);p=Path('/private'+s)if s.startswith('/tmp/')else Path(s)
    need(p.is_absolute()and '..'not in p.parts)
    for q in(p,*p.parents):need(not q.is_symlink(),str(q))
    a=p.stat();need(stat.S_ISREG(a.st_mode));h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns))
    r=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
    if sha is not None:need(r['sha256']==sha,str(p))
    if size is not None:need(r['bytes']==size,str(p))
    if str(p)in observed:need(observed[str(p)]==r)
    observed[str(p)]=r;return r


def verify(r):return record(r['path'],r['sha256'],r['bytes'])
def load(p):record(p);return json.loads(Path(p).read_bytes())
def read(r):verify(r);return json.loads(Path(r['path']).read_bytes())


def family(ix):
    v=read(ix);root=Path(ix['path']).parent;names=set();rows=[ix]
    for r in v['files']:
        n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')));names.add(n);d=dict(r,path=str(root/n));verify(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        need(not p.is_symlink())
        if p.is_file():actual.add(str(p.relative_to(root)))
    need(actual==names|{'index.json'});return rows


def extract(text,name,env):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==name)
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<extracted pure '+name+'>','exec'),env);return env[name]


def case(name,callback,reject=False):
    failed=False
    try:callback()
    except(AssertionError,KeyError,ValueError,TypeError):failed=True
    need(failed==reject,name);cases.append(dict(name=name,passed=True,expected='REJECT'if reject else'PASS'))


def changed(value,path,replacement):
    out=copy.deepcopy(value);target=out
    for key in path[:-1]:target=target[key]
    target[path[-1]]=replacement;return out


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    need(not(HERE/'index.json').exists())
    c=load(HERE/'source-contract.json');refs=load(HERE/'references.json');derivations=load(HERE/'derivations.json')
    for f in refs['families']:family(f['index'])
    artifact=read(c['actualArtifactReview']['result']);contract=read(c['actualArtifactContract'])
    need(artifact['state']==contract['requiredReviewState']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_OFF_NATIVE_ARTIFACT_REVIEW_PASSED_V1'and artifact['verifiedPassed']is True)
    for k,v in contract['requiredFixedValues'].items():need(artifact[k]==v)
    for k,v in contract['requiredExactDescriptors'].items():need(artifact['artifacts'][k]==v)
    need(artifact['artifacts']==contract['artifacts']and artifact['coverage']==contract['requiredCoverage'])
    ledger=read(c['artifactProofInputLedger'])
    for r in ledger['files']:verify(r)
    root=Path(c['frozenRoot']);receipt=read(c['freezeReceipt']);need(len(receipt['copies'])==1902)
    copied={r['path']:r for r in receipt['copies']}
    for r in receipt['copies']:
        verify({k:r[k]for k in['path','sha256','bytes']});need(stat.S_IMODE(Path(r['path']).stat().st_mode)==0o600)
        if r['original']is not None:verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
    need(sum(r['original']is not None for r in receipt['copies'])==1899)
    names=set()
    for p in root.rglob('*'):
        need(not p.is_symlink())
        if p.is_file():names.add(str(p.relative_to(root)))
        if p.is_dir():need(stat.S_IMODE(p.stat().st_mode)==0o700)
    need(names=={str(Path(r['path']).relative_to(root))for r in receipt['copies']}|{'normal-off-freeze-receipt.json'}and len(names)==1903)
    normal=read(refs['normalProtection']);need(normal['originalReferenceEntries']==1387 and len(normal['requiredNormalFreezeMembership'])==1391)
    verify(normal['freezeReceipt'])
    for r in normal['frozenCopyEntries']:verify({k:r[k]for k in['path','sha256','bytes']})
    for r in normal['originals']:verify(r['original']);verify(r['frozen'])
    normal_root=Path(normal['freezeReceipt']['path']).parent
    need({str(p.relative_to(normal_root))for p in normal_root.rglob('*')if p.is_file()}==set(normal['requiredNormalFreezeMembership']))
    for key in['policy','sourceHelperData','recipeData','sourceAdmission','compileCommands','cmakeCache','embeddingCommands','engine','metadata']:verify(c[key])
    for r in refs['frozenRegistrySources'].values():verify(r)
    metadata=read(c['metadata']);policy=read(c['policy']);text=(HERE/'verifier.py').read_text();tree=ast.parse(text)
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    need(not any(isinstance(n,(ast.Import,ast.ImportFrom))and any(a.name in['subprocess','importlib','shutil']for a in n.names)for n in ast.walk(tree)))
    need(not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in['exec','eval','__import__']for n in ast.walk(tree)))
    need(not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in['stat','read_bytes','open','resolve']for n in ast.walk(functions['validate_receipt'])))
    donor=Path(derivations['donor']['path']).read_text();verify(derivations['donor'])
    for d in derivations['exactPureFunctions']:
        node=next(n for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef)and n.name==d['name'])
        need(ast.get_source_segment(donor,node)==d['source']==ast.get_source_segment(text,functions[d['name']]))
    original=ast.get_source_segment(donor,next(n for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef)and n.name=='classify'));forward=original
    for e in derivations['metadataPredicate']['edits']:need(forward.count(e['before'])==e['count']);forward=forward.replace(e['before'],e['after'])
    actual=ast.get_source_segment(text,functions['validate_metadata']);need(forward==actual)
    reverse=actual
    for e in reversed(derivations['metadataPredicate']['edits']):need(reverse.count(e['after'])==e['count']);reverse=reverse.replace(e['after'],e['before'])
    need(reverse==original)
    env=dict(Path=Path,re=re,shlex=shlex,FROZEN=root,CONFIGURED=c['configuredSourceRoot'],WORK=c['workRoot'],HERE=HERE,NATIVE_SHA=c['nativeSourceIndex']['sha256'],FREEZER_SHA=c['freezerSourceIndex']['sha256'],RECEIPT_SHA=c['freezeReceipt']['sha256'],ENGINE_SHA=c['engine']['sha256'],METADATA_SHA=c['metadata']['sha256'])
    def confine_data(path):
        p=Path(path);need(p.is_absolute()and '..'not in p.parts and p!=root and p.is_relative_to(root));return p
    env['confined']=confine_data
    local=extract(text,'local',env)
    case('local frozen member path accepted',lambda:need(local('source/builtins/web/crypto/crypto-key.cpp')=='source/builtins/web/crypto/crypto-key.cpp'))
    for path in['../outside','/absolute','source//double','source/./dot','source\\escape','source\0escape']:
        case('local path refuses '+repr(path),lambda p=path:local(p),True)
    validate_contract=extract(text,'validate_contract',env);validate_receipt=extract(text,'validate_receipt',env);validate_metadata=extract(text,'validate_metadata',env)
    case('actual typed Source contract',lambda:validate_contract(c))
    case('actual1902 row receipt shape without payload/helper calls',lambda:validate_receipt(receipt,c))
    case('actual new355 metadata predicate',lambda:need(validate_metadata(metadata,'normal-off',policy,c['recipeData']['sha256'])==(False,'off')))
    for path,value in[(['nativeSourceIndex','sha256'],'0'*64),(['frozenSourceRoot'],c['configuredSourceRoot']),(['engine','sha256'],'0'*64),(['policy','path'],c['configuredSourceRoot']+'/policy.json'),(['sourceHelperData','path'],str(root/'artifact-tools/artifact_common.py')),(['variant'],'gc-off'),(['engineExecuted'],True)]:
        case('contract rejects '+'.'.join(path),lambda p=path,v=value:validate_contract(changed(c,p,v)),True)
    for path,value in[(['state'],'immutable-crypto-owner-release-engine-frozen'),(['engineSha256'],'0'*64),(['nativeInputsVerified'],350),(['runtimeBackendProof','verified'],True),(['configuredSourceRoot'],c['frozenSourceRoot'])]:
        case('receipt rejects '+'.'.join(path),lambda p=path,v=value:validate_receipt(changed(receipt,p,v),c),True)
    for path,value in[(['cryptoSecretFailureSourcePolicy'],{}),(['sourceManifest'],[]),(['entropyPolicy'],'runtime-only'),(['gcStress'],True),(['syntheticMetadataOnly'],True),(['diagnosticOnly'],True),(['cryptoSecretFailureBuildEvidence','runtimeValidation'],{})]:
        case('metadata rejects '+'.'.join(path),lambda p=path,v=value:validate_metadata(changed(metadata,p,v),'normal-off',policy,c['recipeData']['sha256']),True)
    for name in['manifest','exact_release','compile_command','embedding_command']:extract(text,name,env)
    compile_data=extract(text,'compile_data',env)
    database=read(c['compileCommands']);embedding=Path(c['embeddingCommands']['path']).read_bytes();cache=Path(c['cmakeCache']['path']).read_bytes()
    case('actual frozen68DB and recorded embedding/cache DATA',lambda:need(compile_data(metadata,policy,database,embedding,cache,c)==dict(databaseRows=68,policyCpp=62,otherConfigured=5,generatedNull=1,strictCpp=4,privateCpp=6,embeddingSeparate=1,secretCpp=2)))
    case('compile DATA rejects missing embedding',lambda:compile_data(metadata,policy,database,b'',cache,c),True)
    case('compile DATA rejects old row count',lambda:compile_data(metadata,policy,database[:-1],embedding,cache,c),True)
    # Whole verifier is NOT called. Independent DATA reading checks its exact
    # role names/data access seams while leaving actualVerifierRun NULL.
    for relative in['normal-off-Cargo.toml','normal-off-Cargo.lock','normal-off-libcrypto.a','normal-off-openssl-before.json','normal-off-openssl-receipt.txt','normal-off-openssl-configure.txt','normal-off-openssl-configdata.pm','tooling/repository/runtime/crates/staticlib-template/Cargo.lock']:
        need(str(root/relative)in copied,relative)
    need(metadata['generatedRustProject']['cargoBuildLocked']is True and metadata['generatedRustProject']['manifestAndLockCheckedBeforeAndAfterBuild']is True)
    manifest_names=[r['path']for r in metadata['selectedModuleManifests']];need(len(manifest_names)==len(set(manifest_names))==11)
    for r in metadata['selectedModuleManifests']:record(root/'source'/r['path'],r['sha256'])
    for r in metadata['sourceManifest']:record(root/'source'/r['path'],r['sha256'])
    for r in metadata['componentizeSourceManifest']:record(root/'componentize-source'/r['path'],r['sha256'])
    need(c['exportEntryImplemented']is c['pinModelImplemented']is c['bootstrapApiImplemented']is False)
    for k in['sourceIndependentReview','rootAuthority','actualVerifierRun','actualExport','reviewedPins','bootstrapAuthority','runtimeAuthority']:need(c[k]is None)
    need(not(HERE/'action.py').exists()and not(HERE/'bootstrap.mjs').exists()and not(HERE/'pin_model.py').exists())
    parse_count=0
    for p in HERE.rglob('*'):
        if p.is_file()and p.name not in['source-inputs.json','check-results.json','pure-results.json']:
            record(p)
            if p.suffix=='.py':ast.parse(p.read_text());parse_count+=1
            if p.suffix=='.json':json.loads(p.read_bytes())
    snapshots=list(observed.values())
    for r in snapshots:verify(r)
    ledger_paths={('/private'+r['path'])if r['path'].startswith('/tmp/')else r['path']for r in ledger['files']}
    write('source-inputs.json',dict(schemaVersion=1,files=[r for r in snapshots if r['path']not in ledger_paths],artifactProofLedger=c['artifactProofInputLedger'],artifactProofLedgerRows=len(ledger['files']),uniqueCanonicalInputPaths=len(snapshots),allInputsFinallyRehashed=True))
    write('pure-results.json',dict(schemaVersion=1,scope='Actual extracted pure predicates and independent retained DATA reads only; full verifier and all owner modules never imported/called',cases=cases,fullVerifierInvoked=False,actualExportCandidateCreated=False))
    write('check-results.json',dict(schemaVersion=1,state='SECRET_OWNER355_FROZEN_VERIFIER_SOURCE_CHECKS_PASSED_V1',sourceOnly=True,sourceChecksPassed=True,checks=checks,uniqueInputPaths=len(snapshots),pureCases=len(cases),pythonAstFiles=parse_count,exactPureFunctions=4,metadataPredicateForwardReverseEdits=4,newFrozenCopiesProtected=1902,newFrozenOriginalReferencesProtected=1899,newFrozenMembershipProtected=1903,normalFrozenMembershipProtected=1391,normalOriginalReferencesProtected=1387,ownerModulesImported=False,fullVerifierInvoked=False,helpersInvoked=False,nodeInvoked=False,ninjaInvoked=False,copyOrExportInvoked=False,bootstrapInvoked=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,actualVerifierRun=None,actualExport=None,actualBootstrap=None,exportPinBootstrapImplemented=False))
    print(json.dumps(dict(sourceChecksPassed=True,checks=checks,uniqueInputPaths=len(snapshots),pureCases=len(cases),pythonAstFiles=parse_count,actualVerifierRun=None)))


if __name__=='__main__':main()
