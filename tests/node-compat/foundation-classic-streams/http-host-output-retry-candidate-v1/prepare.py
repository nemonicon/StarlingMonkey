"""Prepare source-only fresh-output retry; no host/body import or execution."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'classic-http-candidate-v1'
def sha(value): return hashlib.sha256(value).hexdigest()
def main():
    assert sha((OLD/'index.json').read_bytes())=='ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982'
    records=[]
    for name,target,edits in [
      ('run-http-wasmtime.mjs','run-http-wasmtime-body.mjs',[
        ("from './http-contract.mjs'","from '../classic-http-candidate-v1/capability/http-contract.mjs'"),
        ("from './preflight.mjs'","from '../classic-http-candidate-v1/capability/preflight.mjs'"),
        ("'http-joint/wasmtime-v1'","'http-joint/wasmtime-v2'"),
        ("import('./hosts/test-wasmtime-http.mjs')","import('../classic-http-candidate-v1/capability/hosts/test-wasmtime-http.mjs')")]),
      ('audit-http.mjs','audit-http-body.mjs',[
        ("from './http-contract.mjs'","from '../classic-http-candidate-v1/capability/http-contract.mjs'"),
        ("from './preflight.mjs'","from '../classic-http-candidate-v1/capability/preflight.mjs'"),
        ("from './validate-hosts.mjs'","from '../classic-http-candidate-v1/capability/validate-hosts.mjs'"),
        ('http-joint/wasmtime-v1/','http-joint/wasmtime-v2/')])]:
        before=(OLD/'capability'/name).read_text();after=before;applied=[]
        for old,new in edits:
            count=after.count(old);assert count==(2 if old=='http-joint/wasmtime-v1/' else 1)
            after=after.replace(old,new);applied.append({'old':old,'new':new,'occurrences':count})
        reverse=after
        for edit in reversed(applied):
            assert reverse.count(edit['new'])==edit['occurrences'];reverse=reverse.replace(edit['new'],edit['old'])
        assert reverse==before
        with(HERE/target).open('x')as stream:stream.write(after)
        records.append({'original':'capability/'+name,'target':target,'beforeSha256':sha(before.encode()),'afterSha256':sha(after.encode()),'edits':applied,'reverseExact':True})
    with(HERE/'transformation-proof.json').open('x')as stream:
        json.dump({'schemaVersion':1,'state':'SOURCE_ONLY_EXACT_OUTPUT_RETRY_DERIVATION','parentIndexSha256':'ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982',
          'bodyChanges':'Only explicit import rebasing and Wasmtime output references v1 to v2; all semantic/validator/config/artifact checks identical.',
          'records':records,'componentOrGuestOrHostExecuted':False},stream,indent=2);stream.write('\n')
if __name__=='__main__':main()
