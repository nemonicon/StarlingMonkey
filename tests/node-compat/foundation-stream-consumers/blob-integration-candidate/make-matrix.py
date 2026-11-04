#!/usr/bin/env python3
"""Finite candidate matrix; Node inventory is observation, not native parity."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
node=json.loads((HERE/'node-results.json').read_text())
rows=[]
def row(api,strategy,deviations,validation,source,status='unverified',capability=None,availability='four-file-source-candidate-unlinked'):
    rows.append({'api':api,'targetAvailability':availability,'supportStatus':status,'strategy':strategy,
                 'requiredCapability':capability or [],'deviationsOrOpenGates':deviations,
                 'nodeValidation':validation,'futureValidation':'Fresh corrected source-pinned component only; not executed',
                 'sourceRef':source})
blob='../native-blob-candidate/v2/source/builtins/web/blob.cpp'
file='../native-blob-candidate/v2/source/builtins/web/file.cpp'
row('globalThis.Blob constructor','Native byte-only vector, synchronous per-part copy; fixed attached unshared backing',
    ['Options/has-get/conversion order, primitive MIME and endings remain partial; shared/detached/RAB excluded; no tested maximum allocation'],
    ['ordinary[0..10]','nodeOnly[0..3,8]'],blob+'::Blob::init/append_value')
row('Blob.prototype.size','Read initialized native vector length',[],['ordinary[0,3,7,9]','receivers'],blob+'::size_get')
row('Blob.prototype.type','Native string slot; printable-ASCII lowercasing',
    ['Primitive number/boolean/Symbol conversion differs from Node22; exact errors/options order unresolved'],
    ['ordinary[6,8,9]','nodeOnly[0,1]','receivers'],blob+'::normalize_type/type_get')
for name,description in [('arrayBuffer','Fresh rooted GC-owned ArrayBuffer and one explicit native copy'),('bytes','Same owned copy, then Uint8Array sharing that fresh output buffer'),('text','Rust UTF8 decoder over immutable owned bytes; checked string-specific allocation and adoption')]:
    row('Blob.prototype.'+name+'()',description,
        ['Promise receiver errors use existing helper; code/text parity unverified','Candidate resolves its result before return; Node22 nonempty settlement queues differ',
         *(['Rust allocator abort remains possible; nonempty UTF16 capacity at least2; JS MaxStringLength gate needs review'] if name=='text' else [])],
        ['ordinary[0..10]','receivers','nodeOnly[10]'],blob+'::'+name+'/data_to_owned_array_buffer')
row('Blob.prototype.slice()','Allocate JS_malloc bytes and transfer to same-family SystemAllocPolicy vector after finite coercions',
    ['No source mutation; full numeric/object coercion and MIME conversion coverage incomplete; no empirical allocation/GC proof'],
    ['ordinary[7,9]','nodeOnly[7]','receivers'],blob+'::slice/create')
row('Blob.prototype.stream()','Existing default ReadableStream/BufReader/StreamTask path unchanged',
    ['Genuine native stream is deferred: not a byte/BYOB stream; cancel no-op; queued owner retained; unchecked task allocation; no post-cancel-enqueue proof'],
    ['Node-only BYOB/cancel[9]; future invalid receivers only'],blob+'::stream and streams/buf-reader.cpp',status='deferred',availability='legacy-path-exists-but-not-admitted-for-reuse')
row('Blob.prototype.stream().getReader({mode:"byob"})','Current source creates a default stream, not a readable byte stream',
    ['BYOB is unavailable on this Blob source; no genuine native reader operation was run'],
    ['Node-only BYOB[9]; native source-kind proof only'],'builtins/web/streams/native-stream-source.cpp::create',status='unavailable',availability='default-stream-source-has-no-BYOB-controller')
row('Blob.prototype[Symbol.toStringTag]','Existing constant Blob tag',[],['Node inventory; ordinary tag uses File inherited chain'],blob+'::properties')
row('globalThis.File constructor','Existing Blob storage prefix plus own FinalizableClassPolicy forwarding cleanup exactly once',
    ['Name conversion lacks well-formed repair; name/lastModified ordering differs; numeric lastModified conversion differs; default clock not enabled by pure gate'],
    ['ordinary[6,9,10]','nodeOnly[4,5,6]'],file+'::File::init/finalize')
row('File.prototype.name','Initialized reserved JS string; guarded native class/Blob storage/name/number fields',
    ['Lone-surrogate name repair differs from Node; broad subclass/realm/Proxy behavior unverified'],['ordinary[6,9]','nodeOnly[4]','receivers'],file+'::name_get/is_instance')
row('File.prototype.lastModified (explicit finite integer)','Stored number from existing ToInt64 conversion',
    ['Node22 preserves fractions, infinities and negative zero and maps NaN to0; candidate numeric domain remains bounded finite integers'],
    ['ordinary[6,9,10]','nodeOnly[5]','receivers'],file+'::read_last_modified/lastModified_get')
row('File default lastModified','Current JS_Now/1000 clock call, not a portable fabricated timestamp',
    ['No native pure-world test; explicit lastModified required in candidate fixture','Future wall-clock selection and snapshot/deployed policy must gate default construction; current P1 bridge/stub is not a live clock guarantee'],
    ['Node-only clock window[6]'],file+'::read_last_modified',status='deferred',capability=['wasi:clocks/wall-clock@0.2.10 (future explicit selection and wiring; not imported by this packet)'])
row('File.prototype[Symbol.toStringTag]','Existing constant File tag',[],['ordinary[9]','Node inventory'],file+'::properties')
row('File inherited Blob methods/accessors','Same Blob method bindings operate on initialized registered File storage',
    ['Each inherited operation retains the corresponding Blob row scope/gates'],['ordinary[6,9,10]'],file+'::init_class and Blob::is_instance')
for name in ['Blob','File']:
    row('node:buffer.'+name+' export binding','Existing explicit finite manifest and deferred function',
        ['Distinct from native global; default/named identity follows current core contract; no constructor promotion'],
        ['Current core manifest/earlier component evidence; future fixture keeps call/new refusal'],
        'builtins/node-compat/buffer-facade.mjs',status='import-only',availability='installed-existing-profile')
    row('node:buffer.'+name+' call/new','Explicit ERR_SM_NODE_UNSUPPORTED refusal',[],
        ['Earlier core refusal gates; future fixture repeats4refusals'],
        'builtins/node-compat/buffer-facade.mjs',status='deferred',availability='installed-explicit-refusal')
for name in ['blob','arrayBuffer','buffer']:
    row('node:stream/consumers.'+name,'Future collect actual part references until iteration completes, then sequential native constructor/copy',
        ['Production module uninstalled; isolated prototype explicitly refuses','Do not pre-copy mutable parts or eagerly coerce objects','Final constructor ordering, bounded coercion/output size, Blob identity and Buffer shared-view contract need implementation/proof'],
        ['Existing 12 Blob/ownership Node groups reused unchanged; no new consumer guest pass'],
        '../node-checks.mjs and ../native-blob-candidate/v2',status='deferred',availability='not-installed; isolated-refusal-prototype-only')
for name in ['text','json']:
    row('node:stream/consumers.'+name,'Reuse existing audited isolated native-TextDecoder facade',
        ['Not installed as production module; this packet changes no semantics','Existing1MiB-byte/string/output and4096-chunk caps remain; no Blob output'],
        ['Prior metadata-v2 component/text oracle evidence reused without rerun'],
        '../metadata-v2/prototype.mjs and component-results.json',status='partial',availability='isolated-component-prototype-only')
for name,inventory in node['inventory'].items():
    for member in inventory['prototypeMembers']:
        if member['keyKind']=='registered-symbol':
            row(name+'.prototype[Symbol.for('+json.dumps(member['registryKey'])+')]','Node inventory observation; native presence/behavior not established',
                ['No delegation/parity claim; inspect/introspection needs its own native namespace/member proof'],
                ['Pinned Node own-property inventory only'],'node-source/internal-'+name.lower()+'.node-v22.14.0.js',availability='unverified')
result={'schemaVersion':1,'node':'v22.14.0','target':'Unlinked native Blob/File owned-copy v2 over current m10; no production export promotion',
        'reflectionOnlyPolicy':'Nonregistry Node symbols are inventory observations, not portable public keys or established native members.',
        'nodeInventory':node['inventory'],'rows':rows,
        'limits':{'nativeBlobBytesChecked':2147483647,'nativeBound':'PTRDIFF_MAX on wasm32; real allocator/memory limits may be lower',
                  'nonemptyTextMinimumWritableUtf16Units':2,'textCapacityArithmetic':'max(maximum,2) <= SIZE_MAX/sizeof(char16_t)',
                  'spiderMonkeyMaxStringCodeUnits':1073741822,'maxStringGuard':'JSAPI string creation enforces it; v2 lacks an explicit before-allocation cap',
                  'existingTextJsonPrototype':{'byteInput':1048576,'stringInputCodeUnits':1048576,'outputCodeUnits':1048576,'chunks':4096},
                  'futureBlobConsumers':'No enforced small cap implemented; choose/review separately before enabling coercing Blob-dependent consumers'},
        'nativeGuestExecuted':False,'publicNodeBufferBlobFilePromoted':False}
(HERE/'api-matrix.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'candidateExecuted':False,'promotion':False}))
