"""Unsealed SOURCE successor for the exact OFF diagnostic/retention corrections."""
from pathlib import Path
import hashlib,json,re,shutil
HERE=Path(__file__).resolve().parent
OLD=HERE.with_name('component-validation-candidate-v1')
OLD_SHA='5659c2885860e1e926e20e8c59a0fac48c2869b401a7e55c190783b2dad9bf79'
def sha(value):return hashlib.sha256(value).hexdigest()
def main():
    assert not(HERE/'component.mjs').exists()
    assert sha((OLD/'index.json').read_bytes())==OLD_SHA
    index=json.loads((OLD/'index.json').read_bytes())
    excluded={'README.md','source-inputs.json','source-receipt.json','seal-source.py','prepare-source.py','evidence/source-results.json','evidence/closure-results.json','evidence/syntax-results.json'}
    for row in index['files']:
        data=(OLD/row['path']).read_bytes();assert sha(data)==row['sha256']and len(data)==row['bytes']
        if row['path']in excluded:continue
        target=HERE/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb')as output:output.write(data)
    ancestry=HERE/'ancestry';ancestry.mkdir(exist_ok=True)
    for name in ['README.md','prepare-source.py','seal-source.py']:(ancestry/('v1-'+name+'.txt')).write_bytes((OLD/name).read_bytes())
    edits=[]
    def edit(name,old,new,count=1):
        path=HERE/name;value=path.read_text();assert value.count(old)==count,(name,old)
        offsets=[m.start()for m in re.finditer(re.escape(old),value)];value=value.replace(old,new);path.write_text(value)
        edits.append({'path':name,'old':old,'new':new,'count':count,'afterOffsets':[at+i*(len(new)-len(old))for i,at in enumerate(offsets)]})
    edit('run-validation.mjs',"import {assertDisabledManifests,assertSmoke} from './disabled-checks.mjs';","import {assertDisabledManifests,assertSmoke} from './disabled-checks.mjs';\nimport {assertDisabledDenial} from './denial-checks.mjs';\nimport {transportReturnEnvelope} from './transport-return.mjs';")
    edit('run-validation.mjs',"assert(failure&&/Node builtin is not admitted by this profile:/.test(failure.message));const record={index,id:row.id,kind:row.kind,error:failure,beforeAnyComponentization:componentizeCalls===0};","const diagnostic=assertDisabledDenial(row,failure);const record={index,id:row.id,kind:row.kind,error:failure,diagnostic,beforeAnyComponentization:componentizeCalls===0};")
    edit('run-validation.mjs',"const raw=await invoke();assert.equal(typeof raw,'string');const rawFile=await save('calls/'+id+'.raw.txt',raw);","const raw=await invoke();const transportFile=await save('calls/'+id+'.transport.json',transportReturnEnvelope(raw));let rawFile=null;if(typeof raw==='string')rawFile=await save('calls/'+id+'.raw.txt',raw);assert.equal(typeof raw,'string');")
    edit('run-validation.mjs',"return{id,value,rawFile};","return{id,value,rawFile,transportFile};")
    edit('activate.py',"DEST=HERE.with_name('component-validation-activated-v1')","DEST=HERE.with_name('component-validation-activated-v2')")
    edit('activate.py',"'checks.mjs','disabled-fixtures.mjs'","'checks.mjs','denial-checks.mjs','transport-return.mjs','disabled-fixtures.mjs'")
    edit('activate.py',"component-validation-candidate-v1').resolve()","component-validation-candidate-v2').resolve()")
    edit('test-closure.py',"'component-validation-activated-v1'in activation","'component-validation-activated-v2'in activation")
    closure=json.loads((HERE/'component-tool-closure.json').read_bytes());old_root=str(OLD/'packaging-tools');new_root=str(HERE/'packaging-tools')
    assert closure['componentToolRoot']==old_root;closure['componentToolRoot']=new_root
    for row in closure['files']:
        assert row['path'].startswith(old_root+'/');row['path']=new_root+row['path'][len(old_root):];row['realPath']=row['path']
    (HERE/'component-tool-closure.json').write_text(json.dumps(closure,indent=2)+'\n')
    for name in sorted({row['path']for row in edits}):
        value=(OLD/name).read_text();original=value
        for row in [row for row in edits if row['path']==name]:assert value.count(row['old'])==row['count'];value=value.replace(row['old'],row['new'])
        assert value==(HERE/name).read_text()
        for row in reversed([row for row in edits if row['path']==name]):
            for at in reversed(row['afterOffsets']):assert value[at:at+len(row['new'])]==row['new'];value=value[:at]+row['old']+value[at+len(row['new']):]
        assert value==original
    (HERE/'successor-derivations.json').write_text(json.dumps({'schemaVersion':1,'state':'UNSEALED_OFF_DIAGNOSTIC_AND_RAW_RETURN_SOURCE_SUCCESSOR','oldIndexSha256':OLD_SHA,'edits':edits,'packagingSnapshotPathRebaseOnly':{'from':old_root,'to':new_root},'guestCorpusOrNativeAuthorityChanged':False,'activationOrGuestExecuted':False},indent=2)+'\n')
    print(json.dumps({'sourceOnly':True,'sourceEdits':len(edits),'guestCasesUnchanged':38,'sealed':False}))
if __name__=='__main__':main()
