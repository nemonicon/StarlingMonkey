"""Finite future source publisher. Data collection is read-only; main is UNEXECUTED."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
ORIGINAL=Path('/Users/dan/dev/StarlingMonkey')
DEST=Path('/tmp/starling-node-compat/consumers-source-v2')
BASE=Path('/tmp/starling-node-compat/zlib-source-v4')
BASE_COMMIT='54b3329b3ce818fd1f244e871e9c259b63667cda'
PARENT=ORIGINAL/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
CONSUMERS=ORIGINAL/'tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2'
FAMILIES=[(PARENT,'d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172','PREPARATION','input-freeze.json','inputs'),
 (CONSUMERS,'eedeef581d961030b9aac3bf87c43e0f58cfe5516c5b04d997eb095c6df7ef7a','PREPARATION','source-inputs.json','files'),
 (ORIGINAL/'tests/node-compat/foundation-stream-consumers/independent-production-text-json-v2-source-review-v1','01f432678d2408d7645d35afea5abd73f192206c6dd3d4197f4ad7a83a0ad9d1','INDEXED_ONLY',None,None),
 (ORIGINAL/'tests/node-compat/foundation-stream-consumers/sdk-registration-syntax-v1','5d0f51bd3325fc3ec36743e10b5da55980a9f956469b7f76c902f5ab8c037117','INDEXED_ONLY',None,None)]
FIVE=['builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs']
def sha(value):return hashlib.sha256(value).hexdigest()
def checked(path,digest,size=None):
    path=Path(path);assert path.is_file()and not path.is_symlink(),path
    data=path.read_bytes();assert sha(data)==digest,path
    if size is not None:assert len(data)==size,path
    return data
def safe(relative):
    assert isinstance(relative,str)and not relative.startswith('/')and '\\'not in relative and all(p not in('','.','..')for p in relative.split('/'))
    return relative
def collect(own_index_sha=None):
    """Read explicit original prep contexts and physical source/tool rows only."""
    rows={};families=[];prep_hits=[]
    def add(relative,original,digest,size,role):
        relative=safe(relative);checked(original,digest,size)
        if relative in rows:
            assert rows[relative]['sha256']==digest and rows[relative]['bytes']==size
            rows[relative]['roles'].append(role);return
        rows[relative]={'path':relative,'original':str(original),'sha256':digest,'bytes':size,'roles':[role]}
    for root,digest,role,manifest_name,key in FAMILIES:
        index=json.loads(checked(root/'index.json',digest))
        for row in index['files']:checked(root/safe(row['path']),row['sha256'],row['bytes'])
        count=0
        if role=='PREPARATION':
            manifest=json.loads((root/manifest_name).read_bytes())
            for row in manifest[key]:
                path=Path(row['path']);path=path if path.is_absolute()else root/path
                checked(path,row['sha256'],row['bytes']);count+=1
                if path.resolve()in[(ORIGINAL/p).resolve()for p in FIVE]:prep_hits.append(str(path.resolve()))
        else:assert manifest_name is None and key is None
        families.append({'root':str(root),'indexSha256':digest,'role':role,'indexedFiles':len(index['files']),'preparationManifest':manifest_name,'preparationRowsReadOnlyAtOriginalRoot':count})
    native=json.loads((HERE/'policy.json').read_bytes())['expectedNativeSourceManifest']
    assert len(native)==355
    edits=json.loads((CONSUMERS/'native-derivations.json').read_bytes())
    proposed=set(edits['addedSources']+[r['path']for r in edits['changes']])
    for row in native:
        origin=CONSUMERS/'proposed'/row['path']if row['path']in proposed else BASE/row['path']
        value=checked(origin,row['sha256']);add(row['path'],origin,row['sha256'],len(value),'ACTUAL_NATIVE355')
    tools=json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes())
    origins=json.loads((HERE/'tool-origins.json').read_bytes())['files'];assert len(origins)==len(tools['toolDependencies'])==767
    for row in origins:add(row['path'],Path(row['original']),row['sha256'],row['bytes'],'FINITE_BUILD_TOOL_DEPENDENCY')
    assert {r['path']:r['sha256']for r in origins}=={r['path']:r['sha256']for r in tools['toolDependencies']}
    if own_index_sha is not None:
        own=json.loads(checked(HERE/'index.json',own_index_sha))
        prefix=str(HERE.relative_to(ORIGINAL))
        value=checked(HERE/'index.json',own_index_sha);add(prefix+'/index.json',HERE/'index.json',own_index_sha,len(value),'SELF_SEALED_SOURCE')
        for row in own['files']:add(prefix+'/'+safe(row['path']),HERE/row['path'],row['sha256'],row['bytes'],'SELF_SEALED_SOURCE')
    five=[]
    for relative in FIVE:
        row=rows[relative];assert Path(row['original']).resolve()!=(ORIGINAL/relative).resolve()
        five.append({'stagedPath':relative,'actualSourceOrigin':row['original'],'sha256':row['sha256'],'originalRootFivePathReadByBuild':False})
    return{'schemaVersion':1,'state':'READ_ONLY_CONSUMERS355_STAGE_COLLECTION','baseCommit':BASE_COMMIT,'destination':str(DEST),'nativeRows':355,'toolRows':767,'files':[rows[p]for p in sorted(rows)],'families':families,'originalRootFivePreparationHits':prep_hits,'fivePathRouting':five,'componentHarnessClosureProvided':False,'stageCreated':False}
def main():
    assert len(sys.argv)==2,'EXACT_OWN_INDEX_SHA; source publication only after Root review'
    expected=sys.argv[1];assert len(expected)==64
    assert HERE.resolve()==(ORIGINAL/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v1').resolve(),'Publisher runs only in original preparation context'
    assert not DEST.exists()and not DEST.is_symlink(),'Exclusive fresh source family only'
    assert shutil.disk_usage(DEST.parent).free>=2*1024**3
    before=collect(expected)
    journal=DEST.parent/'consumers-source-v2-publication.json';assert not journal.exists()
    result={'schemaVersion':1,'state':'SOURCE_PUBLICATION_STARTED','destination':str(DEST),'ownIndexSha256':expected,'nativeBuildOrGuestExecuted':False,'sourceMetadataProjected':False}
    try:
        # A real independent local clone supplies genuine54b HEAD and project
        # scaffolding. No alternates/hardlinks or original-repository writes.
        for command in [['git','clone','--no-local','--no-checkout',str(ORIGINAL),str(DEST)],['git','-C',str(DEST),'checkout','--detach',BASE_COMMIT]]:
            process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
            result.setdefault('sourceCommands',[]).append({'argv':command,'status':process.returncode,'stdout':process.stdout.decode(),'stderr':process.stderr.decode()});assert process.returncode==0
        assert subprocess.check_output(['git','-C',str(DEST),'rev-parse','HEAD'],text=True).strip()==BASE_COMMIT
        assert not(DEST/'.git/objects/info/alternates').exists()
        for row in before['files']:
            target=DEST/row['path'];cursor=DEST
            for part in row['path'].split('/'):
                cursor/=part;assert not cursor.is_symlink()
            if target.exists():
                # Only known genuine baseline files may be replaced, never an
                # unrelated preexisting generated file or source family.
                baseline=subprocess.run(['git','-C',str(DEST),'show',BASE_COMMIT+':'+row['path']],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                assert baseline.returncode==0 and target.read_bytes()==baseline.stdout
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(checked(row['original'],row['sha256'],row['bytes']))
            checked(target,row['sha256'],row['bytes'])
        after=collect(expected);assert after==before
        for row in after['files']:checked(DEST/row['path'],row['sha256'],row['bytes'])
        result.update(state='CONSUMERS355_SOURCE_PUBLISHED_NOT_BUILT',files=len(after['files']),nativeRows=355,toolRows=767,genuineHead=BASE_COMMIT,allOriginalAndStagedBytesVerified=True,preparationRowsInterpretedOnlyAtOriginalRoots=True)
    except BaseException as error:
        result.update(state='SOURCE_PUBLICATION_FAILED_OR_PARTIAL',error={'type':type(error).__name__,'message':str(error)});raise
    finally:
        try:
            with journal.open('x')as output:json.dump(result,output,indent=2);output.write('\n')
        finally:print(json.dumps(result),flush=True)
if __name__=='__main__':main()
