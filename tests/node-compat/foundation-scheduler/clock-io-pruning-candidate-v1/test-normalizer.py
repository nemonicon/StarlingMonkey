"""Pure fixtures plus in-memory hash preparation; never publish an adapter."""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('original_clock_adapter_normalizer_template', HERE / 'normalize-adapter.py')
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)
cases = []


def check(name, callback, reject=False):
    failed = False
    try:
        callback()
    except (ValueError, UnicodeDecodeError):
        failed = True
    assert failed == reject, name
    cases.append({'name': name, 'expectedReject': reject, 'passed': True})


def name(value):
    raw = value.encode()
    return normalizer.encode_u32(len(raw)) + raw


memory = name('env') + name('memory') + b'\x02\x00\x00'
functions = [name('test:interface') + name('function-' + str(i)) + b'\x00' + normalizer.encode_u32(128 + i) for i in range(63)]
payload = normalizer.encode_u32(64) + memory + b''.join(functions)
expected = normalizer.encode_u32(64) + b''.join(functions) + memory
check('sole memory moves after unchanged ordered function entries', lambda: (_ for _ in ()).throw(ValueError('different bytes')) if normalizer.normalize_import_payload(payload) != expected else None)
check('wrong count refuses', lambda: normalizer.normalize_import_payload(b'\x3f' + payload[1:]), True)
check('truncated import payload refuses', lambda: normalizer.normalize_import_payload(payload[:-1]), True)
check('trailing payload refuses', lambda: normalizer.normalize_import_payload(payload + b'\x00'), True)
check('memory already last refuses unexpected input layout', lambda: normalizer.normalize_import_payload(expected), True)
check('nonzero memory minimum refuses', lambda: normalizer.normalize_import_payload(b'\x40' + memory[:-1] + b'\x01' + b''.join(functions)), True)
check('unhandled import kind refuses', lambda: normalizer.normalize_import_payload(b'\x40' + name('env') + name('table') + b'\x01\x70\x00\x00' + b''.join(functions)), True)
check('u32 overflow refuses', lambda: normalizer.u32(b'\xff\xff\xff\xff\x10', 0), True)
check('u32 continuation overflow refuses', lambda: normalizer.u32(b'\x80' * 6, 0), True)
check('unknown full input hash refuses', lambda: normalizer.normalized_bytes(b'\x00asm\x01\x00\x00\x00'), True)
original = HERE.parents[3] / 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
data = original.read_bytes()
normalized = normalizer.normalized_bytes(data)
assert len(data) == len(normalized) == 53512 and data != normalized
result = dict(schemaVersion=1, state='SOURCE_PREPARATION_NORMALIZER_PURE_AND_IN_MEMORY_HASH_CHECKS_V1', cases=cases,
              originalSha256=hashlib.sha256(data).hexdigest(), normalizedInputSha256=hashlib.sha256(normalized).hexdigest(),
              bytes=len(normalized), actualNormalizedBytesComputedInMemory=True, normalizedArtifactPublished=False,
              adapterPrunerExecuted=False, moduleCompiledOrExecuted=False, grantsActionAuthority=False)
with (HERE / 'normalizer-results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({key: value for key, value in result.items() if key != 'cases'}))
