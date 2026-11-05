"""Independent static/Data audit only; no Root helper import or adapter transform."""
from pathlib import Path
import ast,hashlib,io,itertools,json,re,tarfile
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
S=HERE.parent
BASE=Path('/private/tmp/starling-node-compat/import-abi-clock-v2-build/source')
REG=Path('/Users/dan/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f')
seen={};checks=0


def need(ok,message='check'):
    global checks
    checks+=1
    assert ok,message


def raw(path):
    p=Path(path);need(p.is_file()and not p.is_symlink(),str(p));a=p.stat();value=p.read_bytes();z=p.stat()
    identity=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(identity(a)==identity(z))
    row=dict(path=str(p),sha256=hashlib.sha256(value).hexdigest(),bytes=len(value))
    if str(p)in seen:need(seen[str(p)]==(row,identity(z)))
    seen[str(p)]=(row,identity(z));return value


def load(path):return json.loads(raw(path))


def u32(data,pos):
    value=0
    for shift in range(0,35,7):
        need(pos<len(data));byte=data[pos];pos+=1;value|=(byte&127)<<shift
        if byte<128:need(value<=0xffffffff);return value,pos
    raise AssertionError('bounded u32')


def name(data,pos):
    size,pos=u32(data,pos);need(pos+size<=len(data));return data[pos:pos+size].decode('utf-8'),pos+size


def core_metadata(data):
    need(data[:8]==b'\0asm\1\0\0\0');pos=8;sections=[];imports=[];exports=[];types=[]
    while pos<len(data):
        sid=data[pos];size,start=u32(data,pos+1);end=start+size;need(end<=len(data));payload=data[start:end]
        section=dict(id=sid,bytes=size,sha256=hashlib.sha256(payload).hexdigest())
        if sid==0:section['name']=name(payload,0)[0]
        if sid==1:
            count,q=u32(payload,0)
            for _ in range(count):
                need(payload[q]==0x60);q+=1;argc,q=u32(payload,q);params=list(payload[q:q+argc]);q+=argc;retc,q=u32(payload,q);results=list(payload[q:q+retc]);q+=retc
                need(all(t in[0x7f,0x7e,0x7d,0x7c,0x70,0x6f]for t in params+results));types.append(dict(params=params,results=results))
            need(q==len(payload))
        if sid==2:
            count,q=u32(payload,0);function=0
            for entry in range(count):
                module,q=name(payload,q);field,q=name(payload,q);kind=payload[q];q+=1
                row=dict(importIndex=entry,module=module,name=field,kind=kind)
                if kind==0:
                    ty,q=u32(payload,q);need(ty<len(types));row.update(functionIndex=function,typeIndex=ty);function+=1
                elif kind==2:
                    flags,q=u32(payload,q);minimum,q=u32(payload,q);need(flags==0);row['limits']=dict(flags=flags,min=minimum)
                else:raise AssertionError('only pinned function/memory import layout')
                imports.append(row)
            need(q==len(payload))
        if sid==7:
            count,q=u32(payload,0)
            for _ in range(count):
                field,q=name(payload,q);kind=payload[q];q+=1;index,q=u32(payload,q);exports.append(dict(name=field,kind=kind,index=index))
            need(q==len(payload))
        sections.append(section);pos=end
    need(pos==len(data));return dict(sections=sections,imports=imports,exports=exports,types=types)


def function(text,name):
    start=re.search(r'(?m)^fn '+re.escape(name)+r'\b',text).start();following=re.search(r'(?m)^(?:pub )?fn ',text[start+1:])
    return text[start:start+1+following.start()]if following else text[start:]


def calls(text):return re.findall(r'stub_wasi_imports\(\s*module,\s*"([^"]+)",\s*"([^"]+)"',text)


