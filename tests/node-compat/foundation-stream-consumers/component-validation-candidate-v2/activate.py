"""Future exclusive SOURCE publisher. main is not run during proposal preparation."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
ORIGINAL=Path('/Users/dan/dev/StarlingMonkey')
NATIVE_ORIGINAL=ORIGINAL/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2'
NATIVE=Path('/private/tmp/starling-node-compat/consumers-source-v2/tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2')
NATIVE_SHA='9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'
DEST=HERE.with_name('component-validation-activated-v2')
LABELS=('normal-off','normal-runtime','gc-off','disabled-off')
PAYLOAD=['component.mjs','consumer.cjs','differential.mjs','profiles.mjs','profile-contract.mjs','extras.mjs','node-oracle.json','extra-node-oracle.json','profile-oracle-ancestry.json','checks.mjs','denial-checks.mjs','transport-return.mjs','disabled-fixtures.mjs','disabled-checks.mjs','initializers.mjs','run-validation.mjs','durable-host.mjs','consumed.mjs','component-tools.mjs','runtime-preflight.template.mjs']
def sha(value):return hashlib.sha256(value).hexdigest()
def read(path,digest=None,size=None):
    path=Path(path);assert path.is_file()and not path.is_symlink(),path
    value=path.read_bytes()
    if digest is not None:assert sha(value)==digest,path
    if size is not None:assert len(value)==size,path
    return value
def indexed(root,digest):
    value=read(root/'index.json',digest);index=json.loads(value)
    for row in index['files']:read(root/row['path'],row['sha256'],row['bytes'])
    return index
def main():
    assert len(sys.argv)==6,'OWN_INDEX_SHA REVIEWED_PINS PINS_SHA ROOT_REVIEW REVIEW_SHA'
    own_sha,pins_path,pins_sha,review_path,review_sha=sys.argv[1:]
    assert all(re.fullmatch('[a-f0-9]{64}',value)for value in[own_sha,pins_sha,review_sha])
    assert HERE.resolve()==(ORIGINAL/'tests/node-compat/foundation-stream-consumers/component-validation-candidate-v2').resolve(),'Only original preparation context may publish'
    assert not DEST.exists()and not DEST.is_symlink(),'Exclusive source output required'
    own=indexed(HERE,own_sha);original=indexed(NATIVE_ORIGINAL,NATIVE_SHA);staged=indexed(NATIVE,NATIVE_SHA);assert original==staged
    pins_raw=read(pins_path,pins_sha);review_raw=read(review_path,review_sha);pins=json.loads(pins_raw);review=json.loads(review_raw)
    assert pins['state']=='ROOT_REVIEWED_STREAM_CONSUMERS355_VALIDATION_BOOTSTRAP_V1'and set(pins['variants'])==set(LABELS)
    assert review['state']=='ROOT_REVIEWED_STREAM_CONSUMERS355_BUILD_INPUTS_FOR_CODEC_VALIDATION_V1'and review['reviewedPinsSha256']==pins_sha and review['proposalIndexSha256']==NATIVE_SHA
    assert review['sourceFiles']==355 and review['operationalAdmission']is False and review['runtimeAcceptanceClaim']is False
    assert pins['variants']['normal-off']is not None and pins['variants']['normal-runtime']is None,'Normal required; RuntimeOnly is not this validation lane'
    inputs={}
    def add(path,digest=None,size=None):
        path=Path(path).absolute();value=read(path,digest,size);row={'path':str(path),'sha256':sha(value),'bytes':len(value)}
        if row['path']in inputs:assert inputs[row['path']]==row
        inputs[row['path']]=row
    # Source/preparation remains at its actual original roots. A copied
    # preparation manifest is only data, never resolved from a staged ancestor.
    for root,index in[(HERE,own),(NATIVE_ORIGINAL,original),(NATIVE,staged)]:
        add(root/'index.json')
        for row in index['files']:add(root/row['path'],row['sha256'],row['bytes'])
    for row in json.loads(read(HERE/'source-inputs.json'))['files']:add(row['path'],row['sha256'],row['bytes'])
    add(pins_path,pins_sha);add(review_path,review_sha)
    actual={};frozen_rows=[]
    for label in['normal-off','gc-off','disabled-off']:
        if pins['variants'][label]is None:actual[label]=None;continue
        # This is the genuine reviewed355 bootstrap, not a350 projection or
        # copied older selector. It runs only on a future explicit Root action.
        command=['python3',str(NATIVE/'artifact-tools/bootstrap-classifier.py'),pins_path,pins_sha,review_path,review_sha,label]
        process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,timeout=600,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        native=json.loads(process.stdout);assert native['state']=='ROOT_REVIEWED_STREAM_CONSUMERS355_BUILD_VALIDATION_BOOTSTRAP_PASSED'
        assert native['variant']==label and native['validationBootstrapOnly']is True and native['operationalAdmission']is False
        assert native['configuredSourceRoot']=='/private/tmp/starling-node-compat/consumers-source-v2'
        assert native['sourceRoot']=='/tmp/starling-node-compat/production-consumers-v1/native-freeze/source'
        actual[label]={key:native['pin'][key]for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']}
        for row in native['pin']['frozenFiles']:add(row['path'],row['sha256'],row['bytes']);frozen_rows.append(row)
    actual['normal-runtime']=None
    tool_context=json.loads(read(HERE/'tool-context.json'));assert len(tool_context['toolTrees'])==2 and len(tool_context['toolLinks'])==22
    for row in tool_context['inputs']:add(row['path'],row['sha256'],row['bytes'])
    # Authentication/rechecks also include the actual staged current767 files
    # that the genuine bootstrap executes. No original live five-path reads.
    toolpins=json.loads(read(NATIVE/'artifact-tools/tool-pins.json'))
    for row in toolpins['toolDependencies']:add(NATIVE.parents[3]/row['path'],row['sha256'],row['bytes'])
    assert len(toolpins['toolDependencies'])==767
    closure=json.loads(read(HERE/'component-tool-closure.json'));old_snapshot=str(HERE/'packaging-tools');new_snapshot=str(DEST/'packaging-tools')
    assert closure['componentToolRoot']==old_snapshot
    closure['componentToolRoot']=new_snapshot
    for row in closure['files']:
        assert row['path'].startswith(old_snapshot+'/');row['path']=new_snapshot+row['path'][len(old_snapshot):];row['realPath']=row['path']
    closure_raw=(json.dumps(closure,indent=2)+'\n').encode()
    live=json.loads(read(HERE/'live-inputs.json'));add(live['adapter']['path'],live['adapter']['sha256'],live['adapter']['bytes'])
    for row in live['wit']:add(row['path'],row['sha256'],row['bytes'])
    config={'schemaVersion':1,'state':'ROOT_REVIEWED_CONSUMERS355_COMPONENT_VALIDATION_SOURCE_V1','sourceProposalIndexSha256':own_sha,'bootstrapRoot':str(NATIVE),'bootstrapIndexSha256':NATIVE_SHA,'pinsSha256':pins_sha,'rootReviewSha256':review_sha,'actual':actual,'nativeConfiguredSourceRoot':'/private/tmp/starling-node-compat/consumers-source-v2','componentToolRoot':new_snapshot,'componentToolClosureSha256':sha(closure_raw),'liveAdapter':live['adapter'],'liveWit':live['wit'],'operationalAdmission':False,'engineMetadataRewritten':False}
    config_raw=(json.dumps(config,indent=2)+'\n').encode();config_sha=sha(config_raw)
    published={name:read(HERE/name)for name in PAYLOAD}
    for row in json.loads(read(HERE/'packaging-origins.json'))['files']:published[row['path']]=read(HERE/row['path'],row['sha256'],row['bytes'])
    published.update({'activation.json':config_raw,'component-tool-closure.json':closure_raw,'reviewed-pins.json':pins_raw,'root-review.json':review_raw})
    for name,value in published.items():
        path=str(DEST/name);inputs[path]={'path':path,'sha256':sha(value),'bytes':len(value),'boundary':str(DEST)}
    seal={'schemaVersion':1,'state':'CONSUMERS355_ACTIVATED_SOURCE_TOOL_AND_NATIVE_CONSUMED_SEAL','inputs':[inputs[p]for p in sorted(inputs)],'toolTrees':tool_context['toolTrees'],'toolLinks':tool_context['toolLinks'],'invocation':tool_context['invocation']}
    seal_raw=(json.dumps(seal,indent=2)+'\n').encode();seal_sha=sha(seal_raw)
    compiled=published['runtime-preflight.template.mjs'].decode().replace('@CONFIG_SHA@',config_sha).replace('@INPUTS_SHA@',seal_sha)
    published['runtime-preflight.mjs']=compiled.encode();published['input-freeze.json']=seal_raw
    # All original inputs are checked before writing a sibling staging family.
    for row in inputs.values():
        if not row['path'].startswith(str(DEST)+'/'):read(row['path'],row['sha256'],row['bytes'])
    temporary=DEST.with_name(DEST.name+'.publishing');assert not temporary.exists();temporary.mkdir()
    for name,value in published.items():
        path=temporary/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb')as out:out.write(value)
    receipt={'schemaVersion':1,'state':'ROOT_REVIEWED_CONSUMERS355_VALIDATION_SOURCE_FAMILY_CREATED_NOT_EXECUTED','sourceProposalIndexSha256':own_sha,'nativeProposalIndexSha256':NATIVE_SHA,'pinsSha256':pins_sha,'rootReviewSha256':review_sha,'inputFreezeSha256':seal_sha,'componentToolClosureSha256':sha(closure_raw),'nativeConfiguredSourceRoot':config['nativeConfiguredSourceRoot'],'componentToolRoot':new_snapshot,'frozenNativeRoot':'/tmp/starling-node-compat/production-consumers-v1/native-freeze','originalPreparationRoot':str(HERE),'packagingSnapshotRebasedWithoutNativeMetadataChange':True,'actual':actual,'componentOrGuestExecuted':False,'operationalAdmission':False}
    (temporary/'source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    files=[]
    for path in sorted(temporary.rglob('*')):
        if path.is_file():value=path.read_bytes();files.append({'path':str(path.relative_to(temporary)),'sha256':sha(value),'bytes':len(value)})
    (temporary/'index.json').write_text(json.dumps({'schemaVersion':1,'state':'ROOT_REVIEWED_CONSUMERS355_VALIDATION_SOURCE_FAMILY_NOT_EXECUTED','files':files,'runtimeAcceptanceClaim':False},indent=2)+'\n')
    for row in inputs.values():
        if not row['path'].startswith(str(DEST)+'/'):read(row['path'],row['sha256'],row['bytes'])
    assert not DEST.exists();temporary.rename(DEST)
    for row in files:read(DEST/row['path'],row['sha256'],row['bytes'])
    print(json.dumps({'output':str(DEST),'indexSha256':sha(read(DEST/'index.json')),'files':len(files),'consumed':len(inputs),'toolTrees':2,'toolLinks':22,'sourceOnly':True,'guestExecuted':False}))
if __name__=='__main__':main()
