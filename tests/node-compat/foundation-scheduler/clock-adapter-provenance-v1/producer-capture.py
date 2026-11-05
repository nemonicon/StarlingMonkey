"""Read only the selected adapter's producers custom-section metadata."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'


def u32(data, position):
    value = 0
    for shift in range(0, 35, 7):
        assert position < len(data)
        byte = data[position]
        position += 1
        value |= (byte & 127) << shift
        if byte < 128:
            assert value <= 0xffffffff
            return value, position
    raise ValueError('bounded u32')


def name(data, position):
    size, position = u32(data, position)
    assert position + size <= len(data)
    return data[position:position + size].decode(), position + size


def main():
    data = PATH.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    assert sha == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
    assert data[:8] == b'\0asm\1\0\0\0'
    position = 8
    found = []
    while position < len(data):
        kind = data[position]
        size, start = u32(data, position + 1)
        end = start + size
        assert end <= len(data)
        if kind == 0:
            section, cursor = name(data, start)
            if section == 'producers':
                count, cursor = u32(data, cursor)
                fields = []
                for _ in range(count):
                    field, cursor = name(data, cursor)
                    values_count, cursor = u32(data, cursor)
                    values = []
                    for _ in range(values_count):
                        tool, cursor = name(data, cursor)
                        version, cursor = name(data, cursor)
                        values.append(dict(name=tool, version=version))
                    fields.append(dict(field=field, values=values))
                assert cursor == end
                found.append(fields)
        position = end
    assert len(found) == 1
    print(json.dumps(dict(schemaVersion=1, path=str(PATH), sha256=sha, bytes=len(data),
                         producers=found[0], exactSourceBuildRevisionEstablished=False,
                         instructionBodiesDecoded=False, moduleExecuted=False), indent=2))


if __name__ == '__main__':
    main()
