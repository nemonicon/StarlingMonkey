"""Finite Source/hash/line-reader checks only; never loads or evaluates guest/native code."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import stat

HERE=Path(__file__).resolve().parent
BASE=HERE.parent

def stamp(p):
 s=p.lstat();return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def main():
 seen={};checks=[]
 def raw(p):
  p=Path(p);s=stamp(p)
  assert p.is_absolute() and p.resolve()==p and stat.S_ISREG(s[2]) and s[3]==1 and 0<=s[4]<=262144
  b=p.read_bytes();assert len(b)==s[4] and stamp(p)==s;seen[p]=s;return b
 def obj(p):return json.loads(raw(p))
 def ref(r):
  b=raw(r['path']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];return b
 def yes(ok,name):assert ok,name;checks.append(name)
 parent=BASE/'next-public-request-correlation-entry-v1';old=raw(parent/'guest-entry.mjs');new=raw(HERE/'guest-entry.mjs')
 yes(hashlib.sha256(old).hexdigest()=='a1d66a6e3427204f5fc0a8e2207836e71eea7b095926ce5b38e4e2ecef65c8d3','exact held parent entry')
 m=obj(HERE/'afterimages.json');ref(m['baseSourceIndex']);yes(ref(m['before'])==old and ref(m['after'])==new,'exact afterimage descriptors')
 text=new.decode()
 for delta in reversed(m['changes']):
  yes(text.count(delta['after'])==1,'unique after span: '+delta['kind']);text=text.replace(delta['after'],delta['before'])
 yes(text.encode()==old and len(new)-len(old)==500,'only two reviewed replacements')
 patch=''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='parent/guest-entry.mjs',tofile='candidate/guest-entry.mjs')).encode()
 yes(ref(m['patch'])==patch,'exact unified patch')
 yes(raw(HERE/'marker-contract.json')==raw(parent/'marker-contract.json'),'V2 contract byte-identical')
 s=new.decode();yes(s.count('__nativeExportObserve(')==1 and s.count("import {observe as __nativeExportObserve} from 'internal:starlingmonkey/native-export-diagnostic-v1';")==1,'one named import and one lexical call')
 yes(s.count('await ')==old.decode().count('await ') and s.count('new Request(')==old.decode().count('new Request(') and s.count('getReader(')==old.decode().count('getReader('),'no added awaits Request or reader sites')
 p=obj(HERE/'plan.json');q=obj(parent/'plan.json');c=obj(HERE/'native-module-contract.json')
 yes(p['entry']==m['after'] and ref(p['entry'])==new and ref(p['nativeModuleContract'])==raw(HERE/'native-module-contract.json'),'plan product joins')
 yes(p['selectedInterfaces']==q['selectedInterfaces'] and len(p['selectedInterfaces'])==13 and p['componentExports']==q['componentExports'] and p['worldSourceIndex']==q['worldSourceIndex'] and p['witDirectory']==q['witDirectory'] and p['witInputs']==q['witInputs'],'unchanged world and13 interfaces')
 ref(p['worldSourceIndex'])
 for r in p['witInputs']:ref(r)
 yes(c['module']=='internal:starlingmonkey/native-export-diagnostic-v1' and c['imports']==dict(named=['observe'],default=None,namespace=None) and c['arity']==5,'exact prospective named module ABI')
 yes([x['values'] for x in c['arguments'][:4]]==[{'GET':0,'POST':1},{'/actions':0,'/action-result':1},{'missing':0,'valid':1,'invalid':2,'duplicate':3},[0,1,2]],'exact five primitive argument enums')
 yes(c['defaultBuildOption']['name']=='NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1' and c['defaultBuildOption']['default']=='OFF' and c['defaultBuildOption']['actualBuildProof'] is None,'explicit new default-OFF opt-in requirement')
 required=['requiredEngine','requiredNativeMetadata','requiredFullNativeBuildReview','requiredNativeDiagnosticSourceIndex','requiredNativeDiagnosticMarkerContract']
 yes(all(p[k] is None for k in required) and all(v is None for k,v in p.items() if k.startswith('actual')),'all new engine build constructor runtime actuals NULL')
 audit=obj(HERE/'native-builtin-resolution.json');yes(ref(p['nativeBuiltinResolution'])==raw(HERE/'native-builtin-resolution.json'),'resolution audit plan descriptor')
 for item in audit['references']:
  lines=ref(item['source']).decode().splitlines()
  for w in item['witnesses']:yes('\n'.join(lines[w['firstLine']-1:w['lastLine']])==w['excerpt'],'primary Source line witness')
 ast.parse(raw(HERE/'test-source.py'))
 yes(all(stamp(path)==s for path,s in seen.items()),'final Source read bookends')
 print(json.dumps(dict(passed=True,checks=len(checks),names=checks,filesRead=len(seen),sourceOnly=True,pythonASTOnly=True,guestParsedOrExecuted=False,nativeHelperGuardNodeComponentizeTargetInvoked=False,actualConstructionOrRuntimeProved=False),sort_keys=True))

if __name__=='__main__':main()
