"""Dormant retained-DATA primitives. No API, Node, generated module or host execution."""
from pathlib import Path
import hashlib,json,os,stat

def descriptor(path):
    path=Path(path);raw=path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))

def checked(row):
    assert type(row)is dict and set(row)=={'path','sha256','bytes'}
    assert type(row['bytes'])is int and row['bytes']>=0
    path=Path('/private'+row['path'])if row['path'].startswith('/tmp/')else Path(row['path'])
    assert path.is_absolute()and str(path)==os.path.normpath(str(path))
    for p in(path,*path.parents):assert not p.is_symlink()
    before=path.stat();assert stat.S_ISREG(before.st_mode)and before.st_size==row['bytes']
    digest=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(4194304),b''):digest.update(block)
    after=path.stat()
    assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
    assert digest.hexdigest()==row['sha256']
    return path

def data(row):return json.loads(checked(row).read_bytes())

def confined_publication(root,relative):
    assert type(relative)is dict and set(relative)=={'path','sha256','bytes'}
    name=relative['path'];assert not name.startswith('/')and all(p not in('','.','..')for p in name.split('/'))
    row=dict(relative,path=str(Path(root)/name));checked(row)
    return row

def parse_wave(raw):
    text=raw.decode('utf8');assert text.endswith('\n')and not text.endswith('\n\n')
    text=text[:-1];assert text.startswith('"')and text.endswith('"')
    value=[];at=1
    while at<len(text)-1:
        c=text[at];at+=1
        if c=='\\':
            assert at<len(text)-1
            escaped=text[at];at+=1
            if escaped=='u':
                assert text[at]=='{';end=text.index('}',at+1);digits=text[at+1:end]
                assert 1<=len(digits)<=6 and all(v in'0123456789abcdefABCDEF'for v in digits)
                cp=int(digits,16);assert cp<=0x10ffff and not 0xd800<=cp<=0xdfff
                value.append(chr(cp));at=end+1
            else:value.append({'\\':'\\','"':'"',"'":"'",'n':'\n','r':'\r','t':'\t'}[escaped])
        else:
            assert c!='"'and not(ord(c)<32 or 127<=ord(c)<=159)
            value.append(c)
    value=''.join(value);assert len(value)<=2097152
    return value

def check_inner_terminal(value):
    assert value['closed']is value['ownedGroupGone']is value['terminalExitZeroObserved']is True and value['status']==0
    assert value['signal']is value['spawnError']is value['externalSignal']is None
    assert value['timedOut']is value['outputLimitExceeded']is False
    assert value['errors']==value['signals']==[]and value['signalCount']==0

def check_outer_terminal(value,root_authority):
    assert value['authority']==root_authority and value['rawExitCode']==0
    assert value['parentOwnedGroupGone']is value['allObservedOwnedGroupsGone']is True
    assert value['timeout']is value['forcedCleanup']is False
    assert value['remainingObservedPids']==value['errors']==value['signals']==value['interruptedSignals']==[]
    assert value['finalGroups']and all(g['alive']is False for g in value['finalGroups'])

def scalar(value,oracle):
    assert type(value)is str and value==oracle
    result=json.loads(value)
    assert list(result)==['library','html','bytes']and result['library']=='react-dom/server.edge'
    assert result['html']=='<p id="wasm-ssr">Hello from real ReactDOM</p>'and result['bytes']==len(result['html'].encode('utf8'))==45

if __name__=='__main__':
    raise SystemExit('Dormant DATA primitives only. Actual terminal/Root descriptors must be explicitly supplied before an actual review.')
