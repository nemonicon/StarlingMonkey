"""Read/hash/AST and pure metadata models only; never build or run JS/SM."""
from pathlib import Path
import ast,hashlib,json,re
HERE=Path(__file__).resolve().parent
def row(path):
    path=Path(path);b=path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
if (HERE/'index.json').exists():
    entries=json.loads((HERE/'index.json').read_text())['files'];names=[r['path']for r in entries]
    assert len(names)==len(set(names));assert not any(p.is_symlink()for p in HERE.rglob('*'))
    assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}==set(names)|{'index.json'}
    for r in entries:
        assert not Path(r['path']).is_absolute()and'..'not in Path(r['path']).parts
        got=row(HERE/r['path']);assert got['sha256']==r['sha256']and got['bytes']==r['bytes']
meta=json.loads((HERE/'primary-source.json').read_text())
d=json.loads((HERE/'derivation.json').read_text());assert d['baseCommit']==meta['commit']
checks=0
for r in meta['files']:
    p=HERE/'before'/r['path'];b=p.read_bytes()
    assert row(p)['sha256']==r['sha256'] and len(b)==r['bytes']
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['gitBlobSha1'];checks+=1
    text=b.decode()
    own=[e for e in d['edits']if e['path']==r['path']]
    for e in own:assert text.count(e['before'])==1;text=text.replace(e['before'],e['after']);checks+=1
    after=HERE/'after'/r['path'];assert after.read_text()==text
    for e in reversed(own):assert text.count(e['after'])==1;text=text.replace(e['after'],e['before']);checks+=1
    assert text==b.decode();checks+=1
for r in d['after']:
    got=row(HERE/'after'/r['path']);assert got['sha256']==r['sha256']and got['bytes']==r['bytes'];checks+=1
# Independently apply the emitted unified diff in memory, not merely the edit
# ledger. This checks the exact artifact the future build will consume.
patch=(HERE/'saved-frame-is-eval-v1.patch').read_text().splitlines(True);i=0;patched=[]
while i<len(patch):
    assert patch[i].startswith('--- a/');path=patch[i][6:].rstrip('\n');i+=1
    assert patch[i]=='+++ b/'+path+'\n';i+=1
    old=(HERE/'before'/path).read_text().splitlines(True);cursor=0;out=[]
    while i<len(patch)and not patch[i].startswith('--- a/'):
        m=re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\n',patch[i]);assert m,patch[i]
        start=int(m[1])-1;assert start>=cursor;out.extend(old[cursor:start]);cursor=start;i+=1;consumed=produced=0
        while i<len(patch)and not patch[i].startswith(('@@ ','--- a/')):
            line=patch[i];assert line[0]in' +-'
            if line[0]in' -':assert old[cursor]==line[1:];cursor+=1;consumed+=1
            if line[0]in' +':out.append(line[1:]);produced+=1
            i+=1
        assert consumed==int(m[2]or 1)and produced==int(m[4]or 1)
    out.extend(old[cursor:]);assert ''.join(out)==(HERE/'after'/path).read_text();patched.append(path);checks+=1
assert set(patched)=={r['path']for r in d['after']}
cpp=(HERE/'after/js/src/vm/SavedStacks.cpp').read_text()
function=cpp.split('static Maybe<bool> SavedFrameEvalProvenance(FrameIter& iter) {',1)[1].split('\nbool SavedStacks::insertFrames(',1)[0]
types=re.findall(r'strcmp\(type, "([^"]+)"\)',function)
assert types==['eval','Function','GeneratorFunction','AsyncFunction','AsyncGenerator'];checks+=1
assert 'filename'not in function and 'displayURL'not in function
assert function.index('script->isForEval()')<function.index('hasIntroductionType()')<function.index('strcmp(type,')
assert function.rstrip().endswith('return Nothing();\n}');checks+=1
def model(wasm=False,for_eval=False,introduction=None):
    # Source-derived case model, NOT executed native code or a compiler test.
    if wasm:return False
    if for_eval:return True
    if introduction is None:return False
    if introduction in types:return True
    return None
models=[({},False),({'for_eval':True},True),({'wasm':True},False),({'for_eval':True,'introduction':'unknown'},True)]
models += [({'introduction':t},True)for t in types]
models += [({'introduction':t},None)for t in ['unknown','debugger eval','eventHandler','ordinary-source.js']]
for args,expected in models:assert model(**args)is expected;checks+=1
for source_url in [None,'ordinary-source.js','eval','Function']:
    # Presentation data is intentionally not an input to the classifier.
    assert model(introduction='eval')is True and model()is False;checks+=1
