"""Derive only four authenticated guest-SM afterimages; no build or Git action."""
from pathlib import Path
import difflib,hashlib,json
HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'primary-source.json').read_text())
assert data['commit']=='9dab3d6f643e926a340c391ea30968e940390dec'
sources={}
for r in data['files']:
    b=(HERE/'before'/r['path']).read_bytes()
    assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['gitBlobSha1']
    sources[r['path']]=b.decode()
edits=[]
def edit(path,before,after):
    assert sources[path].count(before)==1,(path,before)
    sources[path]=sources[path].replace(before,after)
    edits.append(dict(path=path,before=before,after=after))
api='js/public/SavedFrameAPI.h';header='js/src/vm/SavedFrame.h';cpp='js/src/vm/SavedStacks.cpp';clone='js/src/vm/StructuredClone.cpp'
anchor='/**\n * Given a SavedFrame JSObject, get its line property (1-origin).'
edit(api,anchor,'''// StarlingMonkey guest extension, version 1. The library and installed header
// must be built from the same authenticated patch.
#define JS_HAS_SAVEDFRAME_IS_EVAL 1

/**
 * Get captured JS eval/dynamic-function provenance without interpreting source
 * names or sourceURL text. Live ordinary sources without an introduction type
 * are false; eval and the standard dynamic-function constructors are true.
 * Unrecognized introduction types, heap-reconstructed frames, and all frames
 * read through structured clone have unknown provenance. Like a principal
 * refusal, unknown provenance returns AccessDenied and writes false to isEvalp;
 * that false is only a safe default, NOT a successful non-eval classification.
 * Async adoption preserves the captured provenance. Wasm frames are non-eval.
 * This API does not expose eval origins or provide cloned-stack eval parity.
 */
extern JS_PUBLIC_API SavedFrameResult GetSavedFrameIsEval(
    JSContext* cx, JSPrincipals* principals, Handle<JSObject*> savedFrame,
    bool* isEvalp,
    SavedFrameSelfHosted selfHosted = SavedFrameSelfHosted::Include);

'''+anchor)
edit(header,'#include "mozilla/Attributes.h"','#include "mozilla/Attributes.h"\n#include "mozilla/Maybe.h"')
edit(header,'  uint32_t getSourceId();','  uint32_t getSourceId();\n  mozilla::Maybe<bool> getIsEval();')
edit(header,'  void initSourceId(uint32_t id);','  void initSourceId(uint32_t id);\n  void initIsEval(mozilla::Maybe<bool> isEval);')
edit(header,'    JSSLOT_SOURCEID,','    JSSLOT_SOURCEID,\n    JSSLOT_ISEVAL,  // Boolean for known provenance, undefined for unknown.')
edit(cpp,'#include <algorithm>','#include <algorithm>\n#include <cstring>')
edit(cpp,'         bool mutedErrors,\n','         bool mutedErrors, Maybe<bool> isEval,\n')
edit(cpp,'        mutedErrors(mutedErrors),','        mutedErrors(mutedErrors),\n        isEval(isEval),')
edit(cpp,'        mutedErrors(savedFrame.getMutedErrors()),','        mutedErrors(savedFrame.getMutedErrors()),\n        isEval(savedFrame.getIsEval()),')
edit(cpp,'  bool mutedErrors;\n','  bool mutedErrors;\n  Maybe<bool> isEval;\n')
edit(cpp,'  bool mutedErrors() { return value().mutedErrors; }','  bool mutedErrors() { return value().mutedErrors; }\n  Maybe<bool> isEval() { return value().isEval; }')
edit(cpp,'                   lookup.mutedErrors, parentHash,','                   lookup.mutedErrors,\n                   lookup.isEval.isSome() ? (*lookup.isEval ? 2 : 1) : 0,\n                   parentHash,')
edit(cpp,'  if (existing->getLine() != lookup.line) {','  if (existing->getIsEval() != lookup.isEval) {\n    return false;\n  }\n\n  if (existing->getLine() != lookup.line) {')
anchor='uint32_t SavedFrame::getLine() {'
edit(cpp,anchor,'''Maybe<bool> SavedFrame::getIsEval() {
  const Value& value = getReservedSlot(JSSLOT_ISEVAL);
  MOZ_ASSERT(value.isBoolean() || value.isUndefined());
  if (value.isBoolean()) {
    return Some(value.toBoolean());
  }
  return Nothing();
}

'''+anchor)
anchor='void SavedFrame::initLine(uint32_t line) {'
edit(cpp,anchor,'''void SavedFrame::initIsEval(Maybe<bool> isEval) {
  initReservedSlot(JSSLOT_ISEVAL,
                   isEval.isSome() ? BooleanValue(*isEval) : UndefinedValue());
}

'''+anchor)
edit(cpp,'  initSourceId(lookup.sourceId());','  initSourceId(lookup.sourceId());\n  initIsEval(lookup.isEval());')
anchor='JS_PUBLIC_API SavedFrameResult GetSavedFrameLine('
edit(cpp,anchor,'''JS_PUBLIC_API SavedFrameResult GetSavedFrameIsEval(
    JSContext* cx, JSPrincipals* principals, HandleObject savedFrame,
    bool* isEvalp,
    SavedFrameSelfHosted selfHosted /* = SavedFrameSelfHosted::Include */) {
  js::AssertHeapIsIdle();
  CHECK_THREAD(cx);
  MOZ_RELEASE_ASSERT(cx->realm());
  MOZ_ASSERT(isEvalp);
  *isEvalp = false;
  bool skippedAsync;
  Rooted<js::SavedFrame*> frame(cx, UnwrapSavedFrame(cx, principals, savedFrame,
                                                     selfHosted, skippedAsync));
  if (!frame) {
    return SavedFrameResult::AccessDenied;
  }
  Maybe<bool> isEval = frame->getIsEval();
  if (isEval.isNothing()) {
    return SavedFrameResult::AccessDenied;
  }
  *isEvalp = *isEval;
  return SavedFrameResult::Ok;
}

'''+anchor)
anchor='bool SavedStacks::insertFrames(JSContext* cx, MutableHandle<SavedFrame*> frame,'
edit(cpp,anchor,'''// Compilation metadata belongs to the ScriptSource shared by its nested
// functions. The display URL/filename is intentionally never consulted here.
static Maybe<bool> SavedFrameEvalProvenance(FrameIter& iter) {
  if (iter.isWasm()) {
    return Some(false);
  }
  JSScript* script = iter.script();
  if (script->isForEval()) {
    return Some(true);
  }
  ScriptSource* source = script->scriptSource();
  if (!source->hasIntroductionType()) {
    return Some(false);
  }
  const char* type = source->introductionType();
  if (std::strcmp(type, "eval") == 0 || std::strcmp(type, "Function") == 0 ||
      std::strcmp(type, "GeneratorFunction") == 0 ||
      std::strcmp(type, "AsyncFunction") == 0 ||
      std::strcmp(type, "AsyncGenerator") == 0) {
    return Some(true);
  }
  // Other embedders/debugger introduction kinds are not classified by this
  // bounded extension. The getter refuses instead of returning a guessed bool.
  return Nothing();
}

'''+anchor)
edit(cpp,'                                  principals, iter.mutedErrors(), framePtr,','                                  principals, iter.mutedErrors(),\n                                  SavedFrameEvalProvenance(iter), framePtr,')
edit(cpp,'                                /* mutedErrors */ true)) {','                                /* mutedErrors */ true,\n                                /* isEval */ Nothing())) {')
edit(clone,'  savedFrame->initSourceId(0);','  savedFrame->initSourceId(0);\n  // Clone wire format has no eval provenance; never fabricate non-eval.\n  savedFrame->initIsEval(mozilla::Nothing());')
assert set(sources)=={api,header,cpp,clone}
patch=[];after=[]
for path,text in sources.items():
    before=(HERE/'before'/path).read_text();assert text!=before
    out=HERE/'after'/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text)
    b=out.read_bytes();after.append(dict(path=path,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
    patch.extend(difflib.unified_diff(before.splitlines(True),text.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
(HERE/'saved-frame-is-eval-v1.patch').write_text(''.join(patch))
(HERE/'derivation.json').write_text(json.dumps(dict(schemaVersion=1,baseCommit=data['commit'],changedFiles=4,edits=edits,after=after,uncompiled=True,cloneWireFormatChanged=False,unknownProvenanceRefused=True),indent=2)+'\n')
print(json.dumps(dict(changedFiles=4,exactEdits=len(edits),uncompiled=True)))
