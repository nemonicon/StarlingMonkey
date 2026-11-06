"""Actual process/publication envelopes only, no source or target functions."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;S=P.parent;summary=json.loads((P/'intake-summary.json').read_bytes());root=json.loads(Path(summary['rootResult']['path']).read_bytes());inv=json.loads(Path(root['invocation']['path']).read_bytes());auth=json.loads(Path(root['rootAuthority']['path']).read_bytes());refs=json.loads((S/'combined-native-runtime-candidate-v3/references.json').read_bytes());checks=0

def yes(x,m='envelope'):
 global checks
 checks+=1;assert x,m

def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))

starts={};files=[]
for role,cap in [('externalParentTerminal',1200),('outerTerminal',1800)]:
 d=Path(root[role]['path']).parent;start=json.loads((d/'started.json').read_bytes());term=json.loads((d/'terminal.json').read_bytes());starts[role]=start;yes(start['authority']==term['authority']==root['rootAuthority']);yes(start['pid']==term['pid']and start['timeoutSeconds']==cap);yes(term['rawExitCode']==0 and term['timeout']is False and term['forcedCleanup']is False)
 for k in ['errors','signals','interruptedSignals','remainingObservedPids']:yes(term[k]==[])
 yes(term['parentOwnedGroupGone']and term['allObservedOwnedGroupsGone']);yes(all(x['alive']is False for x in term['finalGroups']))
 for p in sorted(d.rglob('*')):
  yes(not p.is_symlink())
  if p.is_file():files.append(row(p))
yes(starts['outerTerminal']['argv']==inv['actualArgv']);yes(starts['externalParentTerminal']['argv'][:3]==[refs['node']['path'],auth['entry']['path'],'parent']);yes(len(starts['externalParentTerminal']['argv'])==4 and json.loads(starts['externalParentTerminal']['argv'][3])==root['config']);yes(json.loads(inv['actualArgv'][-1])==root['config']);yes(inv['actualArgv'][-2]==auth['externalController']['path']);yes(inv['originalInnerDeadlineSeconds']==1200 and inv['originalOuterDeadlineSeconds']==1800);yes(root['generatedApplicationImported']is root['ordinaryExportsInvoked']is False)
correction=S/'combined-native-runtime-v3-root-observe-preparation-correction-v1.json';v=json.loads(correction.read_bytes());yes(v['targetOperationRerun']is False and v['targetToolSession']==30639 and v['targetToolRawExitCode']==0 and v['rootResultWrittenBeforeCorrection']is False)
yes(v['actualToolObservation']['rawExitCode']==1 and v['actualToolObservation']['chunkId']=='d9acca')
# Actual current observer is authenticated as the corrected reader, not old digest.
obs=root['observer'];yes(row(obs['path'])==obs);yes(obs['sha256']!=v['originalObserver']['sha256']);yes('root-caller' in Path(obs['path']).read_text())
copies=[]
for p in [correction,*[Path(root[r]['path']).parent/'started.json'for r in ['externalParentTerminal','outerTerminal']]]:
 dst=P/'raw'/'extra'/p.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes());yes(row(dst)['sha256']==row(p)['sha256']);copies.append(dict(original=row(p),copy=row(dst)))
value=dict(schemaVersion=1,passed=True,checks=checks,toolObservation=root['toolObservation'],originalInnerDeadlineSeconds=1200,originalOuterDeadlineSeconds=1800,innerNodePid=starts['externalParentTerminal']['pid'],outerPythonPid=starts['outerTerminal']['pid'],allMonitorFiles=files,wholeActualStarts=starts,observerPreparationCorrection=row(correction),observerHistoryQualification='Retained Root reader correction records its initial envelope-selection error before any result write; both actual original process/publication streams independently replayed. No target rerun.',extraRawCopies=copies,reviewerProcessOrTargetInvoked=False)
(P/'envelope-review.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks,actualMonitorFiles=len(files),inner=1200,outer=1800)))
