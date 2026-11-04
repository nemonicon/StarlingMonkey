"""Rewire integrity only; preserve the reviewed342 metadata backend."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'integration-candidate-v1'
def digest(data): return hashlib.sha256(data).hexdigest()
def main():
    old = (PARENT / 'runtime-preflight.template.mjs').read_text()
    text = old
    edits = []
    def replace(a, b):
        nonlocal text
        assert text.count(a) == 1
        text = text.replace(a, b); edits.append({'old': a, 'new': b})
    line = "import {selectClassicPin} from './runtime-contract.mjs';"
    replace(line, line + "\nimport {verifyConsumedSeal} from './consumed.mjs';")
    start = text.index(' async function seal(){')
    end = text.index('\n await seal();', start)
    replace(text[start:end], " async function seal(){return verifyConsumedSeal(HERE,INPUTS_SHA,{PINS_SHA,INPUTS_SHA,RECIPE_SHA,SELECTOR_SHA,ADMISSION_SHA});}")
    restored = text
    for edit in reversed(edits):
        assert restored.count(edit['new']) == 1
        restored = restored.replace(edit['new'], edit['old'])
    assert restored == old
    with (HERE / 'runtime-preflight.template.mjs').open('x') as stream: stream.write(text)
    with (HERE / 'backend-transformations.json').open('x') as stream:
        json.dump({'state': 'INTEGRITY_WIRING_ONLY_342_BACKEND_UNCHANGED', 'beforeSha256': digest(old.encode()),
                   'afterSha256': digest(text.encode()), 'edits': edits, 'reverseByteExact': True}, stream, indent=2); stream.write('\n')
if __name__ == '__main__': main()
