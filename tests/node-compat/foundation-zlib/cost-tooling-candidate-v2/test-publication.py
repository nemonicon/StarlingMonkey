"""Tiny owned-text tests of publisher mechanisms, never publisher main."""
import importlib.util,json,os,tempfile
from pathlib import Path
HERE=Path(__file__).parent.resolve();spec=importlib.util.spec_from_file_location('cost_source_publisher_test_only',HERE/'publish.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=0
def yes(fn):
    global checks
    fn();checks+=1
def no(fn):
    global checks
    try:fn()
    except(Exception,):checks+=1;return
    raise AssertionError('Expected refusal')
for value in['../escape','/absolute','a/../b','a//b','a/./b','a\\b','a\0b',''] :no(lambda value=value:m.safe(value))
yes(lambda:m.safe('owned/member.txt'))
scratch=Path(tempfile.mkdtemp(prefix='zlib-cost-publisher-text-only-',dir='/private/tmp'))
source=scratch/'input.txt';source.write_bytes(b'only ordinary text');source.chmod(0o600);row=m.descriptor(source);row.update(destination='data/source.txt',mode=0o600)
yes(lambda:m.source(row))
yes(lambda:m.need(m.source(row,True)==b'only ordinary text','Exact small text bytes'))
link=scratch/'symlink.txt';link.symlink_to(source);no(lambda:m.source({**row,'source':str(link)}))
root=m.Publication(scratch/'owned')
try:
    yes(lambda:root.copy(row));yes(lambda:root.actual_members())
    no(lambda:root.copy(row))
    yes(lambda:root.json('tiny.json',{'only':'text'}));yes(lambda:root.actual_members())
    no(lambda:root.data('../escape',b'no'))
    no(lambda:m.Publication(scratch/'owned'))
    (root.path/'untracked.txt').write_bytes(b'untracked');no(lambda:root.actual_members())
    (root.path/'untracked.txt').unlink()
    os.link(root.path/'tiny.json',root.path/'unexpected-hardlink');no(lambda:root.actual_members())
    (root.path/'unexpected-hardlink').unlink();yes(lambda:root.actual_members())
finally:root.close()
print(json.dumps({'schemaVersion':1,'state':'OWNED_TEXT_PUBLICATION_MECHANISM_TESTS_PASSED','checks':checks,'scratch':str(scratch),'publisherMainInvoked':False,'realPublicationCreated':False,'codecOrLibraryOrNativeOrGuestInvoked':False}))
