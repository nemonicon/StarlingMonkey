"""Inert real-context intake and tiny stdlib-only guards; no Git/build/tool run."""
from pathlib import Path
import ast,importlib.util,json,re,tempfile
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('actual_intl_driver_source_checks',HERE/'build.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
names=[]
def passed(name):names.append(name)
def rejects(name,callback):
    try:callback()
    except (AssertionError,UnicodeError):passed(name)
    else:raise AssertionError(name+' was accepted')
assert m.saved_frame_eval_requested({})is False;passed('default unpatched')
assert m.saved_frame_eval_requested({'SM_SAVED_FRAME_EVAL':'0'})is False;passed('explicit unpatched')
assert m.saved_frame_eval_requested({'SM_SAVED_FRAME_EVAL':'1'})is True;passed('explicit patch opt in')
for v in ['',None,True,'true','2']:
    rejects('reject nonliteral selection '+repr(v),lambda v=v:m.saved_frame_eval_requested({'SM_SAVED_FRAME_EVAL':v}))
data=m.authenticate_patch_family();assert data['payloadFiles']==27;passed('actual27member sealed family in genuine driver context')
assert data['patch']['sha256']==m.PATCH_SHA;passed('actual sealed patch digest')
with tempfile.TemporaryDirectory(prefix='intl-patch-guards-')as td:
    root=Path(td)/'fresh-source';root.mkdir()
    for r in data['before']:
        p=root/r['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((m.REPO/m.PATCH_FAMILY/'before'/r['path']).read_bytes())
    assert len(m.assert_patch_source_bytes(root,data,False))==4;passed('four actual preimages pass')
    selected=root/m.PATCH_FILES[0];original=selected.read_bytes();selected.write_bytes(b'wrong'+original)
    rejects('preimage byte mismatch',lambda:m.assert_patch_source_bytes(root,data,False));selected.write_bytes(original)
    rejects('before bytes cannot masquerade as after',lambda:m.assert_patch_source_bytes(root,data,True))
    target=Path(td)/'physical-same-bytes';selected.rename(target);selected.symlink_to(target)
    rejects('leaf alias with correct bytes',lambda:m.assert_patch_source_bytes(root,data,False));selected.unlink();target.rename(selected)
    actual_parent=Path(td)/'physical-parent';selected.parent.rename(actual_parent);selected.parent.symlink_to(actual_parent,target_is_directory=True)
    rejects('parent alias with correct bytes',lambda:m.assert_patch_source_bytes(root,data,False));selected.parent.unlink();actual_parent.rename(selected.parent)
    for r in data['after']:
        (root/r['path']).write_bytes((m.REPO/m.PATCH_FAMILY/'after'/r['path']).read_bytes())
    assert len(m.assert_patch_source_bytes(root,data,True))==4;passed('four actual afterimages pass')
    rejects('after bytes cannot masquerade as base',lambda:m.assert_patch_source_bytes(root,data,False))
    selected.write_bytes(selected.read_bytes()+b'\n')
    rejects('postbuild source byte change',lambda:m.assert_patch_source_bytes(root,data,True))
good=('\0'.join(m.PATCH_FILES)+'\0').encode();assert set(m.assert_patch_diff_names(good))==set(m.PATCH_FILES);passed('exact four tracked changed names')
mode_row=[{'descriptor':{'path':'fresh/actual.cpp'},'mode':0o600}];m.assert_patch_modes(mode_row,mode_row);passed('actual source mode preserved')
rejects('source executable mode change',lambda:m.assert_patch_modes(mode_row,[{'descriptor':{'path':'fresh/actual.cpp'},'mode':0o700}]))
for label,b in [('missing',('\0'.join(m.PATCH_FILES[:-1])+'\0').encode()),('extra',good+b'js/other.cpp\0'),('duplicate',good+str(m.PATCH_FILES[0]).encode()+b'\0'),('unterminated',good[:-1]),('invalidUTF8',b'\xff\0')]:
    rejects('tracked diff '+label,lambda b=b:m.assert_patch_diff_names(b))
text=(HERE/'build.py').read_text();ast.parse(text);ast.parse(Path(__file__).read_text());passed('two Python ASTs')
assert text.index('patch_input = authenticate_patch_family()')<text.index("monitor = utility(MONITOR, 'intl_build_original_owned_monitor')");passed('full patch auth precedes custom import')
assert "'apply', '--check'"in text and "'savedframe-patch-apply'"in text;passed('two explicit bounded owned git apply phases dormant')
assert "assert capability == saved_frame_eval"in text and 'installedSavedFrameApiHeader'in text;passed('actual installed capability and exact header required')
header=(m.REPO/m.PATCH_FAMILY/'after/js/public/SavedFrameAPI.h').read_text();assert re.search(r'^#define\s+JS_HAS_SAVEDFRAME_IS_EVAL\s+1\s*$',header,re.M);passed('actual new header macro shape')
workflow=(m.REPO/'.github/workflows/spidermonkey-intl.yml').read_text()
assert re.search(r'saved_frame_eval:\n(?:.*\n){0,4}\s+type: boolean\n\s+default: false',workflow)
assert "SM_SAVED_FRAME_EVAL: ${{ inputs.saved_frame_eval && '1' || '0' }}"in workflow;passed('workflow boolean defaults false and passes literal flag')
assert "intl${{ inputs.saved_frame_eval && '-savedframe-eval' || '' }}"in workflow;passed('Actions artifact variant identity')
print(json.dumps(dict(schemaVersion=1,state='INTL_SAVEDFRAME_OPTIN_SOURCE_CHECKS_PASSED_V1',checks=len(names),names=names,sourceFamilyPayloads=27,guestBaseCommit=m.COMMIT,patchSha256=m.PATCH_SHA,gitInvoked=False,compilerInvoked=False,guestExecuted=False,ciDispatched=False)))
