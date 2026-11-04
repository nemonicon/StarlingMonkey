"""Create one fixed source seal/render; no host, guest or old-source write."""
from pathlib import Path
import hashlib
import json
import os
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
def sha(value): return hashlib.sha256(value).hexdigest()
def main():
    assert not(HERE/'input-freeze.json').exists()
    rows={}
    def add(path,expected=None,size=None):
        path=Path(path);assert path.is_file()and not path.is_symlink();data=path.read_bytes()
        assert expected is None or sha(data)==expected,path
        assert size is None or len(data)==size,path
        row={'path':os.path.relpath(path,HERE),'sha256':sha(data),'bytes':len(data)}
        if row['path']in rows:assert rows[row['path']]==row
        rows[row['path']]=row
    for name,digest in [('classic-http-candidate-v1','ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982'),
                        ('independent-http-prehost-verification-v1','6aaed181e304408ce61874cbf45766aab8264f7d2391936f2c7941243d01579d')]:
        root=BASE/name;raw=(root/'index.json').read_bytes();assert sha(raw)==digest;add(root/'index.json',digest)
        for row in json.loads(raw)['files']:add(root/row['path'],row['sha256'],row['bytes'])
    add(BASE/'production-adoption-v1/http-component-phase-root-review-v1.json','eb1caa1168f57f135c1b38c924ef1ce99305aa34688419edd5847e242a5f9c29')
    for path in sorted(HERE.iterdir()):
        if path.is_file()and path.name not in {'verify-retry.mjs','input-freeze.json','index.json','source-receipt.json'}:add(path)
    document={'schemaVersion':1,'state':'SOURCE_ONLY_WASMTIME_FRESH_OUTPUT_RETRY_INPUTS',
      'originalComponentAndPhaseUnchanged':True,'originalSourceClosureDelegatedToUnchangedVerifyHTTPReady':7518,
      'inputs':sorted(rows.values(),key=lambda row:row['path'])}
    raw=(json.dumps(document,indent=2)+'\n').encode()
    with(HERE/'input-freeze.json').open('xb')as stream:stream.write(raw)
    template=(HERE/'verify-retry.template.mjs').read_text();assert template.count('@INPUTS_SHA@')==1
    with(HERE/'verify-retry.mjs').open('x')as stream:stream.write(template.replace('@INPUTS_SHA@',sha(raw)))
    print(json.dumps({'state':document['state'],'inputs':len(rows),'manifestSha256':sha(raw)}))
if __name__=='__main__':main()
