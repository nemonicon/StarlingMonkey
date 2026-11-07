# Next request isolation — prepared, real run capacity-held

The reviewed V8 client adds six request-isolation/body/recovery cases through
the unchanged Next application. It retains the original24HTTP/cache/stream/
2browser contract and requires both gates. Component1c3108d2, engine462 and the
genuine2,181-file app remain exact; the guest world stays at thirteen standard
WASI0.2.10 interfaces. This is a new test, with no new guest implementation.

Source47c821e8 passes independent review,21 inert checks and62 local fake-server
checks across24 outcomes. Those tests include retaining partial response bytes
and the original error. They are not real Next or guest results. Four initial
client requests overlap; the test makes no same-Store/private-resource claim.
The Source README records the existing module-local cache-counter limitation;
the original cache assertion remains required.

Root's full guard changes only its V7→V8 actor selector. The late authority
changes Source/plan/runId/scope prose; every native, constructor, component and
world field stays exact. The reusable CLI preserves the reviewed fresh-path,
hash,1GiB start and owned-runner logic. All three pass independent review.

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/run-next-request-regression.py --run-id next-check-001
```

Choose a fresh lowercase ID of at most48 characters on each run. `--prepare-only` writes a
request without starting Wasmtime or a browser. Existing private artifacts are
required; the command does not rebuild them. Each result is preserved, with no
automatic retry, failure filtering or overwrite.

Actual preparation exits0 and retains requested9ebfa4. The first actual launch
attempt exits2 at the1GiB floor, reporting761,180,160 free bytes. It creates no
runtime request, Wasmtime output, original monitor or world-guard receipt. The
seven absent paths, original request bytes and complete tool outputs are in
`preparation-and-capacity-hold.json` and adjacent files. These are pre-action
observations; all six new real Next cases remain **unexecuted**. Earlier actual
24+2 successes and the failed all-six reliability cohort remain unchanged.

The matched pinned-Node path is also prepared. SourceV6/bccce053 forks the
normal V4 control and imports the **same V8 helper**; it preserves normal CDP,
the original24/cache/stream/browser gates and300s owner. It does not select the
separate CDP-off diagnostic. Source29 wiring/15 namespace checks and independent
Source/request/CLI reviews pass. Its actual `--prepare-only` exits0, writes a
0600 request in the owned0700 directory, and creates no server/monitor outputs.
`stock-preparation.json` retains exact request6eb140fa and original stdout.
Preparation observes770,953,216 bytes and deliberately skips the launch gate;
no stock launch is attempted and no real six-case differential has run.

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/run-next-request-control.py --run-id next-check-001
```

Each arm must pass its own1GiB launch gate. Run each once in a fresh namespace
and preserve every failure; these commands do not launch an automatic cohort
or replace the earlier failed reliability gate. A future actual result must
separately report the original contract and six-case validation.
