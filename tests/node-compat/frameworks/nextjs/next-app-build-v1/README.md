# Isolated Next application builder — Source only

This CLI extracts the real fixture's app-build and standalone-packaging path
from `../run.mjs`. It excludes the historical Node/bundler corpus, servers,
HTTP/browser checks and native/component operations. **The build path has not
been executed.** No npm, Node, Next, network, compiler or guest ran during this
Source preparation. A passing Source test is not a real app-build result.

Default invocation or `--plan` reads and validates the committed fixture and
prints the command/environment/packaging plan without creating an output:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/next-app-build-v1/build.py
```

Without tool arguments it prints explicit required tool/output placeholders.
To inspect a concrete future invocation, provide canonical real paths:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/next-app-build-v1/build.py --plan \
  --node /REAL/NODE22/bin/node --npm-cli /REAL/npm/bin/npm-cli.js \
  --output /private/tmp/next-app-FRESH
```

Removing `--plan` from that complete command is the **future build action**.
It requires explicit existing Node/npm inputs and a fresh absolute output
outside the checkout. Existing roots, aliases, symlink ancestors and prior
outputs refuse. Node must actually report `v22.14.0`; npm must report the
version in its selected package manifest before installation. No package
installation fallback or retries are present. This does not acquire Node/npm;
the original workstation's historical npm directory is currently absent.

The existing mechanism is preserved:

1. Copy all29 pinned fixture files (41,174 bytes) into owned `application`.
2. Run selected Node on npm's actual `npm-cli.js ci --ignore-scripts --no-audit
   --no-fund`, bounded600 seconds. Inspect installed Next16.4.5 and
   React/ReactDOM19.3.1 plus unchanged package/lock bytes before invoking Next.
3. Run selected Node on the installed `next/dist/bin/next build --webpack`,
   bounded900 seconds. The unchanged config selects standalone output and
   one build CPU.
4. Copy generated `.next/static` and `public` exclusively into the real
   `.next/standalone` tree. Require the genuinely traced `fixtures/message.txt`
   to match; a missing traced file is a failure, never silently fabricated.
5. Record the actual standalone inventory, generated BUILD_ID and real
   server-reference manifest/action IDs. These are fresh hashes, modes and
   filesystem identities, never retargeted historical2218-file records.

Each future phase uses the unchanged original0af monitor and preserves complete
argv, stdout/stderr, started/owned/terminal records. Node/npm version probes
have120-second bounds; original bounded cleanup is additional. Mandatory empty
errors/signals/interruptedSignals/remaining-PID arrays, no timeout/forced cleanup
and all owned groups gone are required. npm/Next warnings remain raw evidence;
version probes require empty stderr. A failed command or packaging/protection
gate preserves partial output and a failed result, rather than claiming a build
from file existence. No overall wall-time or continuously sampled disk floor is
claimed by this app-only CLI.

HOME/USER/LOGNAME are inherited. PATH selects the explicit Node directory;
ambient NODE_OPTIONS/compile-cache settings are excluded. npm cache, TMPDIR and
empty explicit user/global npm config files live under the fresh owned output.
The original fixture, selected Node and npm package tree are authenticated before
actions and rechecked between phases/finally. npm permits only recorded safe
relative internal links; fixture/runtime output links refuse. This pins selected
tool inputs, not all operating-system libraries. Initial owned-directory and
plan-write errors can precede the protected try and yield only CLI failure;
no command or shared-input mutation has begun in that interval.

The57 inert Source tests cover genuine fixture membership, original argv/caps,
private environment, mandatory terminal fields, tool-version refusal, copies,
overwrite/alias refusals, synthetic static/public/tracing packaging and dynamic
identifier handling, plus the real read-only plan CLI. Synthetic packaging data
is explicitly not a fake framework build or runtime acceptance. The first test
omitted the synthetic standalone `.next` parent; its original code and failure
note remain under `preparation-history/attempt1`. Corrected tests pass:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/next-app-build-v1/test-source.py
```

This closes Source isolation of the app-build step. Actual npm/Next execution,
clean-machine installation, generated-input review, component construction,
full24HTTP/cache/stream/2browser regression and production promotion remain
separate. See the [reproducibility plan](../../../../../docs/node-compat/nextjs-reproducibility-plan.md).
