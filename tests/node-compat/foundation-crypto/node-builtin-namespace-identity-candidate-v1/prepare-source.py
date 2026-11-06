"""Create one UNAPPLIED C++ afterimage; no native/helper/guest execution."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
SOURCE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert not(OWN/'index.json').exists()
 original=SOURCE/'runtime/script_loader.cpp';live=REPO/'runtime/script_loader.cpp'
 assert desc(original)['sha256']==desc(live)['sha256']=='479c23822b5e8b5ec9ea2b449d45905b455cad953a02d3208268d54f03645413'
 text=original.read_text();before=text
 edits=[dict(before='#include <js/ScriptPrivate.h>\n',after='#include <js/ScriptPrivate.h>\n#include <js/String.h>\n')]
 old='''    RootedValue specifier_val(cx, StringValue(specifier));
    RootedObject builtin_obj(cx, &builtin_val.toObject());
    RootedObject result(cx, get_builtin_module(cx, specifier_val, builtin_obj));'''
 new='''    RootedValue specifier_val(cx, StringValue(specifier));
    RootedObject builtin_obj(cx, &builtin_val.toObject());
    // Share one module-record cache key only for explicitly registered aliases
    // whose builtin values are the exact same object. Other builtin IDs retain
    // their original module records and import.meta lookup keys.
    if (!std::string_view(path.get()).starts_with("node:")) {
      RootedString node_prefix(cx, JS_NewStringCopyZ(cx, "node:"));
      if (!node_prefix) {
        return false;
      }
      // Concatenate JS strings so Unicode and embedded NULs are not truncated.
      RootedString canonical_specifier(cx, JS_ConcatStrings(cx, node_prefix, specifier));
      if (!canonical_specifier) {
        return false;
      }
      RootedValue canonical_id(cx, StringValue(canonical_specifier));
      RootedValue canonical_builtin(cx);
      if (!JS::MapGet(cx, builtinModules, canonical_id, &canonical_builtin)) {
        return false;
      }
      if (canonical_builtin.isObject() && &canonical_builtin.toObject() == builtin_obj.get()) {
        // This outer root remains live across module compilation/allocation.
        specifier_val.set(canonical_id);
      }
    }
    RootedObject result(cx, get_builtin_module(cx, specifier_val, builtin_obj));'''
 edits.append(dict(before=old,after=new))
 for e in edits:assert text.count(e['before'])==1;text=text.replace(e['before'],e['after'])
 (OWN/'script_loader.cpp').write_text(text)
 inverse=text
 for e in reversed(edits):assert inverse.count(e['after'])==1;inverse=inverse.replace(e['after'],e['before'])
 assert inverse==before
 save('derivation.json',dict(schemaVersion=1,before=desc(original),liveBefore=desc(live),after=desc(OWN/'script_loader.cpp'),edits=edits,forwardAndInverseWholeBytesVerified=True,productionOrStagedFilesChanged=False))
 # These fixtures are future Node/guest differential inputs, never evaluated
 # during preparation. Import order is the only difference between them.
 body='''export function run() {
  return JSON.stringify({schemaVersion:1,kind:'builtin-namespace-alias-identity-v1',
    namespaces:{crypto:cryptoBare===cryptoNode,buffer:bufferBare===bufferNode,stream:streamBare===streamNode},
    defaultObjects:{crypto:cryptoBare.default===cryptoNode.default,buffer:bufferBare.default===bufferNode.default,stream:streamBare.default===streamNode.default},
    namedFunctions:{createHash:cryptoBare.createHash===cryptoNode.createHash,createHmac:cryptoBare.createHmac===cryptoNode.createHmac,Buffer:bufferBare.Buffer===bufferNode.Buffer,Readable:streamBare.Readable===streamNode.Readable},
    constants:{cryptoSame:cryptoBare.constants===cryptoNode.constants,opensslVersionNumber:cryptoNode.constants.OPENSSL_VERSION_NUMBER},
    providerIdentityProved:false,cryptoOperationsInvoked:false,publicProfileAdmission:false});
}
'''
 for order in ['bare-first','prefixed-first']:
  imports=[]
  for name in ['crypto','buffer','stream']:
   pair=[f"import * as {name}Bare from '{name}';",f"import * as {name}Node from 'node:{name}';"]
   imports.extend(pair if order=='bare-first'else pair[::-1])
  (OWN/(order+'.mjs')).write_text('\n'.join(imports)+'\n'+body)
 (OWN/'scalar.wit').write_text('package validation:builtin-alias;\nworld validation { export run: func() -> string; }\n')
 save('fixture-plan.json',dict(schemaVersion=1,sourceOnly=True,fixtures=[desc(OWN/(order+'.mjs'))for order in ['bare-first','prefixed-first']],wit=desc(OWN/'scalar.wit'),rawNativeImportsRequired=True,bundlingMustNotCanonicalizeBareSpecifiers=True,prospectiveNodeAndGuestNamespaceBooleans=dict(crypto=True,buffer=True,stream=True),expectedDefaultAndNamedIdentity=True,nativeHeaderVersionNumberMustRemainSeparateFromHostProvider=True,actualFixtureExecuted=False,actualNewEngine=None))
 print(json.dumps(desc(OWN/'script_loader.cpp')))
if __name__=='__main__':main()
