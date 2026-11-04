"""Three fixture input fixes; no publisher/bootstrap/guest action."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'component-validation-tooling-closure-amendment-v1'
GUEST=HERE.parent/'component-validation-activated-v7/component.mjs'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with(HERE/name).open('xb')as stream:stream.write(raw)
def derive(source,target,changes):
 before=source.read_text();current=before;edits=[]
 for old,new in changes:assert current.count(old)==1,(source,old);current=current.replace(old,new);edits.append({'old':old,'new':new,'count':1})
 reverse=current
 for row in reversed(edits):assert reverse.count(row['new'])==1;reverse=reverse.replace(row['new'],row['old'])
 assert reverse==before
 put(target,current.encode());put(target+'.proof.json',{'schemaVersion':1,'beforePath':str(source),'beforeSha256':sha(before.encode()),'afterSha256':sha(current.encode()),'edits':edits,'reverseExact':True})
def main():
 derive(GUEST,'component.mjs',[("Buffer.from([1])","Buffer.from(new Uint8Array([1]))"),("Buffer.from([0,1,2,3,254,255])","Buffer.from(new Uint8Array([0,1,2,3,254,255]))"),("Buffer.from([i])","Buffer.from(new Uint8Array([i]))")])
 derive(PARENT/'activate.py','activate.py',[
  ('component-validation-activated-v7','component-validation-activated-v8'),
  ("payload['component.mjs']=regular(COVERAGE/'proposed/component.mjs')", "payload['component.mjs']=regular(HERE/'component.mjs')"),
  ("'mandatoryComponentToolClosureAmendmentIndexSha256':own_sha,", "'mandatoryComponentToolClosureAmendmentIndexSha256':'daa7d28a7105f878a9465c4eb0fea2edaa3ef6329a15baafcabd7ccc28a0fd0c','mandatoryBufferFixtureInputAmendmentIndexSha256':own_sha,"),
 ])
 for name in ['inventory.py','runtime-preflight.template.mjs','component-tools.mjs','component-tool-closure.json']:put(name,(PARENT/name).read_bytes())
 print(json.dumps({'guestInputEdits':3,'publisherEdits':3,'nativeOrDriverChanged':False,'actionsExecuted':False}))
if __name__=='__main__':main()
