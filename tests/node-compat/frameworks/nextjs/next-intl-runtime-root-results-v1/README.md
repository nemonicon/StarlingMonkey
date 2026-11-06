# Next.js runtime regression results

The immutable `actual-review/` baseline records Unicode36/36, dependencies48/48,
stack9/12 and full Next11/24 HTTP results on the Intl-enabled V7 engine. Its
portable reader passes; full Next and strict stack acceptance remain false.

Reader scope: it authenticates all retained bytes, compares captured selected
projection objects and preservation flags, and checks recorded owned shutdown.
It does not independently replay every raw body through the original JavaScript
projection helpers or re-establish historical source bookends. A separate
read-only review correlated all six Unicode/stack raw bodies with their saved
typed payloads and confirmed the stack differences are only two fields in the
anonymous first frame's function-name type. Runtime reproduction requires the
actual component/stock-host collectors and fresh output directories.

The diagnostic V2 successor additionally proves that the original CommonJS
compile input contains U+20AC, while the failed assertion's expected compiled
literal is mojibake. The POST input's intrinsic brand is Uint8Array, offset0,
length134, but it fails the captured constructor's instanceof test. Those
findings narrow the fixes to source compilation and intrinsic view recognition.
V2 result retention is a separate successor; the five-run baseline is unchanged.
