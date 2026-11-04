"""Existing narrow public binary reader; no component execution."""
def uint(data,pos):
    value,shift = 0,0
    while True:
        assert pos < len(data) and shift <= 63
        byte = data[pos];pos += 1
        value |= (byte&127)<<shift
        if byte < 128:
            return value,pos
        shift += 7


def string(data,pos):
    size,pos = uint(data,pos)
    assert pos+size <= len(data)
    return data[pos:pos+size].decode(),pos+size


def sections(data,header):
    assert data[:8] == header
    pos = 8
    while pos < len(data):
        kind = data[pos];size,start = uint(data,pos+1);end = start+size
        assert end <= len(data)
        yield kind,data[start:end]
        pos = end
    assert pos == len(data)


def limits(data,pos):
    flags,pos = uint(data,pos)
    _,pos = uint(data,pos)
    if flags&1:
        _,pos = uint(data,pos)
    return pos


def core_imports(data):
    result = []
    for kind,part in sections(data,bytes.fromhex('0061736d01000000')):
        if kind != 2:
            continue
        count,pos = uint(part,0)
        for _ in range(count):
            module,pos = string(part,pos);name,pos = string(part,pos)
            tag = part[pos];pos += 1
            if tag == 0:
                _,pos = uint(part,pos);kind_name = 'function'
            elif tag == 1:
                assert part[pos] in [0x70,0x6f];pos = limits(part,pos+1);kind_name = 'table'
            elif tag == 2:
                pos = limits(part,pos);kind_name = 'memory'
            elif tag == 3:
                pos += 2;kind_name = 'global'
            elif tag == 4:
                pos += 1;_,pos = uint(part,pos);kind_name = 'tag'
            else:
                raise AssertionError(('Unsupported import descriptor',tag))
            result.append(dict(module=module,name=name,kind=kind_name))
        assert pos == len(part)
    return result

