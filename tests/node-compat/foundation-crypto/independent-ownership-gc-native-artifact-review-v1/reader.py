"""Gated independent actual-freeze DATA reader under preparation.

This refuses before any freeze-root read unless an explicit final Root tuple is supplied.
It deliberately issues no PASS: later full native/witness/receipt audit must complete.
"""
from pathlib import Path
import json,sys
import review_io as I
import artifact_model as M
HERE=Path(__file__).resolve().parent
def enter(inputs):
    I.need(inputs['rootFinalRawToolTerminalReceived']is True,'Root final external tool terminal required before freeze output reads')
    I.need(inputs['rootObservedToolRawExitCode']==0,'Root raw0 required, never partial output acceptance')
    root=I.read(inputs['rootFreezeObservation'],'whole actual immutable Root freeze observation')
    terminal=I.read(inputs['externalParentTerminal'],'actual final freeze external terminal')
    for field,value in dict(rawExitCode=0,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True).items():M.equal(terminal[field],value,'actual bounded freeze terminal '+field)
    for field in ['errors','signals','interruptedSignals','remainingObservedPids']:M.equal(terminal[field],[],'actual clean final '+field)
    I.verify(terminal['stdout'],'full raw freeze stdout');I.verify(terminal['stderr'],'full raw freeze stderr');I.need(terminal['stderr']['bytes']==0,'actual clean freeze stderr')
    root_phase=I.read(inputs['rootFreezeAuthority'],'entire actual Root freeze-only authority')
    I.need(root_phase['phase']=='freeze'and root_phase['sourceIndexSha256']=='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05','genuine new freeze-only Root phase')
    M.equal(root_phase['configuredSourceRoot'],M.SOURCE,'real GC configured root');M.equal(root_phase['workRoot'],M.WORK,'real GC work root');M.equal(root_phase['freezeRoot'],M.FREEZE,'real separate GC freeze root')
    M.equal(terminal['authority'],inputs['rootFreezeAuthority'],'actual terminal genuine authority, no projection')
    # The concrete Root receipt schema and complete finite witness paths are supplied
    # only after the final actual tuple; no guessed carrier can issue acceptance.
    raise RuntimeError('PRIVATE_READER_UNFINISHED: complete actual Root/receipt/copy/native/witness bindings and final normal/source rehash; no verdict issued')
if __name__=='__main__':
    I.need(len(sys.argv)==2,'one explicit independent audit input JSON descriptor')
    descriptor=json.loads(sys.argv[1]);enter(I.read(descriptor,'independent final actual input tuple'))
