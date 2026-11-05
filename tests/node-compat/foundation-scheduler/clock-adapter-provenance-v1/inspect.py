"""Read pinned adapter section/import metadata; never compile or execute Wasm."""
from pathlib import Path
import hashlib
import json

REPO = Path(__file__).resolve().parents[4]
ORIGINAL = REPO / 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
UPSTREAM = Path('/private/tmp/starling-node-compat/clock-adapter-provenance-v1/upstream-v25.0.0-reactor.wasm')


def need(value, message):
    if not value:
        raise ValueError(message)


class Reader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def byte(self):
        need(self.pos < len(self.data), 'bounded byte')
        value = self.data[self.pos]
        self.pos += 1
        return value

    def u32(self):
        value = 0
        for shift in range(0, 35, 7):
            byte = self.byte()
            value |= (byte & 127) << shift
            if byte < 128:
                need(value <= 0xffffffff, 'u32 range')
                return value
        raise ValueError('bounded u32 LEB')

    def take(self, size):
        need(self.pos + size <= len(self.data), 'bounded slice')
        value = self.data[self.pos:self.pos + size]
        self.pos += size
        return value

    def name(self):
        return self.take(self.u32()).decode('utf-8')

    def limits(self):
        flags = self.u32()
        need(flags in (0, 1), 'this pinned adapter uses unshared memory32/table limits')
        result = {'flags': flags, 'min': self.u32()}
        if flags == 1:
            result['max'] = self.u32()
        return result


def inspect(path, expected_sha):
    data = path.read_bytes()
    need(hashlib.sha256(data).hexdigest() == expected_sha, 'exact adapter bytes')
    need(data[:8] == b'\0asm\1\0\0\0', 'core Wasm version')
    reader = Reader(data[8:])
    sections = []
    imports = []
    while reader.pos < len(reader.data):
        kind = reader.byte()
        payload = reader.take(reader.u32())
        section = {'id': kind, 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()}
        if kind == 0:
            section['name'] = Reader(payload).name()
        if kind == 2:
            imported = Reader(payload)
            for index in range(imported.u32()):
                row = {'importIndex': index, 'module': imported.name(), 'name': imported.name()}
                row['kind'] = imported.byte()
                if row['kind'] == 0:
                    row['functionIndex'] = sum(item['kind'] == 0 for item in imports)
                    row['typeIndex'] = imported.u32()
                elif row['kind'] == 1:
                    row['elementType'] = imported.byte()
                    row['limits'] = imported.limits()
                elif row['kind'] == 2:
                    row['limits'] = imported.limits()
                elif row['kind'] == 3:
                    row['valueType'] = imported.byte()
                    row['mutable'] = imported.byte()
                else:
                    raise ValueError('unhandled import kind in exact pinned input')
                imports.append(row)
            need(imported.pos == len(payload), 'complete import section')
        sections.append(section)
    return {'path': str(path), 'sha256': expected_sha, 'bytes': len(data), 'sections': sections,
            'imports': imports,
            'allFunctionImportIndicesEqualEntryIndices': all(row['importIndex'] == row['functionIndex'] for row in imports if row['kind'] == 0)}


def main():
    result = {
        'schemaVersion': 1,
        'state': 'READ_ONLY_PINNED_ADAPTER_METADATA_COMPARISON_V1',
        'repository': inspect(ORIGINAL, '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'),
        'upstreamV25': inspect(UPSTREAM, '240c28b2561e2d32daef30112bb2aaeb6427976de731401b806d7e32a1a27326'),
        'exactSourceRevisionEstablished': False,
        'codeInstructionsDecoded': False,
        'memoryContentsDecoded': False,
        'moduleCompiledOrExecuted': False,
        'adapterRewriteAdmission': False,
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
