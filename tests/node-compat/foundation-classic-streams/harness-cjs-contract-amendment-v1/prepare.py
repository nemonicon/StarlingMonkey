"""Correct only fixture CJS placement. Never edit the sealed predecessor."""
from pathlib import Path
import hashlib
import json
import difflib

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'integration-candidate-v1'
INDEX = '5826a3dfc8d79ebbbbd139665dd06f9f493af3aa6f48302f2865611591fcff6d'
def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    assert sha((PARENT / 'index.json').read_bytes()) == INDEX
    rows = json.loads((PARENT / 'index.json').read_bytes())['files']
    expected = next(row['sha256'] for row in rows if row['path'] == 'harness/guest.mjs')
    old = (PARENT / 'harness/guest.mjs').read_text(); assert sha(old.encode()) == expected
    text = old; edits = []
    def replace(a, b):
        nonlocal text
        assert text.count(a) == 1
        text = text.replace(a, b); edits.append({'old':a,'new':b})
    line = "import { checks } from './checks.mjs';"
    replace(line, line + "\nimport cjsBindings from './cjs-bindings.cjs';")
    old_block = """// These four literal calls are the selected bundler's static CJS contract.
// No public runtime require() is installed or used after bundling.
const cjs = require('node:stream');
const cjsAlias = require('stream');
const cjsPromises = require('node:stream/promises');
const cjsPromisesAlias = require('stream/promises');"""
    replace(old_block, """// Literal require calls live in the explicit .cjs fixture module.
// No public runtime require() is installed or used after bundling.
const {cjs, cjsAlias, cjsPromises, cjsPromisesAlias} = cjsBindings;""")
    restored = text
    for edit in reversed(edits):
        assert restored.count(edit['new']) == 1; restored = restored.replace(edit['new'], edit['old'])
    assert restored == old and ' = require(' not in text
    helper = """// Explicit static CJS fixture; only admitted literal builtin requires.
module.exports = {
  cjs: require('node:stream'),
  cjsAlias: require('stream'),
  cjsPromises: require('node:stream/promises'),
  cjsPromisesAlias: require('stream/promises'),
};
"""
    (HERE / 'before').mkdir(exist_ok=False)
    (HERE / 'proposed/harness').mkdir(parents=True, exist_ok=False)
    for path, data in [(HERE/'before/guest.mjs',old),(HERE/'proposed/harness/guest.mjs',text),(HERE/'proposed/harness/cjs-bindings.cjs',helper)]:
        with path.open('x') as stream: stream.write(data)
    patch = ''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='a/harness/guest.mjs',tofile='b/harness/guest.mjs'))
    patch += ''.join(difflib.unified_diff([],helper.splitlines(True),fromfile='/dev/null',tofile='b/harness/cjs-bindings.cjs'))
    with (HERE/'harness-cjs.UNAPPLIED.patch').open('x') as stream: stream.write(patch)
    proof = {'schemaVersion':1,'state':'REVERSIBLE_CJS_FIXTURE_PLACEMENT_ONLY','parentIndexSha256':INDEX,
        'beforeGuestSha256':expected,'afterGuestSha256':sha(text.encode()),'cjsSha256':sha(helper.encode()),
        'patchSha256':sha(patch.encode()),'edits':edits,'reverseRestoresExactGuest':True,
        'ordinaryChecksOrIdentityAssertionsChanged':False,'nativeOrGuestExecuted':False}
    with (HERE/'transformation-proof.json').open('x') as stream: json.dump(proof,stream,indent=2);stream.write('\n')
    print(json.dumps({key:value for key,value in proof.items() if key!='edits'}))
if __name__ == '__main__': main()