def apply_diff(source,patch,reverse=False):
    old=source.splitlines(keepends=True);lines=patch.splitlines(keepends=True);out=[];cursor=0;i=0
    while i<len(lines):
        match=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i])
        if not match:i+=1;continue
        start=int(match[3]if reverse else match[1])-1;need(start>=cursor);out.extend(old[cursor:start]);cursor=start;i+=1
        while i<len(lines)and not lines[i].startswith('@@'):
            line=lines[i];i+=1
            if line.startswith(('---','+++')):continue
            sign=line[:1];text=line[1:]
            if reverse:sign={'+':'-','-':'+',' ':' '}.get(sign,sign)
            need(sign in[' ','+','-'])
            if sign in[' ','-']:need(old[cursor]==text);cursor+=1
            if sign in[' ','+']:out.append(text)
    out.extend(old[cursor:]);return ''.join(out)


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    need(not(HERE/'index.json').exists())
    drafts=[S/'clock-adapter-provenance-v1',S/'clock-io-pruning-candidate-v1']
    for folder in drafts:
        for p in sorted(folder.rglob('*')):
            if p.is_file():raw(p)
    meta=load(drafts[0]/'metadata.json');derivation=load(drafts[1]/'source-derivation.json')
    adapter=REPO/meta['repository']['path']if not Path(meta['repository']['path']).is_absolute()else Path(meta['repository']['path'])
    data=raw(adapter);need(len(data)==53512 and hashlib.sha256(data).hexdigest()=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0')
    decoded=core_metadata(data);need(decoded['sections']==meta['repository']['sections']and decoded['imports']==meta['repository']['imports'])
    upstream=load(drafts[0]/'section-comparison.json');other=raw(upstream['downloadPath']);other_meta=core_metadata(other)
    need(hashlib.sha256(other).hexdigest()==upstream['downloadSha256']and len(other)==upstream['downloadBytes']and data!=other)
    for a,b,claim in zip(decoded['sections'],other_meta['sections'],upstream['sections']):need((a['sha256']==b['sha256'])==claim['equal'])
    need(len(decoded['sections'])==len(other_meta['sections'])==len(upstream['sections']))
    need(meta['exactSourceRevisionEstablished']is meta['codeInstructionsDecoded']is meta['moduleCompiledOrExecuted']is meta['adapterRewriteAdmission']is False)
    need(decoded['imports'][0]==dict(importIndex=0,module='env',name='memory',kind=2,limits=dict(flags=0,min=0)))
    funcs=[r for r in decoded['imports']if r['kind']==0];need(len(funcs)==63 and all(r['importIndex']==r['functionIndex']+1 for r in funcs))
    before=raw(derivation['baselinePath']).decode();after=raw(drafts[1]/derivation['afterPath']).decode();patch=raw(drafts[1]/'io-policy.patch').decode()
    need(hashlib.sha256(before.encode()).hexdigest()==derivation['baselineSha256']and len(before.encode())==derivation['baselineBytes'])
    need(hashlib.sha256(after.encode()).hexdigest()==derivation['afterSha256']and len(after.encode())==derivation['afterBytes'])
    patches={chunk.splitlines()[0][6:]:chunk for chunk in re.split(r'(?m)(?=^--- a/)',patch)if chunk.startswith('--- a/')}
    stub_patch=patches['crates/spidermonkey-embedding-splicer/src/stub_wasi.rs']
    need(apply_diff(before,stub_patch)==after and apply_diff(after,stub_patch,True)==before)
    if 'cliAfter'in derivation:
        cli_before=raw(derivation['cliBaseline']['path']).decode();cli_after=raw(drafts[1]/derivation['cliAfter']['path']).decode();cli_patch=patches['crates/spidermonkey-embedding-splicer/src/bin/splicer.rs']
        need(hashlib.sha256(cli_before.encode()).hexdigest()==derivation['cliBaseline']['sha256']and hashlib.sha256(cli_after.encode()).hexdigest()==derivation['cliAfter']['sha256'])
        need(apply_diff(cli_before,cli_patch)==cli_after and apply_diff(cli_after,cli_patch,True)==cli_before)
    original=calls(function(before,'stub_io'));poll=calls(function(after,'stub_io_poll'));streams=calls(function(after,'stub_io_streams'))
    need(len(original)==23 and len(poll)==4 and len(streams)==19 and sorted(original)==sorted(poll+streams)and len(set(poll+streams))==23)
    need(all(module=='wasi:io/poll'for module,_ in poll)and all(module in['wasi:io/error','wasi:io/streams']for module,_ in streams))
    policy=function(after,'io_requirements');target=function(after,'target_world_requires_io');target_names=set(re.findall(r'"(wasi:[^"]+)"',target))
    names=set(re.findall(r'"(wasi:[^"]+)"',policy));stream_names=names-{'wasi:io/poll@0.2'};need(len(target_names)==14 and len(stream_names)==5)
    need('features.contains(&Feature::Clocks)'in policy and 'let poll = streams'in policy and 'features.contains(&Feature::FetchEvent)'in policy)
    model_cases=[]
    for enabled in itertools.product([False,True],repeat=5):
        features={f for f,on in zip(['Clocks','Stdio','Http','FetchEvent','Random'],enabled)if on}
        for world in[set()]+[{n}for n in sorted(target_names|names)]:
            stream=bool(features&{'Stdio','Http','FetchEvent'}or world&(target_names|stream_names));p=stream or 'Clocks'in features or 'wasi:io/poll@0.2'in world
            need(not stream or p)
            if features=={'Clocks'}and not world:need(p and not stream)
            if not features and world=={'wasi:io/poll@0.2'}:need(p and not stream)
            model_cases.append(dict(features=sorted(features),worldImports=sorted(world),poll=p,streams=stream))
    # Synthetic kind-list theorem only: no actual adapter byte transformation.
    synthetic=['memory']+['func']*63;rotated=synthetic[1:]+synthetic[:1]
    need([x for x in synthetic if x=='func']==[x for x in rotated if x=='func']and [x for x in synthetic if x=='memory']==[x for x in rotated if x=='memory'])
    need(all(entry==function for function,entry in enumerate(i for i,k in enumerate(rotated)if k=='func')))
    wirm=REG/'wirm-5.0.0';crate=raw(REG.parents[1]/'cache'/REG.name/'wirm-5.0.0.crate');need(hashlib.sha256(crate).hexdigest()=='8da24f7393e7008c1b2102f4d69340d388a6687a0e687a77fedaa440dbec1286')
    archive=tarfile.open(fileobj=io.BytesIO(crate),mode='r:gz')
    texts={}
    for relative in['src/ir/function.rs','src/ir/module/module_imports.rs','src/ir/module/module_functions.rs','src/ir/module/mod.rs']:
        value=raw(wirm/relative);member=archive.getmember('wirm-5.0.0/'+relative);need(member.isfile()and archive.extractfile(member).read()==value);texts[relative]=value.decode()
    archive.close()
    need('Some(ImportsID(id as u32))'in texts['src/ir/module/module_imports.rs'])
    need('FunctionID(imp_fn_id)'in texts['src/ir/module/mod.rs']and 'imp_fn_id += 1'in texts['src/ir/module/mod.rs'])
    need('FunctionID(*import_id)'in texts['src/ir/function.rs']and 'self.functions.is_local(FunctionID(*import_id))'in texts['src/ir/module/mod.rs'])
    component=raw(BASE/'src/componentize.js').decode();lock=raw(BASE/'Cargo.lock').decode();raw(BASE/'Cargo.toml');raw(BASE/'crates/spidermonkey-embedding-splicer/wit/spidermonkey-embedding-splicer.wit')
    need('name = "wirm"\nversion = "5.0.0"'in lock and 'name = "wit-parser"\nversion = "0.258.0"'in lock)
    need('const finalBin = splicer.stubWasi('in component and 'wasi_snapshot_preview1: await readFile(preview2Adapter)'in component)
    raw(REG/'wit-parser-0.258.0/src/resolve/mod.rs');raw(REG/'wit-parser-0.258.0/src/lib.rs')
    exported={r['name']for r in decoded['exports']if r['kind']==0};imported={(r['module'],r['name'])for r in funcs}
    need('cabi_realloc'not in exported and ('__main_module__','cabi_realloc')in imported and ('wasi:random/random@0.2.0','get-random-u64')not in imported)
    actual_poll=[r for r in funcs if(r['module'].split('@')[0],r['name'])in poll];actual_stream=[r for r in funcs if(r['module'].split('@')[0],r['name'])in streams]
    stdio=[r for r in funcs if r['module']in['wasi:cli/stdin@0.2.0','wasi:cli/stdout@0.2.0','wasi:cli/stderr@0.2.0']]
    clocks=[r for r in funcs if r['module'].startswith('wasi:clocks/')];need(len(stdio)==3 and len(clocks)==6 and len(actual_poll)==2 and len(actual_stream)==11)
    need(not any(r['module']=='wasi_snapshot_preview1'for r in funcs))
    normalize=raw(drafts[1]/'normalize-adapter.py').decode();ast.parse(normalize)
    own=REPO/'tests/node-compat/foundation-crypto/ownership-secret-verifier-controller-candidate-v1';index=load(own/'index.json');need(hashlib.sha256(raw(own/'index.json')).hexdigest()=='0fc0082da7d9842bf9bd9e46a28760e2cea5f698eec62880f0150c572d94a78f')
    for row in index['files']:need(hashlib.sha256(raw(own/row['path'])).hexdigest()==row['sha256'])
    for path in list(seen):raw(path)
    write('observations.json',dict(schemaVersion=1,state='CLOCK_IO_PRUNING_STATIC_DESIGN_OBSERVATIONS_NOT_APPROVAL_V1',checks=checks,inputs=len(seen),adapter=seen[str(adapter)][0],metadataOnlyDecoded=True,instructionsDecoded=False,adapterTransformed=False,customHelpersImported=False,buildOrNodeOrWizerOrGuestOrComponentActions=False,
        exactRepositoryAdapterSourceRevisionEstablished=False,adapterFunctionImports=63,adapterMemoryImports=1,allFunctionEntryIdsDifferByOne=True,adapterExports=decoded['exports'],adapterTypes=decoded['types'],randomDisabledPrerequisitesSatisfied=False,draftSourceDerivation=seen[str(drafts[1]/'source-derivation.json')][0],candidateExactSourceVerdictIssued=False,
        exactForwardReversePatch=True,ioStubCalls=dict(original=23,poll=4,streamsAndError=19),actualAdapterMatchedCalls=dict(poll=len(actual_poll),streamsAndError=len(actual_stream),stdio=len(stdio),narrowEntryTotal=14),actualAdapterClockImports=clocks,actualAdapterPollImports=actual_poll,actualAdapterStreamErrorImports=actual_stream,actualAdapterStdioImports=stdio,preview1StdioStubAttemptsAreNoOpsForExactAdapter=True,expectedUnexecutedPostPruneInventory=dict(functionImports=49,memoryImports=1,totalImports=50),
        wirmVersion='5.0.0',wirmSelectedSourceChecksumVerified=True,syntheticKindSpaceRotationOnly=True,policyModelCases=len(model_cases),policyModelScope='Independent Boolean translation with names extracted from Rust source, not Rust execution or WIT Resolve validation',originalCaller0fcUnchanged=True,
        sourceApprovalIssued=False,rootAuthority=None,normalizationAuthority=None,buildAuthority=None,componentAuthority=None,runtimeAuthority=None))
    write('pure-policy-cases.json',dict(schemaVersion=1,scope='Independent Boolean model of exact proposed source formula only; no Rust/helper execution',cases=model_cases))
    write('input-hashes.json',dict(schemaVersion=1,files=[row for row,_ in seen.values()],initialFinalIdentityAndHashesVerified=True))
    print(json.dumps(dict(checks=checks,inputs=len(seen),policyModelCases=len(model_cases),actualAdapterMatchedPoll=len(actual_poll),actualAdapterMatchedStreamError=len(actual_stream),adapterTransformed=False,sourceApprovalIssued=False)))


if __name__=='__main__':main()
