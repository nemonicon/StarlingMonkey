"""Create the immutable C355-M1 source successor only. No artifact action calls."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
OLD=HERE.with_name('native-integration-candidate-v1')
HOLD=HERE.parent/'independent-native-integration-source-review-v1'
OLD_SHA='ab88215a4d1348f4928ae83cc95a234c570b6a3d1809f622e3202eb370f88e25'
HOLD_SHA='6e24de20da9c6940d8d213b1f21a2cc4bd149195010d391befb459fba5f6c5bc'
def sha(value):return hashlib.sha256(value).hexdigest()
def put(name,value):
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x')as out:out.write(value if isinstance(value,str)else json.dumps(value,indent=2)+'\n')
def main():
    assert not(HERE/'artifact-tools').exists()
    for root,digest in[(OLD,OLD_SHA),(HOLD,HOLD_SHA)]:
        assert sha((root/'index.json').read_bytes())==digest
        for row in json.loads((root/'index.json').read_bytes())['files']:
            value=(root/row['path']).read_bytes();assert sha(value)==row['sha256']and len(value)==row['bytes']
    exclude={'README.md','source-receipt.json','input-freeze.json','prepare-source.py','seal-source.py','evidence/source-tests.json','evidence/syntax-results.json'}
    for row in json.loads((OLD/'index.json').read_bytes())['files']:
        if row['path']in exclude:continue
        put(row['path'],(OLD/row['path']).read_text())
    for name in['README.md','prepare-source.py','seal-source.py']:
        put('ancestry/v1-'+name+'.txt',(OLD/name).read_text())
    oldprefix=str(OLD.relative_to(REPO));newprefix=str(HERE.relative_to(REPO))
    pins=json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes());rewired=0
    for row in pins['toolDependencies']:
        if row['path'].startswith(oldprefix+'/'):row['path']=newprefix+row['path'][len(oldprefix):];rewired+=1
    assert rewired==6
    pins['toolDependencies'].sort(key=lambda row:row['path'])
    toolpath=HERE/'artifact-tools/tool-pins.json';toolpath.write_text(json.dumps(pins,indent=2)+'\n')
    oldtool=sha((OLD/'artifact-tools/tool-pins.json').read_bytes());newtool=sha(toolpath.read_bytes())
    origins=json.loads((HERE/'tool-origins.json').read_bytes());rewired=0
    for row in origins['files']:
        if row['path'].startswith(oldprefix+'/'):
            row['path']=newprefix+row['path'][len(oldprefix):]
            assert row['original'].startswith(str(OLD)+'/');row['original']=str(HERE)+row['original'][len(str(OLD)):];rewired+=1
    assert rewired==6
    origins['files'].sort(key=lambda row:row['path']);(HERE/'tool-origins.json').write_text(json.dumps(origins,indent=2)+'\n')
    transformations=json.loads((HERE/'tool-transformations.json').read_bytes())
    successor=[]
    def edit(name,old,new,count):
        path=HERE/name;value=path.read_text();assert value.count(old)==count,(name,old)
        at=[m.start()for m in re.finditer(re.escape(old),value)]
        updated=value.replace(old,new);path.write_text(updated)
        row={'old':old,'new':new,'count':count,'afterOffsets':[p+i*(len(new)-len(old))for i,p in enumerate(at)]}
        successor.append({'path':name,**row})
        record=next((r for r in transformations['records']if r['path']==name),None)
        if record:record['edits'].append(row);record['afterSha256']=sha(updated.encode())
    edit('artifact-tools/artifact_common.py',"def verify_frozen_variant(label, output=OUTPUT, return_receipt_digest=False):\n    assert label in LABELS\n","def verify_frozen_variant(label, output=OUTPUT, return_receipt_digest=False):\n    assert label in LABELS\n    tool_dependencies(REPO)  # Authenticate every configured helper before any dynamic import.\n",1)
    edit('artifact-tools/artifact_common.py',oldtool,newtool,1)
    edit('artifact-tools/metadata-admission.mjs',oldtool,newtool,1)
    edit('stage.py',"ORIGINAL/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v1').resolve()","ORIGINAL/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2').resolve()",1)
    last="(ORIGINAL/'tests/node-compat/foundation-stream-consumers/sdk-registration-syntax-v1','5d0f51bd3325fc3ec36743e10b5da55980a9f956469b7f76c902f5ab8c037117','INDEXED_ONLY',None,None)]"
    extra=last[:-1]+",\n (ORIGINAL/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v1','"+OLD_SHA+"','INDEXED_ONLY',None,None),\n (ORIGINAL/'tests/node-compat/foundation-stream-consumers/independent-native-integration-source-review-v1','"+HOLD_SHA+"','INDEXED_ONLY',None,None)]"
    edit('stage.py',last,extra,1)
    edit('test-source.py',"==[2261,506,0,0]","==[2261,506,0,0,0,0]",1)
    edit('test-source.py',"==['PREPARATION','PREPARATION','INDEXED_ONLY','INDEXED_ONLY']","==['PREPARATION','PREPARATION','INDEXED_ONLY','INDEXED_ONLY','INDEXED_ONLY','INDEXED_ONLY']",1)
    contract=json.loads((HERE/'bootstrap-contract.json').read_bytes());contract['originalPreparationRoot']=str(HERE)
    (HERE/'bootstrap-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    seal=(OLD/'seal-source.py').read_text()
    needle="HERE.parent/'sdk-registration-syntax-v1']"
    assert seal.count(needle)==1
    seal=seal.replace(needle,"HERE.parent/'sdk-registration-syntax-v1',HERE.parent/'native-integration-candidate-v1',HERE.parent/'independent-native-integration-source-review-v1']")
    needle="'state':'UNAPPLIED_CONSUMERS355_NATIVE_ARTIFACT_FRAMEWORK_SOURCE_ONLY',"
    assert seal.count(needle)==1
    seal=seal.replace(needle,"'state':'UNAPPLIED_CONSUMERS355_NATIVE_ARTIFACT_FRAMEWORK_SOURCE_ONLY_V2','parentProducerIndexSha256':'"+OLD_SHA+"','parentHoldIndexSha256':'"+HOLD_SHA+"','resolvedFinding':'C355-M1','configuredDependenciesAuthenticatedBeforeCustomImports':True,")
    needle="'nodeSyntaxChecks':3,"
    seal=seal.replace(needle,"'nodeSyntaxChecks':3,'scratchOrderingChecks':json.loads((HERE/'evidence/ordering-tests.json').read_bytes())['passed'],")
    seal=seal.replace('SOURCE_ONLY_CONSUMERS355_NATIVE_ARTIFACT_FRAMEWORK_SEALED','SOURCE_ONLY_CONSUMERS355_NATIVE_ARTIFACT_FRAMEWORK_SEALED_V2')
    put('seal-source.py',seal)
    for record in transformations['records']:
        value=Path(record['origin']).read_text();original=value
        for row in record['edits']:assert value.count(row['old'])==row['count'];value=value.replace(row['old'],row['new'])
        assert value==(HERE/record['path']).read_text()
        for row in reversed(record['edits']):
            for at in reversed(row['afterOffsets']):assert value[at:at+len(row['new'])]==row['new'];value=value[:at]+row['old']+value[at+len(row['new']):]
        assert value==original
    (HERE/'tool-transformations.json').write_text(json.dumps(transformations,indent=2)+'\n')
    for name in sorted({r['path']for r in successor}):
        rows=[r for r in successor if r['path']==name];value=(OLD/name).read_text()
        for row in rows:assert value.count(row['old'])==row['count'];value=value.replace(row['old'],row['new'])
        assert value==(HERE/name).read_text()
        for row in reversed(rows):
            for at in reversed(row['afterOffsets']):assert value[at:at+len(row['new'])]==row['new'];value=value[:at]+row['old']+value[at+len(row['new']):]
        assert value==(OLD/name).read_text()
    put('successor-derivations.json',{'schemaVersion':1,'state':'UNAPPLIED_C355_M1_UNIVERSAL_AUTHENTICATION_ORDER_SUCCESSOR','oldIndexSha256':OLD_SHA,'oldHoldIndexSha256':HOLD_SHA,'oldToolPinsSha256':oldtool,'newToolPinsSha256':newtool,'ownToolRowsRewired':6,'toolRows':767,'edits':successor,'nativeRecipePolicyPayloadChanged':False,'stageWorkArtifactDestinationsChanged':False,'stageBuildVerifierBootstrapOrGuestExecuted':False})
    print(json.dumps({'sourceOnly':True,'toolRows':767,'ownRowsRewired':6,'toolPinsSha256':newtool,'semanticFix':'one universal configured-tool authentication barrier'}))
if __name__=='__main__':main()
