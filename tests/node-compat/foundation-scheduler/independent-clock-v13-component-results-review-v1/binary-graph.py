"""Bounded metadata/import decoder; never compiles/instantiates, reads code or data payloads."""
import hashlib
import json
from pathlib import Path

OWN = Path(__file__).resolve().parent
CORE = b'\0asm\1\0\0\0'
COMPONENT = b'\0asm\r\0\1\0'


class R:
    def __init__(self, data): self.b, self.p = data, 0
    def byte(self):
        assert self.p < len(self.b)
        v = self.b[self.p]; self.p += 1; return v
    def u(self):
        v = 0
        for i in range(5):
            x = self.byte(); v |= (x & 127) << (7 * i)
            if not x & 128: return v
        raise AssertionError('bounded u32')
    def signed(self):
        v = 0
        for i in range(5):
            x = self.byte(); v |= (x & 127) << (7 * i)
            if not x & 128: return v - (1 << (7 * (i + 1))) if x & 64 else v
        raise AssertionError('bounded signed type')
    def string(self):
        n = self.u(); assert n <= 16384 and self.p + n <= len(self.b)
        v = self.b[self.p:self.p+n].decode('utf8'); self.p += n; return v
    def name(self):
        assert self.byte() in (0, 1)
        return self.string()
    def done(self): assert self.p == len(self.b), ('unconsumed metadata', self.p, len(self.b))


def sha(data): return hashlib.sha256(data).hexdigest()


def sections(data, header):
    assert data[:8] == header
    r = R(data); r.p = 8; out = []
    while r.p < len(data):
        tag = r.byte(); n = r.u(); start = r.p
        assert start + n <= len(data)
        out.append(dict(id=tag, offset=start, bytes=n, sha256=sha(data[start:start+n])))
        r.p += n
    r.done(); return out


def limits(r):
    flags = r.u(); assert flags < 4
    result = dict(flags=flags, minimum=r.u())
    if flags & 1: result['maximum'] = r.u()
    return result


def core(data, section):
    ss = sections(data, CORE); imports, exports, names, elements, shim_bodies = [], [], [], [], []
    for row in ss:
        r = R(data[row['offset']:row['offset']+row['bytes']])
        if row['id'] == 2:
            for _ in range(r.u()):
                imp = dict(module=r.string(), name=r.string()); k = r.byte()
                if k == 0: imp.update(kind='function', typeIndex=r.u())
                elif k == 1: imp.update(kind='table', elementType=r.byte(), limits=limits(r))
                elif k == 2: imp.update(kind='memory', limits=limits(r))
                elif k == 3: imp.update(kind='global', valueType=r.byte(), mutable=r.byte())
                elif k == 4: imp.update(kind='tag', attribute=r.byte(), typeIndex=r.u())
                else: raise AssertionError('unknown import kind')
                imports.append(imp)
            r.done()
        elif row['id'] == 7:
            for _ in range(r.u()): exports.append(dict(name=r.string(), kind=r.byte(), index=r.u()))
            r.done()
        elif row['id'] == 0:
            names.append(r.string())
        elif row['id'] == 9 and len(data) < 1024:
            for _ in range(r.u()):
                flags = r.u(); assert flags == 0
                assert r.byte() == 0x41
                offset = r.signed(); assert r.byte() == 0x0b
                elements.append(dict(table=0, offset=offset, functionIndices=[r.u() for _ in range(r.u())]))
            r.done()
        elif row['id'] == 10 and len(data) < 1024:
            # Only finite generated indirect-call shims, never the engine or
            # adapter implementation. Retain logical operands, not raw code.
            for _ in range(r.u()):
                n = r.u(); end = r.p + n; assert r.u() == 0
                ops = []
                while r.p < end:
                    op = r.byte()
                    if op == 0x20: ops.append(dict(op='local.get', index=r.u()))
                    elif op == 0x41: ops.append(dict(op='i32.const', value=r.signed()))
                    elif op == 0x11: ops.append(dict(op='call_indirect', typeIndex=r.u(), table=r.u()))
                    elif op == 0x0b: ops.append(dict(op='end'))
                    else: raise AssertionError(('unknown finite generated shim instruction',op))
                assert r.p == end; shim_bodies.append(ops)
            r.done()
    return dict(componentSection=section, moduleSha256=sha(data), moduleBytes=len(data),
        sections=ss, imports=imports, exports=exports, customSections=names,
        elementSegments=elements, finiteGeneratedIndirectCallShims=shim_bodies)


def sort(r):
    k = r.byte()
    return (0, r.byte()) if k == 0 else (k,)


def external(r):
    s = sort(r)
    if s == (3,):
        bound = r.byte(); assert bound in (0, 1)
        return dict(sort=list(s), bound=bound, typeIndex=r.u() if bound == 0 else None)
    assert s in ((0, 17), (1,), (4,), (5,)), s
    return dict(sort=list(s), typeIndex=r.u())


