"""Text-only V5 descendant: one private helper declaration and one owned-try call."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'next-component-entry-fixes-v5'
START = '// Standard WASI HTTP resource ownership -> ordinary Web Request/Response.'
END = '// Pure orchestration, inlined unchanged into each raw guest entry.'
FUNCTION = 'function createWasiHttpHandler(webHandler,types,runFreshRequest){'
NEEDLE = "      request=new Request(url,{method,headers,signal:ioAbort.signal,...(body?{body,duplex:'half'}:{})});\n"
CALL = '      recordCacheAffinityAdmission(method,url);\n'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def family():
    expected = dict(path=str(BASE / 'index.json'), sha256='73b583bed57a6e988debe5abca156abcd2e4b5ed331b1b4171f8636d33bf1042', bytes=2914)
    assert row(BASE / 'index.json') == expected
    value = json.loads((BASE / 'index.json').read_bytes())
    assert {r['path'] for r in value['files']} | {'index.json'} == {str(p.relative_to(BASE)) for p in BASE.rglob('*') if p.is_file()}
    for r in value['files']:
        path = BASE / r['path']
        assert not path.is_symlink() and row(path) == dict(r, path=str(path))
    return expected


def render():
    source_index = family()
    original = (BASE / 'guest-entry.mjs').read_text()
    assert row(BASE / 'guest-entry.mjs')['sha256'] == '1e49ddc61094f25a46056f10869e2ec409ef03d1b2a762670720666d3dc9bf4c'
    assert original.count(START) == original.count(END) == original.count(FUNCTION) == original.count(NEEDLE) == 1
    helper = (HERE / 'cache-affinity.mjs').read_text()
    assert helper.count('export function ') == 1
    declaration = helper.replace('export function ', 'function ') + '\n'
    output = original.replace(FUNCTION, declaration + FUNCTION).replace(NEEDLE, NEEDLE + CALL)
    assert output.replace(declaration, '', 1).replace(CALL, '', 1) == original
    start, end = original.index(START), original.index(END)
    assert output[:start] == original[:start] and output.endswith(original[end:])
    family()
    proof = dict(schemaVersion=1, sourceOnly=True, baseSourceIndex=source_index,
        baseEntry=row(BASE / 'guest-entry.mjs'), baseComposition=row(BASE / 'composition.json'),
        helper=row(HERE / 'cache-affinity.mjs'), assembler=row(Path(__file__).resolve()),
        unchangedPrefix=dict(bytes=len(original[:start].encode()), sha256=hashlib.sha256(original[:start].encode()).hexdigest()),
        unchangedSuffix=dict(bytes=len(original[end:].encode()), sha256=hashlib.sha256(original[end:].encode()).hexdigest()),
        exactTransforms=['Inline one private helper declaration inside the adapter span.', 'Insert one two-argument call after actual Request construction inside the existing owned try.'],
        helperHasOnlyFunctionDeclarationAtInit=True, sixFacadesByteIdentical=True, bootstrapReadinessNativeBoundariesByteIdentical=True,
        applicationRewritten=False, nativeSourceChanged=False, worldChanged=False, newHostImports=False,
        rawEntryEvaluated=False, actualRootAuthority=None, actualComponent=None, actualRuntime=None)
    return output, proof, ''.join(difflib.unified_diff(original.splitlines(True), output.splitlines(True), fromfile='held-v5/guest-entry.mjs', tofile='cache-affinity-v1/guest-entry.mjs'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write only this fresh Source descendant; no entry evaluation.')
    args = parser.parse_args()
    output, proof, diff = render()
    target = HERE / 'guest-entry.mjs'
    if args.write:
        for path in [target, HERE / 'composition.json', HERE / 'entry-diff.patch']:
            assert not path.exists()
        target.write_text(output)
        proof['entry'] = row(target)
        (HERE / 'composition.json').write_text(json.dumps(proof, indent=2) + '\n')
        (HERE / 'entry-diff.patch').write_text(diff)
    else:
        assert target.read_text() == output
        assert (HERE / 'entry-diff.patch').read_text() == diff
    print(json.dumps(dict(sourceOnly=True, entry=row(target), rawEntryEvaluated=False)))
