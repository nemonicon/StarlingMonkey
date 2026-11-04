"""Generate isolated runner/oracle siblings with reversible declared edits."""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ROOT = REPO / 'tests/node-compat'
MODULES = ['path', 'events', 'string-decoder', 'assert', 'querystring', 'util']


def digest(data):
    return hashlib.sha256(data).hexdigest()


rows = []


def generate(original, destination, kind, module=None):
    original, destination = ROOT / original, HERE / destination
    data = original.read_bytes()
    text, changes = data.decode(), []

    def replace(before, after, count=1):
        nonlocal text
        assert text.count(before) == count, (str(original), before, text.count(before), count)
        text = text.replace(before, after)
        changes.append(dict(before=before, after=after, count=count))

    for match in list(re.finditer(r"from (['\"])(\.[^'\"]+)\1", text)):
        source = (original.parent / match.group(2)).resolve()
        if kind == 'runner' and source == ROOT / 'foundations/native-scalar-harness.mjs':
            source = HERE / 'helpers/native-scalar-harness.mjs'
        relative = os.path.relpath(source, destination.parent).replace(os.sep, '/')
        if not relative.startswith('.'):
            relative = './' + relative
        replace(match.group(0), 'from ' + match.group(1) + relative + match.group(1), text.count(match.group(0)))

    if kind == 'helper':
        replace("resolve(dirname(fileURLToPath(import.meta.url)), '../../..')",
                "resolve(dirname(fileURLToPath(import.meta.url)), '../../../../..')")
        replace("join(here, 'native-component-results.json')", "join(output, 'native-component-results.json')")
    elif kind == 'oracle':
        if module == 'glob':
            replace("import { dirname, join } from 'node:path';", "import { dirname, join, resolve } from 'node:path';")
        replace('const here = dirname(fileURLToPath(import.meta.url));',
                "const here = resolve(dirname(fileURLToPath(import.meta.url)), '../../../foundation-path');\n"
                "assert(process.env.NODE_COMPAT_PATH_ORACLE_OUTPUT, 'Explicit fresh oracle output required');\n"
                "const oracleOutput = resolve(process.env.NODE_COMPAT_PATH_ORACLE_OUTPUT);")
        replace('await writeFile(join(here,', 'await writeFile(join(oracleOutput,', 2 if module == 'semantic' else 3)
    else:
        # Keep real fixture/oracle paths at their original source locations.
        if module in ['assert', 'querystring']:
            replace("import { dirname, join } from 'node:path';", "import { dirname, join, resolve } from 'node:path';")
        if module == 'util':
            replace("import {dirname,join} from 'node:path';", "import {dirname,join,resolve} from 'node:path';")
        replace('dirname(fileURLToPath(import.meta.url))',
                "resolve(dirname(fileURLToPath(import.meta.url)), '../../../foundation-" + module + "')")
        if module == 'events':
            replace("'sm-uncaught-event-v3-protected-abort-v2'", "'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1'")
        if module == 'path':
            marker="for (const [file, flags] of [['semantic.mjs', []], ['glob.mjs', ['--expose-internals']]]) {"
            replace(marker,
                    "const oracleScripts = resolve(dirname(fileURLToPath(import.meta.url)), '../oracles');\n"
                    "const oracleOutput = join(output, 'node-oracles');\n"
                    "await mkdir(output, { recursive: true }); await mkdir(oracleOutput, { recursive: false });\n" + marker)
            replace('join(here, file)', 'join(oracleScripts, file)')
            replace("{ encoding: 'utf8', timeout: 30000 }",
                    "{ encoding: 'utf8', timeout: 30000, env: { ...process.env, NODE_COMPAT_PATH_ORACLE_OUTPUT: oracleOutput } }")
            for filename in ['lexical-vectors.json', 'glob-vectors.json', 'glob-results.json', 'semantic-results.json']:
                replace("join(here, '" + filename + "')", "join(oracleOutput, '" + filename + "')")
            replace("({ path, sha256: hash(await readFile(join(here, path))) })",
                    "({ path, actualPath: ['lexical-vectors.json', 'glob-vectors.json'].includes(path) ? join(oracleOutput, path) : join(here, path), sha256: hash(await readFile(['lexical-vectors.json', 'glob-vectors.json'].includes(path) ? join(oracleOutput, path) : join(here, path))) })")
            replace("join(here, 'results.json')", "join(output, 'native-component-results.json')")
        elif module == 'events':
            replace("join(here, 'native-component-results.json')", "join(output, 'native-component-results.json')")
        elif module == 'string-decoder':
            replace("join(here,'native-component-results.json')", "join(output,'native-component-results.json')")

    restored = text
    for change in reversed(changes):
        assert restored.count(change['after']) == change['count'], (kind, module, change)
        restored = restored.replace(change['after'], change['before'])
    assert restored.encode() == data
    destination.parent.mkdir(exist_ok=True)
    with destination.open('x') as stream:
        stream.write(text)
    assert original.read_bytes() == data
    rows.append(dict(original=str(original.relative_to(REPO)), originalSha256=digest(data),
                     generated=str(destination.relative_to(HERE)), generatedSha256=digest(text.encode()),
                     kind=kind, module=module, changes=changes, reverseDeclaredEditsRestoresOriginalBytes=True))


for module in MODULES:
    name = 'run.mjs' if module == 'path' else 'run-native-component.mjs'
    generate('foundation-' + module + '/' + name, 'runners/' + module + '.mjs', 'runner', module)
generate('foundations/native-scalar-harness.mjs', 'helpers/native-scalar-harness.mjs', 'helper')
for module in ['semantic', 'glob']:
    generate('foundation-path/' + module + '.mjs', 'oracles/' + module + '.mjs', 'oracle', module)
with (HERE / 'runner-transformations.json').open('x') as stream:
    json.dump(dict(schemaVersion=1, state='ISOLATED_REVERSIBLE_ADMISSION_PATH_AND_REPORT_TRANSFORMS', files=rows), stream, indent=2)
    stream.write('\n')
print(json.dumps(dict(generated=len(rows), originalsUnchanged=True, nativeOrGuestExecuted=False)))
