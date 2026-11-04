"""New source/Node-evidence seal only. No preflight, guest, native or host action."""
from pathlib import Path
import hashlib
import json
import os
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
RUNTIME=BASE/'production-runtime-activated-v3'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    assert not(HERE/'input-freeze.json').exists();rows={}
    def add(path,digest=None,size=None):
        path=Path(path);assert not path.is_symlink();path=path.resolve(strict=True);assert path.is_file();data=path.read_bytes()
        assert digest is None or sha(data)==digest,path
        assert size is None or len(data)==size,path
        row={'path':os.path.relpath(path,HERE),'sha256':sha(data),'bytes':len(data)}
        if row['path']in rows:assert rows[row['path']]==row
        rows[row['path']]=row
    def indexed(root,digest):
        raw=(root/'index.json').read_bytes();assert sha(raw)==digest;add(root/'index.json',digest)
        for row in json.loads(raw)['files']:add(root/row['path'],row['sha256'],row['bytes'])
    indexed(RUNTIME,'7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66')
    runtime=json.loads((RUNTIME/'input-freeze.json').read_bytes())
    for row in runtime['inputs']:add(RUNTIME/row['path'],row['sha256'],row['bytes'])
    indexed(BASE/'stream-trace-regression-candidate-v1','636dfc0561891ff23f028b19289693aa77452fc25e8c5b415f1bf4a191afe7ac')
    indexed(BASE/'independent-stream-trace-component-review-v1','7db35421ab2d46830e0d60b6eb007a0bda801207dc692e8bfd3bc8a83ee1ff84')
    add('/tmp/starling-node-compat/stream-trace-regression-node-v2-eleven/results.json')
    for path in sorted(HERE.rglob('*')):
        if not path.is_file()or'evidence'in path.relative_to(HERE).parts or'__pycache__'in path.relative_to(HERE).parts:continue
        if str(path.relative_to(HERE))in{'index.json','source-receipt.json','input-freeze.json','preflight.mjs'}:continue
        add(path)
    document={'schemaVersion':1,'state':'SEALED_ELEVEN_PUBLIC_STREAM_TRACE_SOURCE_ONLY','caseCount':11,'originalEightCasesUnchanged':True,
      'runtimeIndexSha256':'7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66','runtimeInputFiles':len(runtime['inputs']),
      'delegatedActualVariant':'normal-off','engineSha256':'b8279ee1fedc4e26b7319b6777f6a413242cee0c36169a14195f5c24c44511e4',
      'newGuestOrNativeOrTargetHostInvoked':False,'inputs':sorted(rows.values(),key=lambda row:row['path'])}
    raw=(json.dumps(document,indent=2)+'\n').encode()
    with(HERE/'input-freeze.json').open('xb')as stream:stream.write(raw)
    template=(HERE/'preflight.template.mjs').read_text();assert template.count('@INPUTS_SHA@')==1
    with(HERE/'preflight.mjs').open('x')as stream:stream.write(template.replace('@INPUTS_SHA@',sha(raw)))
    print(json.dumps({'inputs':len(rows),'sha256':sha(raw)}))
if __name__=='__main__':main()
