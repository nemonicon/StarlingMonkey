"""Check the retained identity-prework sample without private build trees or hosts."""
import hashlib
import json
from pathlib import Path
import sys

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError("Run with python3 -I -B; optimized assertion removal is unsupported")

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw-records"
INDEX_SHA256 = "3f20c56c698709b61d4207e75409deca0cab43c97dfbcc09c2511b3321e85419"
index_bytes = (RAW / "index.json").read_bytes()
assert hashlib.sha256(index_bytes).hexdigest() == INDEX_SHA256
index = json.loads(index_bytes)
assert index["payloadFiles"] == len(index["files"]) == 208
assert index["payloadBytes"] == sum(r["bytes"] for r in index["files"]) == 5576656
payloads, originals = {}, {}
for row in index["files"]:
    relative = Path(row["path"])
    assert not relative.is_absolute() and all(p not in (".", "..") for p in relative.parts)
    path = RAW / relative
    assert path.resolve() == path and path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
    assert row["path"] not in payloads
    payloads[row["path"]] = data
    original = row["original"]
    assert (original["bytes"], original["sha256"]) == (row["bytes"], row["sha256"])
    key = (original["path"], original["sha256"], original["bytes"])
    assert key not in originals or originals[key] == data
    originals[key] = data
assert sorted(payloads) == sorted(
    str(p.relative_to(RAW)) for p in RAW.rglob("*") if p.is_file() and p != RAW / "index.json"
)


def retained(ref):
    return originals[(ref["path"], ref["sha256"], ref["bytes"])]


arms = {}
for arm, owner in (("cloud", 53303), ("stock", 53776)):
    prefix = "files/" + arm + "/work/client/"
    client = json.loads(payloads[prefix + "result.json"])
    prework = json.loads(payloads[prefix + "prework-result.json"])
    publication = json.loads(payloads[prefix + "publication.json"])
    terminal = json.loads(payloads["files/" + arm + "/owner/terminal.json"])
    assert terminal["pid"] == owner and terminal["rawExitCode"] == 0
    assert not terminal["timeout"] and not terminal["forcedCleanup"]
    assert terminal["parentOwnedGroupGone"] and terminal["allObservedOwnedGroupsGone"]
    assert all(not terminal[k] for k in ("errors", "signals", "interruptedSignals", "remainingObservedPids"))
    assert client["passed"] and client["responseProbeExecuted"] and client["responseCollectionComplete"]
    assert client["collectionErrors"] == client["validationErrors"] == client["errors"] == []
    assert not client["fullOriginalContractExecuted"] and not client["fullNextAccepted"]
    preceding = client["precedingWorkload"]
    assert preceding["executed"] and preceding["collectionComplete"] and preceding["passed"]
    assert json.loads(retained(preceding["result"])) == prework
    assert prework["executed"] and prework["collectionComplete"] and prework["passed"]
    assert prework["collectionFrame"] == dict(httpRecords=24, portableRecords=5, portableChecks=52,
        supplementalRecords=6, supplementalChecks=80, streamChunks=3, allHttpBodiesPublished=True,
        allPortableCollected=True, allSupplementalCollected=True, streamCapturePublished=True)
    assert len(prework["http"]) == 24 and all(r["passed"] for r in prework["http"])
    assert prework["cacheInvalidation"]["before"]["generation"] == 1
    assert prework["cacheInvalidation"]["after"]["generation"] == 2
    assert prework["streaming"] == dict(chunks=3, shellChunk=0, readyChunk=1,
        complete=True, incrementalDeliveryObserved=True)
    for ref in prework["rawFiles"]:
        retained(ref)
    response = client["response"]
    assert response["statusCode"] == 200 and "content-encoding" not in response["headers"]
    assert response["complete"] and response["endObserved"] and not response["abortedObserved"]
    assert client["connection"]["cleanupCompleted"] and client["connection"]["socketCloseObserved"]
    body, copy = retained(response["encodedBody"]), retained(response["decodedBody"])
    assert body == copy == payloads[prefix + "body.raw.bin"] == payloads[prefix + "body.decoded.bin"]
    assert response["identity"]["operation"] == "identity-copy"
    assert not response["identity"]["contentDecodingPerformed"]
    assert publication["complete"] and not publication["errors"]
    assert retained(publication["result"]) == payloads[prefix + "result.json"]
    for value in (preceding["publication"], publication["resultPublication"],
                  response["encodedBodyPublication"], response["decodedBodyPublication"]):
        assert all(value[k] for k in ("complete", "fsynced", "closed")) and not value["errors"]
    arms[arm] = dict(originalOwner=owner, bodyBytes=len(body), bodySHA256=hashlib.sha256(body).hexdigest())

print(json.dumps(dict(state="RETAINED_IDENTITY_PREWORK_SAMPLE_VERIFIED_V1", passed=True,
    payloadFiles=208, payloadBytes=5576656, arms=arms, retainedDataOnly=True,
    freshRuntimeExecuted=False, originalStrictBrowserFailureWaived=False, fullNextAccepted=False)))
