"""Prepare source text only. No bundler, componentizer, native compiler or guest."""
from pathlib import Path
import hashlib
import json
import re
import posixpath

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent/'source-audit-v1'
PACKAGES = Path('/tmp/starling-node-compat/native-toolchain-lock/node_modules')
digest = lambda value: hashlib.sha256(value).hexdigest()

def main():
    audit = json.loads((AUDIT/'source-audit.json').read_bytes())
    graph = audit['readableCoreGraph']['reachableFiles']
    assert len(graph) == 24
    source_pins = {row['path']:row for row in audit['sources'] if row['origin']=='locked-package'}
    before = []
    transformed = []
    modules = []
    ids = {name.removeprefix('readable-stream/'):name for name in graph}
    for name in graph:
        raw = (PACKAGES/name).read_bytes()
        assert digest(raw) == source_pins[name]['sha256'], name
        target = HERE/'vendor'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as stream: stream.write(raw)
        before.append({'path':name,'sha256':digest(raw),'bytes':len(raw)})
        body = raw.decode()
        edits = []
        def replace(old,new,count=1):
            nonlocal body
            assert body.count(old)==count,(name,old,body.count(old))
            body=body.replace(old,new)
            edits.append({'old':old,'new':new,'count':count})
        if "const process = require('process/')" in body:
            replace("const process = require('process/')", '// nextTick is a private captured factory argument.')
        count=body.count('process.nextTick')
        if count:replace('process.nextTick','nextTick',count)
        if name.endswith('/readable.js'):
            replace('const doEnd = (!pipeOpts || pipeOpts.end !== false) && dest !== process.stdout && dest !== process.stderr',
                    'const doEnd = !pipeOpts || pipeOpts.end !== false // No host stdio objects exist in this profile.')
        if name.endswith(('/readable.js','/writable.js')):
            replace('Stream._isUint8Array(chunk)','Stream._isArrayBufferView(chunk)')
        if name.endswith('/state.js'):
            replace('let defaultHighWaterMarkBytes = 16 * 1024','let defaultHighWaterMarkBytes = 64 * 1024 // Deterministic Node22 POSIX baseline.')
        if name.endswith('/stream.js'):
            replace('return value instanceof Uint8Array','return isUint8Array(value)')
            replace('return Buffer.from(chunk.buffer, chunk.byteOffset, chunk.byteLength)','return byteViewToBuffer(chunk)')
            body += '\nStream._isArrayBufferView = isArrayBufferView\n'
            edits.append({'append':'Stream._isArrayBufferView = isArrayBufferView'})
        if name.endswith('/readable.js'):
            replace('    state.length += state.objectMode ? 1 : chunk.length',
                    "    checkQueueLimit(state, chunk, state.buffer.length, 'push')\n    state.length += state.objectMode ? 1 : chunk.length")
        if name.endswith('/writable.js'):
            replace('  state.pendingcb++\n  return writeOrBuffer',
                    "  checkQueueLimit(state, chunk, state.buffered.length - state.bufferedIndex + (state.writing ? 1 : 0), 'write')\n  state.pendingcb++\n  return writeOrBuffer")
        if name.endswith('/ours/primordials.js'):
            body = (HERE/'captured-primordials.cjs').read_text()
            edits.append({'replacement':'captured-primordials.cjs','reason':'Private captured native intrinsics; no package global monkeypatch shim'})
        if name.endswith('/ours/util.js'):
            body = (HERE/'private-util.cjs').read_text()
            edits.append({'replacement':'private-util.cjs','reason':'Injected native abort listener/constructors, no npm fallback or public util stub dependency'})
        if name.endswith('/ours/errors.js'):
            replace('      super(getMessage(code, message, args))',"      super(getMessage(code, message, args))\n      own(this, 'code', code)")
            replace('    err.code = outerError.code',"    own(err, 'code', outerError.code)")
            replace("    this.code = 'ABORT_ERR'\n    this.name = 'AbortError'","    own(this, 'code', 'ABORT_ERR')\n    own(this, 'name', 'AbortError')")
        # Capture existing native byte methods instead of observing application
        # replacements later. Buffer itself retains its real instance identity.
        for old,new in [('Buffer.allocUnsafe','bufferAllocUnsafe'),('Buffer.alloc','bufferAlloc'),('Buffer.from','bufferFrom'),('Buffer.isEncoding','bufferIsEncoding')]:
            count=body.count(old)
            if count:replace(old,new,count)
        assert not re.search(r'\bprocess\s*\.',body), name
        def dependency(match):
            request=match.group(2)
            if request.startswith('.'):
                resolved=posixpath.normpath(posixpath.join(posixpath.dirname(name.removeprefix('readable-stream/')),request))
                if not resolved.endswith('.js'):resolved+='.js'
                assert resolved in ids,(name,request,resolved)
                return 'require('+json.dumps(resolved)+')'
            assert request in ('buffer','events','string_decoder/','abort-controller'),(name,request)
            return 'require('+json.dumps(request)+')'
        body=re.sub(r"\brequire\((['\"])([^'\"]+)\1\)",dependency,body)
        output=HERE/'source'/name
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('x') as stream:stream.write(body)
        transformed.append({'path':name,'beforeSha256':digest(raw),'afterSha256':digest(body.encode()),'edits':edits})
        modules.append(json.dumps(name.removeprefix('readable-stream/'))+': function(module, exports, require) {\n'+body+'\n}')
    license_data=(PACKAGES/'readable-stream/LICENSE').read_bytes()
    with (HERE/'LICENSE.readable-stream').open('xb') as stream:stream.write(license_data)
    prefix=(HERE/'core-prefix.mjs').read_text()
    suffix=(HERE/'core-suffix.mjs').read_text()
    generated=prefix+'\nconst modules = {\n'+',\n'.join(modules)+'\n};\n'+suffix
    with (HERE/'classic-core.generated.mjs').open('x') as stream:stream.write(generated)
    receipt={'schemaVersion':1,'state':'SOURCE_TEXT_FACTORY_PREPARED_UNAPPLIED','node':'v22.14.0',
        'upstreamPackage':'readable-stream@4.7.0','rawSources':before,'transformations':transformed,
        'licenseSha256':digest(license_data),'generatedSha256':digest(generated.encode()),
        'sourceGraphFiles':24,'noPublicProcess':True,'componentOrNativeBuildExecuted':False}
    with (HERE/'transformation-receipt.json').open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps({'rawSources':len(before),'transformedSources':len(transformed),'state':receipt['state']}))

if __name__=='__main__':main()