def alias(r):
    s, k = sort(r), r.byte()
    if k in (0, 1): return dict(sort=list(s), kind=k, instance=r.u(), name=r.string())
    assert k == 2
    return dict(sort=list(s), kind=k, outer=r.u(), index=r.u())


def value(r): return r.signed()
def maybe_value(r):
    flag = r.byte(); assert flag in (0, 1)
    return value(r) if flag else None


def typedef(r):
    b = r.byte()
    if b == 0x40:
        params = [dict(name=r.string(), type=value(r)) for _ in range(r.u())]
        result = r.byte()
        if result == 0: returns = [value(r)]
        else: assert result == 1 and r.u() == 0; returns = []
        return dict(kind='function', params=params, results=returns)
    if b == 0x42:
        declarations = []
        for _ in range(r.u()):
            k = r.byte()
            if k == 1: declarations.append(dict(kind='type', type=typedef(r)))
            elif k == 2: declarations.append(dict(kind='alias', alias=alias(r)))
            elif k == 4: declarations.append(dict(kind='export', name=r.name(), type=external(r)))
            else: raise AssertionError(('unknown instance type declaration', k))
        return dict(kind='instance', declarations=declarations)
    if b == 0x72: return dict(kind='record', fields=[dict(name=r.string(), type=value(r)) for _ in range(r.u())])
    if b == 0x71:
        cases = []
        for _ in range(r.u()):
            cases.append(dict(name=r.string(), type=maybe_value(r))); assert r.byte() == 0
        return dict(kind='variant', cases=cases)
    if b == 0x70: return dict(kind='list', type=value(r))
    if b == 0x6f: return dict(kind='tuple', types=[value(r) for _ in range(r.u())])
    if b in (0x6e, 0x6d): return dict(kind='flags' if b == 0x6e else 'enum', names=[r.string() for _ in range(r.u())])
    if b == 0x6b: return dict(kind='option', type=value(r))
    if b == 0x6a: return dict(kind='result', ok=maybe_value(r), error=maybe_value(r))
    if b in (0x69, 0x68): return dict(kind='own' if b == 0x69 else 'borrow', typeIndex=r.u())
    if 0x73 <= b <= 0x7f: return dict(kind='primitive', byte=b)
    raise AssertionError(('unsupported actual type opcode', b))


