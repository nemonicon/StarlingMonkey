"""Tiny owned-text tests of publisher mechanisms, never publisher main."""
import importlib.util,json,os,tempfile,stat
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
source=scratch/'input.txt';source.write_bytes(b'only ordinary text');m.need(stat.S_IMODE(source.stat().st_mode)==0o644,'Actual0644 fixture required; never chmod a proof original')
original=source.stat();row=m.capsule_copy_row(m.descriptor(source),'data/source.txt','owned-text-proof-capsule')
yes(lambda:m.need(row['sourceMode']==0o644 and row['outputMode']==0o600,'Real644 source separate from600 destination'))
yes(lambda:m.source(row))
yes(lambda:m.need(m.source(row,True)==b'only ordinary text','Exact small text bytes'))
no(lambda:m.source({**row,'sourceMode':0o600}))
no(lambda:m.source({**row,'sha256':'a'*64}))
no(lambda:m.source({**row,'mode':0o600}))
link=scratch/'symlink.txt';link.symlink_to(source);no(lambda:m.source({**row,'source':str(link)}))
root=m.Publication(scratch/'owned')
try:
    yes(lambda:root.copy(row));yes(lambda:root.actual_members())
    yes(lambda:m.need(stat.S_IMODE((root.path/row['destination']).stat().st_mode)==0o600,'Copied proof permissions0600'))
    yes(lambda:m.need(root.rows[row['destination']]['sourceMode']==0o644 and root.rows[row['destination']]['outputMode']==0o600 and root.rows[row['destination']]['mode']==0o600,'Both permission roles preserved in copied inventory'))
    after=source.stat();yes(lambda:m.need((original.st_dev,original.st_ino,original.st_size,original.st_mtime_ns,original.st_ctime_ns,original.st_mode)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns,after.st_mode),'Original identity/hash/mode unchanged; no chmod'))
    no(lambda:root.copy({**row,'destination':'wrong-mode.txt','sourceMode':0o600}))
    no(lambda:root.copy({**row,'destination':'missing-role.txt','outputMode':None}))
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
