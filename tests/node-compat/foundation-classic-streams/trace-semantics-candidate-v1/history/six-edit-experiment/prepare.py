"""Isolated writable semantic afterimages; leave canonical source342 untouched."""
from pathlib import Path
import hashlib,json,posixpath,re,difflib
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
CANONICAL=REPO/'builtins/node-compat/classic-streams'
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,data):
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as stream:stream.write(data)
def main():
    receipt=json.loads((CANONICAL/'transformation-receipt.json').read_bytes())
    name='readable-stream/lib/internal/streams/writable.js';record=next(row for row in receipt['transformations']if row['path']==name)
    raw=(CANONICAL/'vendor'/name).read_bytes();assert sha(raw)==record['beforeSha256'];body=raw.decode()
    for edit in record['edits']:
        assert 'old'in edit and body.count(edit['old'])==edit['count'];body=body.replace(edit['old'],edit['new'])
    def require(match):
        target=match.group(2)
        if target.startswith('.'):target=posixpath.normpath(posixpath.join('lib/internal/streams',target));target+= ''if target.endswith('.js')else'.js'
        return 'require('+json.dumps(target)+')'
    body=re.sub(r'\brequire\(([\'"])([^\'"]+)\1\)',require,body)
    assert sha(body.encode())==record['afterSha256'];before=body;edits=[]
    def replace(old,new):
        nonlocal body
        assert body.count(old)==1,old;offset=body.index(old);body=body.replace(old,new);edits.append({'old':old,'new':new,'count':1,'offset':offset})
    replace("  if (typeof encoding === 'function') {\n    cb = encoding\n    encoding = state.defaultEncoding\n  } else {\n    if (!encoding) encoding = state.defaultEncoding\n    else if (encoding !== 'buffer' && !bufferIsEncoding(encoding)) throw new ERR_UNKNOWN_ENCODING(encoding)\n    if (typeof cb !== 'function') cb = nop\n  }",
        "  if (typeof cb !== 'function') cb = nop")
    replace("  } else if (!state.objectMode) {\n    if (typeof chunk === 'string') {",
        "  } else if (!state.objectMode) {\n    if (!encoding) encoding = state.defaultEncoding\n    else if (encoding !== 'buffer' && !bufferIsEncoding(encoding)) throw new ERR_UNKNOWN_ENCODING(encoding)\n    if (typeof chunk === 'string') {")
    replace("Writable.prototype.write = function (chunk, encoding, cb) {\n  return _write(this, chunk, encoding, cb) === true\n}",
        "Writable.prototype.write = function (chunk, encoding, cb) {\n  if (encoding != null && typeof encoding === 'function') {\n    cb = encoding\n    encoding = null\n  }\n  return _write(this, chunk, encoding, cb) === true\n}")
    replace("  // stream._write resets state.length\n  const ret = state.length < state.highWaterMark\n  // We must ensure that previous needDrain will not be reset to false.\n  if (!ret) state.needDrain = true\n",'')
    replace("  // Return false if errored or destroyed in order to break\n  // any synchronous while(stream.write(data)) loops.\n  return ret && !state.errored && !state.destroyed",
        "  // Node22 checks the remaining queue after a synchronous _write callback.\n  const ret = state.length < state.highWaterMark || state.length === 0\n  if (!ret) state.needDrain = true\n\n  // Return false if errored or destroyed in order to break\n  // any synchronous while(stream.write(data)) loops.\n  return ret && !state.errored && !state.destroyed")
    replace("  finishMaybe(stream, state)\n}\n\n// If there's something in the buffer waiting, then invoke callbacks.",
        "  if (state.ending) finishMaybe(stream, state, true)\n}\n\n// If there's something in the buffer waiting, then invoke callbacks.")
    core=(CANONICAL/'classic-core.generated.mjs').read_text();assert sha(core.encode())==receipt['generatedSha256']
    assert core.count(before)==1;after=core.replace(before,body)
    put('before/writable.transformed.js',before.encode());put('proposed/writable.transformed.js',body.encode())
    put('proposed/classic-core.generated.mjs',after.encode());put('proposed/classic-streams.mjs',(CANONICAL/'classic-streams.mjs').read_bytes())
    restored=body
    for edit in reversed(edits):
        at=edit['offset'];assert restored[at:at+len(edit['new'])]==edit['new'];restored=restored[:at]+edit['old']+restored[at+len(edit['new']):]
    assert restored==before
    put('writable.UNAPPLIED.patch',''.join(difflib.unified_diff(before.splitlines(True),body.splitlines(True),fromfile='a/writable.transformed.js',tofile='b/writable.transformed.js')).encode())
    put('transformation-proof.json',(json.dumps({'schemaVersion':1,'state':'ISOLATED_WRITABLE_NODE22_SEMANTICS_SOURCE_PROPOSAL',
      'canonicalCoreBeforeSha256':sha(core.encode()),'candidateCoreSha256':sha(after.encode()),'writableBeforeSha256':sha(before.encode()),'writableAfterSha256':sha(body.encode()),
      'edits':edits,'exactReverseProof':True,'schedulerChanged':False,'liveSourcesChanged':False,'nativePinsChanged':False,'compiledOrGuestExecuted':False},indent=2)+'\n').encode())
    workload=REPO/'tests/node-compat/foundation-classic-streams/measurement-workload-candidate-v1'
    for name in ('workload.mjs','node-provider.mjs'):
        data=(workload/name).read_bytes();put('workload/'+name,data)
    put('workload/source-pins.json',(json.dumps({'schemaVersion':1,'files':[{'path':name,'origin':str(workload/name),'sha256':sha((workload/name).read_bytes())}for name in ('workload.mjs','node-provider.mjs')],
      'workloadSemanticsChanged':False},indent=2)+'\n').encode())
if __name__=='__main__':main()