def graph(path):
    data = Path(path).read_bytes(); ss = sections(data, COMPONENT)
    modules, types, instances, cfuncs, funcs, core_instances, aliases, canons, root_exports = [], [], [], [], [], [], [], [], []
    for section in ss:
        r = R(data[section['offset']:section['offset']+section['bytes']]); tag = section['id']
        if tag == 1:
            modules.append(core(r.b, section)); continue
        if tag == 7:
            for _ in range(r.u()): types.append(typedef(r))
        elif tag == 10:
            for _ in range(r.u()):
                name, t = r.name(), external(r)
                assert t['sort'] == [5]
                instances.append(dict(kind='import', name=name, typeIndex=t['typeIndex']))
        elif tag == 6:
            for _ in range(r.u()):
                a = alias(r); aliases.append(a); s = a['sort']
                if s == [3]: types.append(dict(kind='alias', alias=a))
                elif s == [1]: funcs.append(dict(kind='instance-export', instance=a['instance'], name=a['name']))
                elif s == [0, 0]: cfuncs.append(dict(kind='core-instance-export', instance=a['instance'], name=a['name']))
                elif s in ([0, 1], [0, 2], [0, 3]): pass
                else: raise AssertionError(('unsupported alias sort', s))
        elif tag == 2:
            for _ in range(r.u()):
                k = r.byte()
                if k == 0:
                    module = r.u(); args = []
                    for _ in range(r.u()):
                        name = r.string(); assert r.byte() == 0x12
                        args.append(dict(name=name, instance=r.u()))
                    core_instances.append(dict(kind='instantiate', module=module, arguments=args))
                else:
                    assert k == 1
                    exports = []
                    for _ in range(r.u()): exports.append(dict(name=r.string(), sort=r.byte(), index=r.u()))
                    core_instances.append(dict(kind='inline', exports=exports))
        elif tag == 8:
            for _ in range(r.u()):
                k = r.byte()
                if k in (0, 1):
                    assert r.byte() == 0
                    f = r.u(); opts = []
                    for _ in range(r.u()):
                        opt = r.byte(); opts.append(dict(kind=opt, index=r.u() if opt in (3, 4, 5, 7) else None))
                    c = dict(kind='lift' if k == 0 else 'lower', function=f, options=opts)
                    if k == 0: c['typeIndex'] = r.u(); funcs.append(c)
                    else: cfuncs.append(c)
                else:
                    assert k in (2, 3, 4)
                    c = dict(kind={2:'resource-new',3:'resource-drop',4:'resource-rep'}[k], typeIndex=r.u()); cfuncs.append(c)
                canons.append(c)
        elif tag == 11:
            for _ in range(r.u()):
                name, s, idx = r.name(), sort(r), r.u(); flag = r.byte(); assert flag in (0, 1)
                root_exports.append(dict(name=name, sort=list(s), index=idx, type=external(r) if flag else None))
                # Component exports introduce aliases into their sort's index space.
                if s == (1,): funcs.append(dict(kind='export-alias', targetIndex=idx))
        elif tag == 0: continue
        else: raise AssertionError(('unsupported actual component section', tag))
        r.done()
    roots = []
    for i in instances:
        t = types[i['typeIndex']]; assert t['kind'] == 'instance'
        members = [d for d in t['declarations'] if d['kind'] == 'export']
        roots.append(dict(i, functions=[d['name'] for d in members if d['type']['sort'] == [1]],
            types=[d['name'] for d in members if d['type']['sort'] == [3]], typeDefinition=t))
    connections = []
    for n, instance in enumerate(core_instances):
        if instance['kind'] != 'instantiate': continue
        mod = modules[instance['module']]
        for imp in mod['imports']:
            arg = next(a for a in instance['arguments'] if a['name'] == imp['module'])
            supplied = core_instances[arg['instance']]
            edge = dict(module=instance['module'], instance=n, importModule=imp['module'], importName=imp['name'], kind=imp['kind'], suppliedInstance=arg['instance'])
            if supplied['kind'] == 'inline':
                e = next(e for e in supplied['exports'] if e['name'] == imp['name'])
                edge['inlineExport'] = e
                if e['sort'] == 0:
                    cf = cfuncs[e['index']]; edge['coreFunctionOrigin'] = cf
                    if cf['kind'] == 'lower':
                        f = funcs[cf['function']]; edge['componentFunctionOrigin'] = f
                        if f['kind'] == 'instance-export': edge['rootImport'] = instances[f['instance']]['name']
            else: edge['suppliedModule'] = supplied['module']
            connections.append(edge)
    def resolve_func(cf, seen=()):
        if cf['kind'] == 'lower':
            f = funcs[cf['function']]
            assert f['kind'] == 'instance-export'
            return dict(kind='root-function', interface=instances[f['instance']]['name'], name=f['name'])
        if cf['kind'].startswith('resource-'):
            return dict(kind=cf['kind'], typeIndex=cf['typeIndex'])
        assert cf['kind'] == 'core-instance-export'
        key = (cf['instance'], cf['name']); assert key not in seen
        inst = core_instances[cf['instance']]; assert inst['kind'] == 'instantiate'
        m = modules[inst['module']]
        export = next(e for e in m['exports'] if e['name'] == cf['name'] and e['kind'] == 0)
        if not m['finiteGeneratedIndirectCallShims']:
            return dict(kind='core-module-export', module=inst['module'], instance=cf['instance'], name=cf['name'])
        body = m['finiteGeneratedIndirectCallShims'][export['index']]
        assert len([o for o in body if o['op']=='call_indirect']) == 1
        slot = next(o['value'] for o in body if o['op']=='i32.const')
        fixups = [(ix,x) for ix,x in enumerate(core_instances) if x['kind']=='instantiate' and modules[x['module']]['elementSegments']]
        assert len(fixups)==1
        ix, fixup = fixups[0]; segment=modules[fixup['module']]['elementSegments'][0]
        assert segment['offset']==0
        imported_function=segment['functionIndices'][slot]
        im=[x for x in modules[fixup['module']]['imports']if x['kind']=='function'][imported_function]
        edge=next(e for e in connections if e['instance']==ix and e['importModule']==im['module'] and e['importName']==im['name'])
        return dict(kind='generated-table-shim', shimModule=inst['module'], shimExport=cf['name'], tableSlot=slot,
            fixupModule=fixup['module'], target=resolve_func(edge['coreFunctionOrigin'],seen+(key,)))
    for edge in connections:
        if 'coreFunctionOrigin' in edge: edge['resolvedFunctionOrigin']=resolve_func(edge['coreFunctionOrigin'])
    return dict(schemaVersion=1, component=dict(path=str(path), sha256=sha(data), bytes=len(data)),
        componentSections=ss, modules=modules, rootImports=roots, componentFunctions=funcs,
        componentTypes=types, coreFunctions=cfuncs, coreInstances=core_instances, aliases=aliases, canonicalDefinitions=canons,
        importBindings=connections, exports=root_exports,
        engineAndAdapterCodeAndAllDataPayloadsNotDecoded=True, finiteGeneratedShimInstructionsOnly=True,
        noCompilationOrInstantiation=True)


if __name__ == '__main__':
    out = {}
    for fixture in ['pure', 'resource']:
        path = Path('/private/tmp/starling-node-compat/scheduler-resource-component-v1-' + fixture + '/worker/component.wasm')
        out[fixture] = graph(path)
    (OWN / 'binary-import-graph.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k:dict(modules=len(v['modules']), rootImports=[dict(name=i['name'], functions=i['functions'], types=i['types']) for i in v['rootImports']], coreImports=[dict(index=n, imports=m['imports']) for n,m in enumerate(v['modules'])]) for k,v in out.items()}))
