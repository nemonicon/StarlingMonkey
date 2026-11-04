"""Owned read-only binary/glue and retained-host-output inspection; no execution."""
from pathlib import Path
import base64,hashlib,json,re
from binary_reader import sections,core_imports

def digest(data):return hashlib.sha256(data).hexdigest()

def review_core_glue(root,components):
    results=[]
    for component in components:
        path=Path(component['path']);data=path.read_bytes();assert digest(data)==component['sha256']
        cores=[part for kind,part in sections(data,bytes.fromhex('0061736d0d000100')) if kind==1]
        assert cores
        main_sha=digest(cores[0]);found=[]
        for candidate in path.parent.glob('*.wasm'):
            if candidate.name.endswith('.component.wasm'):continue
            raw=candidate.read_bytes()
            if digest(raw)!=main_sha:continue
            assert raw==cores[0]
            for glue in path.parent.glob('*.js'):
                text=glue.read_text()
                if "new URL('./"+candidate.name+"', import.meta.url)" not in text:continue
                inline=[base64.b64decode(x+'='*((-len(x))%4)) for x in re.findall(r"base64Compile\('([^']+)'\)",text)]
                assert inline==cores[1:]
                found.append({'corePath':str(candidate),'coreSha256':main_sha,'coreBytes':len(raw),'gluePath':str(glue),'glueSha256':digest(glue.read_bytes()),'inlineAdapters':[{'sha256':digest(x),'bytes':len(x)} for x in inline]})
        assert found,(str(path),'Missing matching emitted core and glue')
        wasi=sorted({x['module'] for core in cores for x in core_imports(core) if x['module'].startswith('wasi:')})
        assert wasi in [[],['wasi:random/random@0.2.10']]
        assert not any(x['module']=='wasi_snapshot_preview1' for core in cores for x in core_imports(core))
        results.append({'componentPath':str(path),'exactMainCoreAndInlineAdapters':True,'matches':found,'embeddedCoreCount':len(cores),'coreWasiModules':wasi,'preview1Imported':False})
    return results

def cli_string(source):
    source=source.strip();out=[];i=0
    while i<len(source):
        char=source[i];i+=1
        if char!='\\':out.append(char);continue
        assert i<len(source);next_char=source[i];i+=1
        if next_char=='u' and i<len(source) and source[i]=='{':
            end=source.index('}',i+1);digits=source[i+1:end];assert re.fullmatch('[0-9a-fA-F]+',digits)
            out.append(json.dumps(chr(int(digits,16)),ensure_ascii=False)[1:-1]);i=end+1
        elif next_char=="'":out.append("'")
        else:out.append('\\u0000' if next_char=='0' else '\\'+next_char)
    return json.loads(''.join(out))

def raw_host_inventory(reports):
    rows=[]
    def visit(label,value,trail=()):
        if isinstance(value,list):
            for n,item in enumerate(value):visit(label,item,trail+(n,))
        elif isinstance(value,dict):
            key=str(trail[-1]).lower() if trail else ''
            if ('wasmtime' in key or key in ['freshhost','host']) and any(k in value for k in ['stdout','stdoutSha256','observed','status']):
                raw=value.get('stdout');item={'report':label,'jsonPath':list(trail),'rawStdoutAvailable':isinstance(raw,str),'stdoutDigestAvailable':isinstance(value.get('stdoutSha256'),str),'parsedObservationAvailable':'observed'in value,'independentlyDecoded':False,'status':value.get('status')}
                if isinstance(raw,str):
                    item['rawStdoutSha256']=digest(raw.encode())
                    if 'stdoutSha256'in value:assert value['stdoutSha256']==item['rawStdoutSha256']
                    if 'stdoutBytes'in value:assert value['stdoutBytes']==len(raw.encode())
                    if raw.strip() and 'observed'in value:
                        decoded=cli_string(raw)
                        if isinstance(decoded,str):decoded=json.loads(decoded)
                        assert decoded==value['observed'],(label,trail)
                        item['independentlyDecoded']=True
                rows.append(item)
            for key,item in value.items():
                if key in ['engineMetadata','engineReceipt','metadata','receipt','pin','componentizerProvenance','componentizer']:continue
                if key=='wasmtimeReport':
                    rows.append({'report':label,'jsonPath':list(trail+(key,)),'rawStdoutAvailable':False,'stdoutDigestAvailable':False,'parsedObservationAvailable':True,'independentlyDecoded':False})
                visit(label,item,trail+(key,))
    for label,report in reports.items():visit(label,report)
    return {'records':rows,'rawStdoutRecords':sum(r['rawStdoutAvailable'] for r in rows),'independentlyDecodedRecords':sum(r['independentlyDecoded'] for r in rows),'missingRawStdoutRecords':sum(not r['rawStdoutAvailable'] for r in rows),'scope':'No absent stdout is reconstructed, invented or borrowed from another gate. Parsed-only or digest-only observations remain recorded evidence rather than independent raw decoding.'}
