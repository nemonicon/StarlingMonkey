"""One finite host-reporting amendment; never runs guest/producer/packager."""
from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'measurement-correctness-candidate-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    raw=(PARENT/'index.json').read_bytes();assert sha(raw)=='138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da'
    for row in json.loads(raw)['files']:assert sha((PARENT/row['path']).read_bytes())==row['sha256']
    before=(PARENT/'component-driver.mjs').read_text();after=before;edits=[]
    def replace(old,new,count=1):
        nonlocal after
        assert after.count(old)==count,(old,after.count(old));after=after.replace(old,new);edits.append({'old':old,'new':new,'count':count})
    replace("import {trackedWriter,publishCompletion} from './completion.mjs';","import {trackedWriter,publishCompletion} from './completion.mjs';\nimport {requireExactJSON,RecordedMismatch} from './bounded-comparison.mjs';")
    replace(" function validateCase(value,index,call){const expected=expectedCase(index);assert.equal(value.schemaVersion,1);assert.equal(value.calls,call);assert.equal(value.caseIndex,index);assert.equal(value.setup,expected.setup);assert.deepEqual(value.result,expected.oracle);return value;}",
        " async function validateCase(value,index,call,context=null){const row=expectedCase(index),expected={schemaVersion:1,calls:call,caseIndex:index,setup:row.setup,result:row.oracle};await requireExactJSON({label:'workload-'+index,actual:value,expected,context,writeCounterexample});return value;}")
    replace(" function validateBoundaries(value,call){assert.equal(value.schemaVersion,1);assert.equal(value.calls,call);assert.deepEqual(value.observed,encoding.expected);return value;}",
        " async function validateBoundaries(value,call,context=null){await requireExactJSON({label:'boundaries',actual:value,expected:{schemaVersion:1,calls:call,observed:encoding.expected},context,writeCounterexample});return value;}")
    replace(" async function retainCounterexample(label,actual,expected,error){", " async function writeCounterexample(record){await write(join(output,'correctness-counterexample.json'),JSON.stringify(record,null,2)+'\\n',{flag:'wx'});}\n async function retainCounterexample(label,actual,expected,error){")
    replace('cases.push(validateCase(value,index,startCall+index));','cases.push(await validateCase(value,index,startCall+index));')
    replace('validateBoundaries(boundaries,startCall+20);','await validateBoundaries(boundaries,startCall+20);')
    replace('catch(error){await retainCounterexample(', 'catch(error){if(error instanceof RecordedMismatch)throw error;await retainCounterexample(',3)
    replace(' assert.deepEqual(freshJco,retained[0]);'," await requireExactJSON({label:'fresh-Jco-full-rotation',actual:freshJco,expected:retained[0],writeCounterexample});")
    replace('if(index<20)validateCase(value,index,1);else validateBoundaries(value,1);',"if(index<20)await validateCase(value,index,1,{stdout:actual.stdout,stderr:actual.stderr});else await validateBoundaries(value,1,{stdout:actual.stdout,stderr:actual.stderr});")
    restored=after
    for edit in reversed(edits):assert restored.count(edit['new'])==edit['count'];restored=restored.replace(edit['new'],edit['old'])
    assert restored==before
    target=HERE/'proposed/component-driver.mjs';target.parent.mkdir(exist_ok=False)
    with target.open('x')as stream:stream.write(after)
    for name,value in [('transformation-proof.json',{'schemaVersion':1,'parentIndexSha256':sha(raw),'beforeSha256':sha(before.encode()),'afterSha256':sha(after.encode()),'edits':edits,'reverseExact':True,'guestWorkloadBoundaryOracleBytesChanged':False})]:
        with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
    with(HERE/'reporting.UNAPPLIED.patch').open('x')as stream:stream.write(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/component-driver.mjs',tofile='b/component-driver.mjs')))
if __name__=='__main__':main()