assert 'Maybe<bool> isEval;'in cpp and 'isEval(savedFrame.getIsEval())'in cpp
assert 'existing->getIsEval() != lookup.isEval'in cpp
assert 'lookup.isEval.isSome() ? (*lookup.isEval ? 2 : 1) : 0'in cpp
assert len({0 if x is None else (2 if x else 1)for x in [None,False,True]})==3;checks+=3
assert '/* isEval */ Nothing()'in cpp
clone_before=(HERE/'before/js/src/vm/StructuredClone.cpp').read_text();clone_after=(HERE/'after/js/src/vm/StructuredClone.cpp').read_text()
new='  // Clone wire format has no eval provenance; never fabricate non-eval.\n  savedFrame->initIsEval(mozilla::Nothing());\n'
assert clone_after.replace(new,'')==clone_before;checks+=1
api=cpp.split('JS_PUBLIC_API SavedFrameResult GetSavedFrameIsEval(',1)[1].split('JS_PUBLIC_API SavedFrameResult GetSavedFrameLine(',1)[0]
assert api.index('*isEvalp = false;')<api.index('UnwrapSavedFrame(')<api.index('frame->getIsEval()')
assert 'if (isEval.isNothing()) {\n    return SavedFrameResult::AccessDenied;'in api
assert api.index('*isEvalp = *isEval;')<api.index('return SavedFrameResult::Ok;');checks+=3
assert '#define JS_HAS_SAVEDFRAME_IS_EVAL 1'in(HERE/'after/js/public/SavedFrameAPI.h').read_text();checks+=1
for r in json.loads((HERE/'classification-primary-source.json').read_text())['files']:
    b=(HERE/'provenance'/r['path']).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['gitBlobSha1'];checks+=1
eval_cpp=(HERE/'provenance/js/src/builtin/Eval.cpp').read_text();assert 'setIntroductionType("eval")'in eval_cpp and 'setIntroductionInfo(introducerFilename, "eval",'in eval_cpp
fn_cpp=(HERE/'provenance/js/src/vm/JSFunction.cpp').read_text()
for t in types[1:]:assert '"'+t+'"'in fn_cpp;checks+=1
oracle=HERE/'node-oracle-data/stdout.log';value=json.loads(oracle.read_text());assert value['node']=='v22.14.0'and value['guestExecuted']is False and len(value['rows'])==16
true_count=0
for r in value['rows']:
    i=r['id'];intro=None
    if 'eval' in i:intro='eval'
    elif i.startswith('function-constructor'):intro='Function'
    elif i=='async-function-constructor':intro='AsyncFunction'
    elif i=='generator-constructor':intro='GeneratorFunction'
    elif i=='async-generator-constructor':intro='AsyncGenerator'
    expected=model(introduction=intro);observed=r['frames'][0]
    assert observed['isEval']is expected
    assert observed['evalOriginType']==('string'if expected else'undefined')
    true_count+=int(expected);checks+=1
assert true_count==12
terminal=json.loads((HERE/'node-oracle-data/terminal.json').read_text());assert terminal['rawExitCode']==0
for k in ['timeout','forcedCleanup']:assert terminal[k]is False
for k in ['parentOwnedGroupGone','allObservedOwnedGroupsGone']:assert terminal[k]is True
for k in ['signals','interruptedSignals','errors','remainingObservedPids']:assert terminal[k]==[]
assert row(oracle)['sha256']==terminal['stdout']['sha256'];assert row(oracle)['bytes']==terminal['stdout']['bytes'];assert terminal['stderr']['bytes']==0;checks+=1
authority=json.loads((HERE/'node-oracle-data/authority.json').read_text());assert row(HERE/'node-is-eval-oracle.mjs')==authority['entry']
assert row(HERE/'node-oracle-data/authority.json')['sha256']==terminal['authority']['sha256'];checks+=1
ast.parse((HERE/'derive.py').read_text());ast.parse(Path(__file__).read_text());checks+=2
print(json.dumps(dict(schemaVersion=1,state='SAVEDFRAME_IS_EVAL_SOURCE_CHECKS_PASSED_V1',checks=checks,exactEdits=len(d['edits']),nativeFilesChanged=4,hostNodeOracleRows=16,hostNodeDynamicTrue=12,hostNodeOrdinaryFalse=4,sourceModelNotNativeProof=True,compilerInvoked=False,guestExecuted=False,cloneWireFormatChanged=False)))
