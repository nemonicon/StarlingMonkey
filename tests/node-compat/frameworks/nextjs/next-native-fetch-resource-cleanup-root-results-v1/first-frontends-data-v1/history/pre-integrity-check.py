"""Read-only stdlib retained-TAR checks. --current adds exact selected original text reads.
No archive extraction, Source eval/import, producer, C++/tool, SDK or engine scan.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import stat
import tarfile

HERE = Path(__file__).resolve().parent

def need(value, text):
    if value is not True: raise ValueError(text)

def exact(a,b,text):
    if type(a)is bytes or type(b)is bytes:
        need(type(a)is bytes and type(b)is bytes and a==b,text);return
    need(json.dumps(a,sort_keys=True,separators=(',',':')) == json.dumps(b,sort_keys=True,separators=(',',':')),text)

def physical(path):
    s=path.lstat(); need(path.resolve(strict=True)==path and stat.S_ISREG(s.st_mode) and s.st_nlink==1,'ordinary canonical selected text')
    return dict(dev=s.st_dev,ino=s.st_ino,mode=s.st_mode,nlink=s.st_nlink,size=s.st_size,mtimeNs=s.st_mtime_ns,ctimeNs=s.st_ctime_ns)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--current',action='store_true');args=parser.parse_args()
    ledger=json.loads((HERE/'payload-index.json').read_text());items=ledger['records']
    need(len(items)==ledger['totalOriginals']==47,'exact finite originals')
    need(sum(row['original']['bytes']for row in items)==ledger['totalBytes']<=33554432,'total text bytes')
    work=[row for row in items if row['role']=='complete-original-work']
    need(len(work)==ledger['workOriginals']==32 and sum(row['original']['bytes']for row in work)==ledger['workBytes']==20591543,'complete32WORK text payloads')
    members={row['member']:row for row in items};paths={row['original']['path']:row['member']for row in items}
    need(len(members)==len(paths)==47,'unique original/member paths')
    v1_names={'authority.json','result.json','source-before.json','source-after.json','tools-before.json','tools-after.json'}
    v2_names=v1_names|{'failed-attempt-before.json','failed-attempt-after.json'}|{f'owned-{i}/{name}'for i in range(3)for name in ['started.json','terminal.json','owned-0000.json','owned-0001.json','stdout.log','stderr.log']}
    need({name.removeprefix('work/v1/')for name in members if name.startswith('work/v1/')}==v1_names and
         {name.removeprefix('work/v2/')for name in members if name.startswith('work/v2/')}==v2_names,'exact6/26 original WORK namespaces')
    data={}; need((HERE/'data.tar.gz').stat().st_size<=8388608,'compressed cap')
    with tarfile.open(HERE/'data.tar.gz','r:gz')as archive:
        seen=set();total=0
        for member in archive:
            name=member.name;parts=PurePosixPath(name)
            need(member.isfile() and not member.issym() and not member.islnk(),'ordinary TAR members only')
            need(not parts.is_absolute() and '..'not in parts.parts and str(parts)==name and name not in seen and name in members,'canonical exact TAR namespace')
            seen.add(name);row=members[name];need(member.size==row['original']['bytes']<=8388608,'member byte bound')
            need(member.mode==row['originalMode'] and member.mtime==0,'archived mode and declared time normalization')
            body=archive.extractfile(member).read();total+=len(body);need(total<=33554432,'uncompressed cap')
            need(hashlib.sha256(body).hexdigest()==row['original']['sha256'],'exact original hash');body.decode('utf8');data[name]=body
        need(seen==set(members),'all and only indexed members')
    def js(name):return json.loads(data[name])
    def ref(ref):
        need(set(ref)=={'path','sha256','bytes'} and ref['path']in paths,'retained original ref')
        row=members[paths[ref['path']]];exact(row['original'],ref,'cross-file original descriptor');return data[row['member']]
    v1=js('work/v1/result.json');v2=js('work/v2/result.json')
    exact(v1['rawExitCodes'],[],'prelaunch has no compiler results');exact(v1['completedCommands'],0,'prelaunch zero commands')
    need(v1['passed']is False and v1['ownedClean']is None and v1['collectedTerminalsOwnedClean']is None and v1['primaryError']['type']=='AssertionError','prelaunch failure remains failed, no invented owner')
    exact(v2['rawExitCodes'],[0,0,1],'actual frontend failure raw codes');exact(v2['completedCommands'],3,'three actual commands')
    need(v2['passed']is False and v2['ownedClean']is True and v2['collectedTerminalsOwnedClean']is True and v2['primaryError']is None,'actual failed frontend clean collection')
    for prefix,result in [('v1',v1),('v2',v2)]:
        exact(ref(result['authority']),data[f'work/{prefix}/authority.json'],'result authority')
        need(result['fullBuildOrGuestAccepted']is False,'no fullbuild/guest acceptance')
        need(result['guards']['sourceUnchanged']is True and result['guards']['toolsUnchanged']is True,'reported protection flags')
        exact(js(f'work/{prefix}/source-before.json'),js(f'work/{prefix}/source-after.json'),'captured source bookends')
        exact(js(f'work/{prefix}/tools-before.json'),js(f'work/{prefix}/tools-after.json'),'captured documentary tools bookends')
    exact(js('work/v2/failed-attempt-before.json'),js('work/v2/failed-attempt-after.json'),'failedV1 current bookends')
    need(v2['guards']['failedAttemptUnchanged']is True,'V1 retained')
    authority=js('work/v2/authority.json');need(authority['perCommandSeconds']==180,'original frontend cap')
    owned_count=0
    for i,code in enumerate([0,0,1]):
        start=js(f'work/v2/owned-{i}/started.json');term=js(f'work/v2/owned-{i}/terminal.json')
        need(type(term['rawExitCode'])is int and term['rawExitCode']==code and start['pid']==term['pid'],'actual PID/raw')
        exact(start['authority'],term['authority'],'started terminal authority');ref(term['authority'])
        exact(start['authority'],v2['authority'],'genuine actual authority');exact(start['argv'],authority['commands'][i]['argv'],'literal argv')
        need(start['timeoutSeconds']==180 and start['argv'].count('-fsyntax-only')==1 and '-c'in start['argv'] and '-o'not in start['argv'] and not any(arg.startswith('-M')for arg in start['argv']),'frontend-only args')
        for key in ['timeout','forcedCleanup']:need(term[key]is False,'no timeout/force')
        for key in ['parentOwnedGroupGone','allObservedOwnedGroupsGone']:need(term[key]is True,'owned groups gone')
        for key in ['errors','signals','interruptedSignals','remainingObservedPids']:exact(term[key],[],'clean owned terminal')
        need(all(group['alive']is False for group in term['finalGroups']),'all final groups dead')
        records=[js(name)for name in sorted(data)if name.startswith(f'work/v2/owned-{i}/owned-')]
        exact([record['sequence']for record in records],list(range(len(records))),'sequential original owned records')
        exact([record['process']for record in records],term['observedProcesses'],'owned records/process inventory');owned_count+=len(records)
        need(ref(term['stdout'])==b'','empty actual stdout')
        stderr=ref(term['stderr'])
        if i<2:need(stderr==b'','successful frontend stderr empty')
        else:
            text=stderr.decode();exact([int(n)for n in re.findall(r':(\d+):\d+: error: ignoring return value',text)],[3355,3368,3406],'actualthree nodiscard diagnostics')
            need(text.count('[-Werror,-Wunused-result]')==3 and text.endswith('3 errors generated.\n'),'complete failed diagnostic')
    first=js('root/first-frontend-prelaunch-failure.json');need(first['compilerResultAccepted']is False and first['sourceChanged']is False,'prelaunch witness no compiler pass')
    for key,member in [('controller','root/run-frontends.py'),('inputs','root/frontend-inputs.json'),('result','work/v1/result.json')]:exact(ref(first[key]),data[member],'prelaunch proof ref')
    original_monitor=data['source/original-monitor.py'].decode()
    need(original_monitor.index('assert 0 < sample_seconds <= 1 and Path(output).is_dir()')<original_monitor.index('subprocess.Popen'),'retained monitor pre-Popen guard Source')
    review=js('root/actual-frontends-v2-review.json');need(review['verifiedDataConsistent']is True and review['frontendProfilePassed']is False and review['originalFailureReclassified']is False and review['compilerRerunByReviewer']is False and review['newObjectOrLinkOrEngineOrComponentOrGuestAccepted']is False,'independent C failed-DATA scope')
    for key,member in [('controller','root/run-frontends-v2.py'),('inputMap','root/frontend-inputs-v2.json'),('actualResult','work/v2/result.json'),('actualAuthority','work/v2/authority.json')]:exact(ref(review[key]),data[member],'independent review exact role')
    for item in items:
        exact(item['currentCaptureBefore'],item['currentCaptureAfter'],'curator reported physical readbookends')
        need(stat.S_ISREG(item['currentCaptureBefore']['mode']) and item['currentCaptureBefore']['nlink']==1 and
             stat.S_IMODE(item['currentCaptureBefore']['mode'])==item['originalMode'],'captured original file mode/nlink')
    if args.current:
        for item in items:
            path=Path(item['original']['path']);before=physical(path);exact(before,item['currentCaptureAfter'],'current selected identity/mode')
            body=path.read_bytes();need(len(body)==item['original']['bytes']and hashlib.sha256(body).hexdigest()==item['original']['sha256'],'current selected bytes')
            exact(physical(path),before,'current readbookend')
    print(json.dumps(dict(retainedDataVerified=True,currentSelectedText=args.current,originals=47,workOriginals=32,
                         workBytes=20591543,bytes=ledger['totalBytes'],prelaunchCompilerResults=[],actualFrontendRawExitCodes=[0,0,1],
                         actualOwnedRecords=owned_count,parentFrontendProfilePassed=False,compilerOrSourceOrProducerExecuted=False,
                         snapshotToolPayloadsRevalidated=False,fullBuildOrGuestAccepted=False)))

if __name__=='__main__':main()
