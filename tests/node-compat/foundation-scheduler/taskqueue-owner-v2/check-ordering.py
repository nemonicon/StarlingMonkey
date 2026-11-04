#!/usr/bin/env python3
"""Pure Python ordering model checked against previously executed exact Node22 traces.
This is NOT execution of the proposed C++ scheduler or any guest component.
"""
from collections import deque
from pathlib import Path
import hashlib, json
HERE=Path(__file__).resolve().parent
source=HERE.parent/'node-results.json'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='7e61775b17b889f3bc0ccfae37eba8520f8f48a9b153002361019c728d7bdb18'
node=json.loads(source.read_text()); assert node['node']=='v22.14.0'
def model(promise_first):
    ticks,jobs,trace=deque(),deque(),[]
    def promise():
        trace.append('promise-first')
        ticks.append(lambda:trace.append('tick-from-promise'))
        jobs.append(lambda:trace.append('nested-promise'))
    def tick():
        trace.append('tick-first')
        ticks.append(lambda:trace.append('nested-tick'))
        jobs.append(lambda:trace.append('promise-from-tick'))
    jobs.append(promise); ticks.append(tick); jobs.append(lambda:trace.append('microtask'))
    while True:
        if not promise_first:
            while ticks: ticks.popleft()()
        promise_first=False
        while jobs: jobs.popleft()()
        if not ticks: return trace
records=[]
for row in node['boundaryCases']:
    predicted=model(row['boundary'] in ['esm-initial','promise-job'])
    assert row['passed'] and row['trace']==row['expected']==predicted
    records.append({'boundary':row['boundary'],'executedNodeTrace':row['trace'],
                    'predictedPhaseModelTrace':predicted,'phaseModelMatchesNode':True})
result={'status':'reused-executed-Node22-oracles-plus-pure-Python-phase-model',
        'nodeRelease':node['node'],'nodeBinarySha256':node['nodeBinarySha256'],
        'nodeEvidence':{'path':'../node-results.json','sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
        'nativeSchedulerCompiled':False,'guestExecuted':False,'cases':records,
        'contractAndFatalEvidenceReused':node['contracts'],
        'fatalNodeEvidence':node['fatal'],
        'qualification':'Promise-job row models ticks registered while full checkpoint is already draining; it does not add a reentrant C++ checkpoint.'}
(HERE/'ordering-proof.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'nodeRelease':'v22.14.0','reusedNodeCases':len(records),'phaseModelMatches':len(records),'nativeCompiled':False,'guestExecuted':False}))
