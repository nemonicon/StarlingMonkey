#!/usr/bin/env python3
"""Actual two-TU Release syntax only; candidate/frozen include overlay, no link/run."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import re
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
V1 = HERE.parent
BASE = Path('/tmp/starling-node-compat/foundations-v7/native-freeze')
REPOSITORY = V1.parents[3]
digest = lambda data: hashlib.sha256(data).hexdigest()
v1_index_bytes = (V1 / 'index.json').read_bytes()
for item in json.loads(v1_index_bytes)['files']:
    assert digest((V1 / item['path']).read_bytes()) == item['sha256']
receipt_bytes = (BASE / 'off-foundations.engine.wasm.build.json').read_bytes()
receipt = json.loads(receipt_bytes)
assert digest((BASE / 'off-foundations.engine.wasm').read_bytes()) == receipt['engineSha256'] == 'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09'
commands_path = Path(receipt['cmakeCachePath']).with_name('compile_commands.json')
commands_bytes = commands_path.read_bytes()
assert digest(commands_bytes) == receipt['compileCommandsSha256']
commands = json.loads(commands_bytes)
out = Path(os.environ.get('NODE_COMPAT_BLOB_SYNTAX_OUTPUT', '/tmp/starling-node-compat/blob-owned-copy-v2-syntax'))
out.mkdir(parents=True, exist_ok=True)
report_path = out / 'results.json'
assert not report_path.exists(), 'Preserve earlier syntax results; select fresh output'
overlay = HERE / 'source/builtins/web'
frozen_web = BASE / 'source/builtins/web'
entries = [next(c for c in commands if c['file'].endswith('/builtins/web/' + name + '.cpp')) for name in ('blob','file')]
wrapper = Path((entries[0].get('arguments') or shlex.split(entries[0]['command']))[0])
wrapper_bytes = wrapper.read_bytes()
compiler_match = re.search(r'(/[^\s"\']+/bin/clang\+\+)', wrapper_bytes.decode())
assert compiler_match, 'Record actual SDK compiler from the pinned wrapper'
compiler = Path(compiler_match.group(1))
version = subprocess.run([str(compiler),'--version'],capture_output=True,text=True,check=True)

def syntax(entry):
    original = entry.get('arguments') or shlex.split(entry['command'])
    args, i = [], 0
    while i < len(original):
        arg = original[i]
        if arg in ('-o','-MF','-MT','-MQ'):
            i += 2
            continue
        if arg in ('-c','-MD','-MMD') or arg == entry['file']:
            i += 1
            continue
        if arg.startswith('-I' + str(REPOSITORY) + '/'):
            relative = arg[len('-I' + str(REPOSITORY) + '/'):]
            frozen = BASE / 'source' / relative
            if frozen.is_dir():
                arg = '-I' + str(frozen)
        args.append(arg)
        i += 1
    source = overlay / Path(entry['file']).name
    args.extend(['-iquote',str(overlay),'-iquote',str(frozen_web),'-H','-fsyntax-only',str(source)])
    result = subprocess.run(args,cwd=entry['directory'],capture_output=True,text=True)
    header_paths = [Path(line.lstrip('. ').strip()) for line in result.stderr.splitlines() if re.match(r'^\.+ /',line)]
    # Prove the copied candidate headers resolve, instead of production headers.
    for name in ('blob.h','file.h'):
        assert overlay / name in header_paths, (source, name)
        assert REPOSITORY / 'builtins/web' / name not in header_paths
    header_evidence = []
    for header in sorted(set(header_paths)):
        if header.is_file():
            header_evidence.append({'path':str(header),'sha256':digest(header.read_bytes())})
    return {'source':str(source),'sourceSha256':digest(source.read_bytes()),'command':args,'cwd':entry['directory'],
        'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'headers':header_evidence}

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(syntax,entries))
report = {'schema':1,'candidateVersion':'native-blob-owned-copy-v2','state':'sdk30-sm147-two-tu-syntax-pass' if all(r['exitCode']==0 for r in results) else 'syntax-failed',
    'scope':'C++ syntax/headers only; no linked engine, native runtime, GC, invalid receiver or allocation fault test.',
    'v1IndexSha256':digest(v1_index_bytes),'baseEngineSha256':receipt['engineSha256'],'baseReceiptSha256':digest(receipt_bytes),
    'compileCommandsPath':str(commands_path),'compileCommandsSha256':digest(commands_bytes),
    'compiler':{'wrapper':str(wrapper),'wrapperSha256':digest(wrapper_bytes),'path':str(compiler),'sha256':digest(compiler.read_bytes()),'version':version.stdout},
    'includeOverlay':{'candidate':str(overlay),'fallbackWebHeaders':str(frozen_web),'frozenExistingIncludeDirectories':True},
    'results':results,'driverSha256':digest(Path(__file__).read_bytes()),'contractProofSha256':digest((HERE/'contract-proof.json').read_bytes()),
    'coordination':'Toolchain agent confirmed no active timing window; two syntax TUs may run alongside the private v3 Release build.'}
report_path.write_text(json.dumps(report,indent=2)+'\n')
(HERE/'sdk-syntax-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'state':report['state'],'translationUnits':len(results),'exitCodes':[r['exitCode'] for r in results],'output':str(report_path)}))
raise SystemExit(0 if all(r['exitCode']==0 for r in results) else 1)
