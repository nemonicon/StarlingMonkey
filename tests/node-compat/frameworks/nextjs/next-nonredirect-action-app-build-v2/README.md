This fresh v2 Source candidate corrects one HTML attribute in the nonredirect action fixture: `pattern="[a-z0-9-]+"` becomes `pattern="(?:[a-z0-9]|-)+"`. The literal hyphen is outside the character class under HTML's UnicodeSets `v` regular-expression mode ([WHATWG pattern rule](https://html.spec.whatwg.org/multipage/input.html#the-pattern-attribute), primary Source inspected by Root). The server-side bounded-value validator, Server Action, React `useActionState` consumer and original redirect fixture are unchanged. Exactly 33 fixture files are byte-identical to v1; the 34th differs only in that attribute.

Root's completed v1 native and Node controls both remain raw1/clean failures: their functional result, five script assets and POST body/sizes/finished succeeded, but Chrome reported the invalid HTML pattern. This candidate fixes the fixture; it does not filter console errors, relax a predicate, retry/overwrite either result or claim runtime success. Their final independent primary review was pending at this Source cutoff. All v1 files and results remain intact.

The builder is the same genuine four-phase implementation with only its fixture-catalogue version literal changed. `builder.patch` and `fixture.patch` retain the exact diffs. Node22.14.0/npm10.9.2, locked normal npm-ci/private cache, original120/120/600/900 owners, webpack build, standalone tracing, generated identifiers and complete dynamic application inventory remain required. No native-engine/component rebuild is added. Root must authenticate tools, the accepted interop prerequisite and genuine before/final guards as for v1.

Root alone may execute the new build after Source review:

```sh
/opt/homebrew/Cellar/python@3.11/3.11.10/Frameworks/Python.framework/Versions/3.11/bin/python3.11 -I -B \
  tests/node-compat/frameworks/nextjs/next-nonredirect-action-app-build-v2/build.py \
  --output /private/tmp/starling-node-compat/next-nonredirect-action-app-build-v2-first \
  --node /private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  --npm-cli /private/tmp/starling-node-compat/next-app-tools-bootstrap-v1/lib/node_modules/npm/bin/npm-cli.js
```

New generated HTML/script pins, application inventory/root identity, action IDs and runtime inputs must come from the genuine new build. No v1 proof arrays or generated asset hashes are retargeted. `/action-value` remains outside existing guest/native/outer correlation route classifiers. Root owns eventual bindings and execution; no actual new Source index/build/runtime fields are filled here.

R performed only own Source copying, byte/hash/JSON checks and Python AST parsing of the selector-only builder. No retained functions, CLI, JS parser, Node/npm/Next, guard, compiler, host, guest or browser executed. This family is frozen unsealed for Source review. The existing strict gates, original redirect failures and experimental-runtime qualifications remain unchanged.
