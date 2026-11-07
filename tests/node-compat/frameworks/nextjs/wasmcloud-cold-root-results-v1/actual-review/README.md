# Cold V1: readiness failure preserved

The original attempt **failed raw1**. All eight responses were complete HTTP404
with empty bodies; all eight contracts failed. Config-show exited0. The dev
process exited130 following the requested SIGINT, without forced cleanup. The
original600s owner reports clean groups and protected inputs unchanged. None of
this demonstrates a successful Next route or selected-interface instantiation.

The complete dev log records `HTTP server listening` before `development session
started, building and deploying component...`, followed by `failed to route
incoming request err=no workload registered`. No positive workload-registration
marker appears. The harness admitted requests on TCP availability and sent all
eight before a ready workload was established. It then stopped dev while build/
deployment was in progress. The cold Source/result and all raw failures remain
unchanged; no HTTP readiness retries or workload rerun were performed here.

The reviewer previously approved Sourceca875's TCP-only gate. That Source review
missed the need for a positive workload-registration barrier. This review
qualifies that approval; it does not repair or relabel the failed attempt.
The selected component55f05/engine462/metadata726d remain the same separately
reviewed artifacts. Their thirteen standard0.2.10 imports are artifact evidence,
not evidence that this wasmCloud attempt instantiated or routed the component.

All eight response bodies, chunk records, contract failures, both CLI streams,
effective/private configuration, Root authority and original monitor records are
retained byte for byte. No stream shell/ready marker was observed. Captured bytes
are fetch-decoded bodies; no raw compressed-wire hash is claimed.

Current independent before/final readback verified both the original and copied
app trees: 2218 files/48,808,299 bytes each, exact source inventory identities,
distinct copied inodes, files0444/directories0555. The writable nested cache is
separate. Physical modes are not proof of read-only WASI descriptor rights.
The actual whole Source/world family has17 files including its index,9
directories and8 fixed WIT files; its content and current identities match.
Private XDG/empty user config and explicit workload environment remain recorded.

Run `python3 -B -I check.py` for the inert portable reader. `--current` additionally
rehashes126 selected artifact/Source descriptors, both app trees and world
identities while available. `data.tar.gz` losslessly retains101 files (2,053,425
expanded bytes, about378KB compressed). It copies no component, engine, wash/Node
binary, SDK, application payload or recursive build ancestry. App inventories and
direct build descriptors remain explicit. This is finite current protection,
not an all-time or recursive SDK attestation.

The reviewer authored earlier ALS/constructor tooling; B authored the cold
Source and Root executed this attempt. No target, CLI, network, compiler,
constructor, engine or guest operation was rerun by the reviewer. A reader-only
import-order assumption was corrected before publication and is recorded in
`preparation.json`; original evidence was unchanged.

Fresh-Store behavior remains a source-derived wasmCloud expectation, not an
observed Next identity. There is no cache-generation/browser/retained24+2,
full-Next, cold-runtime-success or production-adoption claim from this attempt.
