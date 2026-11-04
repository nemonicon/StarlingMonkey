"""Finite source/tool closure only; no producer, componentizer or guest call."""
from pathlib import Path
import hashlib
import json
import os
HERE=Path(__file__).resolve().parent
RUNTIME=HERE.parent/'production-runtime-activated-v3'
def sha(value):return hashlib.sha256(value).hexdigest()
def main():
    assert not(HERE/'input-freeze.json').exists();rows={}
    def add(path,expected=None,size=None):
        path=Path(path);assert not path.is_symlink();path=path.resolve(strict=True);assert path.is_file();data=path.read_bytes()
        assert expected is None or sha(data)==expected,path
        assert size is None or len(data)==size,path
        row={'path':os.path.relpath(path,HERE),'sha256':sha(data),'bytes':len(data)}
        if row['path']in rows:assert rows[row['path']]==row
        rows[row['path']]=row
    raw=(RUNTIME/'index.json').read_bytes();assert sha(raw)=='7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66';add(RUNTIME/'index.json',sha(raw));index=json.loads(raw)
    for row in index['files']:add(RUNTIME/row['path'],row['sha256'],row['bytes'])
    runtime=json.loads((RUNTIME/'input-freeze.json').read_bytes())
    for row in runtime['inputs']:add(RUNTIME/row['path'],row['sha256'],row['bytes'])
    add('/tmp/starling-node-compat/stream-trace-regression-node-v1/results.json')
    for path in sorted(HERE.iterdir()):
        if path.is_file()and path.name not in {'index.json','source-receipt.json','input-freeze.json','preflight.mjs'}:add(path)
    document={'schemaVersion':1,'state':'SEALED_PUBLIC_STREAM_TRACE_REGRESSION_SOURCE_ONLY',
      'runtimeIndexSha256':sha(raw),'runtimeInputFiles':len(runtime['inputs']),'runtimeToolTrees':len(runtime['toolTrees']),'runtimeToolLinks':len(runtime['toolLinks']),
      'delegatedActualVariant':'normal-off','engineSha256':'b8279ee1fedc4e26b7319b6777f6a413242cee0c36169a14195f5c24c44511e4',
      'componentOrGuestExecuted':False,'inputs':sorted(rows.values(),key=lambda row:row['path'])}
    manifest=(json.dumps(document,indent=2)+'\n').encode()
    with(HERE/'input-freeze.json').open('xb')as stream:stream.write(manifest)
    template=(HERE/'preflight.template.mjs').read_text();assert template.count('@INPUTS_SHA@')==1
    with(HERE/'preflight.mjs').open('x')as stream:stream.write(template.replace('@INPUTS_SHA@',sha(manifest)))
    print(json.dumps({'state':document['state'],'inputs':len(rows),'sha256':sha(manifest)}))
if __name__=='__main__':main()
