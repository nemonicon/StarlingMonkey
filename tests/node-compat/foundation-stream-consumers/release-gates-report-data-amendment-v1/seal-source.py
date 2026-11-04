#!/usr/bin/env python3
"""Seal only this new source proposal, no publication/action."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def h(b):return hashlib.sha256(b).hexdigest()
def row(p):
 b=p.read_bytes();return dict(path=p.relative_to(P).as_posix(),sha256=h(b),bytes=len(b))
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
checks=json.loads((P/'evidence/source-checks.json').read_text());assert checks['checks']==41
for r in json.loads((P/'source-inputs.json').read_text())['files']:
 b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and h(b)==r['sha256']
write('source-receipt.json',dict(schemaVersion=1,state='UNAPPLIED_REPORT_SOURCE_DATA_CLOSURE_CORRECTION_SOURCE_ONLY',baseIndexSha256='a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372',contextIndexSha256='9080e48fbccaf74835bfb8c8ef54c91b8df54ff5eb6e4c2cdc1c83443ad79b70',failedGeneratedFamilyIndexSha256='562e4236c8f99a34323c57c26f92749dba4aaf3e5dc1a509d33ababd97d79250',rootFailureSha256='ce4c52bd15fcbfef91fa7b877fa77f2a911626d30a265f7157a97b038fe9a49d',independentFailureIndexSha256='584b917832ef550bff00baf042f059f7604d1345154064939284f7326a8698a5',newPhysicalSnapshotFiles=1,producerBytes=2251,producerSha256='fe48fc8049fffbc7d60010f617369e498608db6e69cce05dbc4e06ed96a3c4ba',requiredDataRows=69,graphRows=160,graphEdges=259,publisherExactReverseEdits=14,runGateNamespaceEdits=1,sourceChecks=41,pythonASTOnlyChecks=3,preparationInputs=checks['originalSourceInputsRehashed'],sourcePublicationExecuted=False,ownerHelpersNodeNativeGuestOrHostInvoked=False,guestRunnerOracleCaseNativeBytesChanged=False,operationalAdmission=False,sourcePromotionAllowed=False,runtimeActionAuthority=None,partialPassReused=False))
files=[row(p) for p in sorted(P.rglob('*')) if p.is_file() and p!=P/'index.json']
write('index.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_CONSUMERS355_REPORT_DATA_SOURCE_AMENDMENT',files=files,sourceOnly=True,actionsAllowed=False,sourcePublicationExecuted=False,operationalAdmission=False))
print(json.dumps({n:row(P/n) for n in ['index.json','source-receipt.json','evidence/source-checks.json']}))
