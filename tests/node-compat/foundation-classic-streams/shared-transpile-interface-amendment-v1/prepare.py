"""Derive only the shared generated declaration writer; never edit a sealed family."""
from pathlib import Path
import hashlib
import json
import difflib

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'harness-completion-amendment-v1'
PARENT_INDEX = '76e735336884634ab4811963586738da6c70fdcda722a74706e917a07c615489'
def sha(data): return hashlib.sha256(data).hexdigest()
def put(name, data):
    path = HERE / name; path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream: stream.write(data)
def main():
    assert sha((PARENT / 'index.json').read_bytes()) == PARENT_INDEX
    for row in json.loads((PARENT / 'index.json').read_bytes())['files']:
        assert sha((PARENT / row['path']).read_bytes()) == row['sha256']
    proof = []; patch = []
    for name in ('completion.mjs', 'component-driver.mjs'):
        before = (PARENT / 'proposed/harness' / name).read_text(); after = before; edits = []
        def replace(old, new, count=1):
            nonlocal after
            assert after.count(old) == count, (name, old, after.count(old))
            after = after.replace(old, new); edits.append({'old':old,'new':new,'occurrences':count})
        if name == 'completion.mjs':
            replace('  const paths = new Set();', '  const paths = new Set();\n  const written = new Map();')
            replace('    paths.add(target);', "    paths.add(target);\n    const bytes = typeof data === 'string' ? Buffer.from(data, options.encoding ?? 'utf8') : Buffer.from(data);\n    written.set(target, { sha256: hash(bytes), bytes: bytes.length });")
            replace('  return Object.freeze({ write, paths });', '''  // Jco may emit a shared interface declaration for multiple components.
  // Only exact declarations created by this writer may be reused. All other
  // outputs retain exclusive creation; an old directory is never repaired.
  async function writeGenerated(path, data, options) {
    const { target, name } = below(output, path);
    assert(options?.flag === 'wx', 'Generated outputs require exclusive creation');
    if (!paths.has(target)) return write(target, data, options);
    assert(/^interfaces\\/[A-Za-z0-9][A-Za-z0-9._-]*\\.d\\.ts$/.test(name),
      'Only already-tracked interface declarations may repeat');
    await ordinaryParent(output, target);
    const previous = await ordinaryFile(output, target);
    const bytes = typeof data === 'string' ? Buffer.from(data, options.encoding ?? 'utf8') : Buffer.from(data);
    const original = written.get(target);
    assert(original && original.sha256 === previous.sha256 && original.bytes === previous.bytes,
      'Tracked declaration changed after creation');
    assert.equal(hash(bytes), original.sha256, 'Repeated declaration differs');
    assert.equal(bytes.length, original.bytes, 'Repeated declaration length differs');
    assert((await readFile(target)).equals(bytes), 'Repeated declaration bytes differ');
  }
  return Object.freeze({ write, writeGenerated, paths });''')
        else:
            replace("await writeOutput(join(output,name),bytes,{flag:'wx'});", "await tracked.writeGenerated(join(output,name),bytes,{flag:'wx'});", 2)
        restored = after
        for edit in reversed(edits):
            assert restored.count(edit['new']) == edit['occurrences']
            restored = restored.replace(edit['new'],edit['old'])
        assert restored == before
        put('before/' + name, before.encode()); put('proposed/harness/' + name, after.encode())
        proof.append({'path':name,'beforeSha256':sha(before.encode()),'afterSha256':sha(after.encode()),'edits':edits,'exactReverseProof':True})
        patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/harness/'+name,tofile='b/harness/'+name))
    put('shared-transpile-interface.UNAPPLIED.patch', ''.join(patch).encode())
    put('transformation-proof.json', (json.dumps({'schemaVersion':1,'state':'GENERATED_DECLARATION_REUSE_ONLY_REVERSIBLE_SOURCE',
        'completionAmendmentIndexSha256':PARENT_INDEX,'files':proof,'guestSemanticBytesChanged':False,
        'producerOrGuestInvoked':False},indent=2)+'\n').encode())
if __name__ == '__main__': main()
