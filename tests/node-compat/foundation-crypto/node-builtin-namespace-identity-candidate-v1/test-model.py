"""Synthetic identity/cache decision checks; not a JSAPI/GC/runtime proof."""
from pathlib import Path
import json
OWN=Path(__file__).resolve().parent
def canonical(request,registered):
 if request not in registered:return request
 if request.startswith('node:'):return request
 other='node:'+request
 return other if other in registered and registered[other]is registered[request]and isinstance(registered[request],dict)else request
checks=[]
def case(name,request,mapping,wanted):assert canonical(request,mapping)==wanted,name;checks.append(name)
same={};different={}
case('same object explicit alias','crypto',{'crypto':same,'node:crypto':same},'node:crypto')
case('prefixed unchanged','node:crypto',{'crypto':same,'node:crypto':same},'node:crypto')
case('distinct objects unchanged','crypto',{'crypto':same,'node:crypto':different},'crypto')
case('missing prefixed registration','crypto',{'crypto':same},'crypto')
case('missing bare registration','crypto',{'node:crypto':same},'crypto')
case('arbitrary custom builtin unchanged','starling:test',{'starling:test':same},'starling:test')
case('bare nonalias unchanged','custom',{'custom':same},'custom')
case('equal primitives never alias','custom',{'custom':7,'node:custom':7},'custom')
case('embedded NUL key exact','a\0b',{'a\0b':same,'node:a':same},'a\0b')
case('embedded NUL registered alias exact','a\0b',{'a\0b':same,'node:a\0b':same},'node:a\0b')
case('Unicode registered alias exact','café',{'café':same,'node:café':same},'node:café')
for order in [('crypto','node:crypto'),('node:crypto','crypto')]:
 modules={};observed=[];registered={'crypto':same,'node:crypto':same}
 for request in order:
  key=canonical(request,registered)
  if key not in modules:modules[key]=object()
  observed.append(modules[key])
 assert observed[0]is observed[1]and len(modules)==1;checks.append('cache import order '+str(order))
text=(OWN/'script_loader.cpp').read_text()
assert 'RootedValue canonical_id(cx, StringValue(canonical_specifier));'in text
assert 'specifier_val.set(canonical_id);'in text and 'JS_ConcatStrings(cx, node_prefix, specifier)'in text
checks.append('afterimage rooted-id/string API source checks')
print(json.dumps(dict(schemaVersion=1,checks=len(checks),names=checks,syntheticModelOnly=True,jsApiGcOrGuestOrCryptoInvoked=False)))
