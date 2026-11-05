"""UNREVIEWED build template: normalize only the exact pinned adapter's import order.

The selected wirm 5.0.0 replacement path uses import entry IDs as function IDs.
The original adapter imports memory first. Moving its sole memory import after
the functions preserves every Wasm index space, without decoding instructions.
No normalization, stubbing or artifact publication happens at import time.
"""
from pathlib import Path
import hashlib
import os
import stat

EXPECTED_SHA256 = '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
NORMALIZED_SHA256 = '667907826ed62123beb0c1817969dcf32527a02b4bcbbbb10dc1dcafaba12ecc'


def need(value, message):
    if not value:
        raise ValueError(message)


def u32(data, position):
    value = 0
    for shift in range(0, 35, 7):
        need(position < len(data), 'bounded u32')
        byte = data[position]
        position += 1
        value |= (byte & 127) << shift
        if byte < 128:
            need(value <= 0xffffffff, 'u32 range')
            return value, position
    raise ValueError('bounded LEB')


def encode_u32(value):
    need(isinstance(value, int) and 0 <= value <= 0xffffffff, 'u32 value')
    result = bytearray()
    while True:
        byte = value & 127
        value >>= 7
        result.append(byte | (128 if value else 0))
        if not value:
            return bytes(result)


def skip_name(data, position):
    length, position = u32(data, position)
    need(position + length <= len(data), 'bounded import name')
    data[position:position + length].decode('utf-8')
    return position + length


def normalize_import_payload(payload):
    count, position = u32(payload, 0)
    need(count == 64, 'exact pinned import count')
    entries = []
    kinds = []
    for index in range(count):
        start = position
        position = skip_name(payload, position)
        position = skip_name(payload, position)
        need(position < len(payload), 'import kind')
        kind = payload[position]
        position += 1
        if kind == 0:
            _, position = u32(payload, position)
        elif kind == 2:
            flags, position = u32(payload, position)
            minimum, position = u32(payload, position)
            need(index == 0 and flags == 0 and minimum == 0, 'sole unshared memory32 import first')
        else:
            raise ValueError('this adapter has only function and memory imports')
        entries.append(payload[start:position])
        kinds.append(kind)
    need(position == len(payload), 'complete import payload')
    need(kinds == [2] + [0] * 63, 'exact pinned import kind sequence')
    normalized = encode_u32(count) + b''.join(entries[1:] + entries[:1])
    need(len(normalized) == len(payload), 'unchanged section size')
    return normalized


def normalized_bytes(data):
    need(len(data) == 53512, 'exact pinned input size')
    need(hashlib.sha256(data).hexdigest() == EXPECTED_SHA256, 'exact reviewed binary input')
    need(data[:8] == b'\0asm\1\0\0\0', 'core Wasm input')
    result = bytearray(data[:8])
    position = 8
    imports = 0
    while position < len(data):
        start = position
        kind = data[position]
        size, payload_start = u32(data, position + 1)
        end = payload_start + size
        need(end <= len(data), 'bounded section')
        if kind == 2:
            imports += 1
            result.extend(data[start:payload_start])
            result.extend(normalize_import_payload(data[payload_start:end]))
        else:
            result.extend(data[start:end])
        position = end
    need(imports == 1, 'one import section')
    need(len(result) == len(data), 'unchanged module size')
    normalized = bytes(result)
    need(hashlib.sha256(normalized).hexdigest() == NORMALIZED_SHA256, 'exact normalized binary output')
    return normalized


def write_normalized(input_path, output_path):
    # Future reviewed build caller supplies the exact authenticated input and a
    # fresh private output directory. Partial failed outputs stay unaccepted.
    output = Path(output_path)
    need(output.is_absolute() and '..' not in output.parts, 'absolute output')
    need(all(not p.is_symlink() for p in (output, *output.parents)), 'no output symlinks')
    need(output.parent.is_dir() and stat.S_IMODE(output.parent.stat().st_mode) == 0o700, 'private output parent')
    source = Path(input_path)
    need(source.is_file() and not source.is_symlink(), 'regular input')
    before = source.stat()
    need(before.st_size == 53512, 'bounded exact input')
    data = normalized_bytes(source.read_bytes())
    after = source.stat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    need(identity(before) == identity(after), 'stable exact input')
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        # The finally owns the fd even when wrapping it fails. The buffered
        # wrapper must therefore leave fd closure to that single owner.
        with os.fdopen(descriptor, 'wb', closefd=False) as stream:
            need(stream.write(data) == len(data), 'complete normalized output write')
            stream.flush()
            os.fsync(stream.fileno())
            current = os.fstat(stream.fileno())
            need(stat.S_ISREG(current.st_mode) and stat.S_IMODE(current.st_mode) == 0o600 and current.st_size == len(data), 'complete private output')
    finally:
        os.close(descriptor)
    return {'path': str(output), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
