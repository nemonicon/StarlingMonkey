"""Verify one golden saved Chrome-body sample using copied bytes only, never hosts."""
import hashlib
import json
from pathlib import Path
import stat
import sys
from urllib.parse import urlsplit

RAW_INDEX_SHA256 = '44f69415664bfe73a16c320eb8fca3890ea26f2f5df331c8f6bd3ed7e86167e5'
EXPECTED_FILES = 239
EXPECTED_BYTES = 6882196
if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError("Run with python3 -I -B, without assertion optimization")
assert type(RAW_INDEX_SHA256) is str and len(RAW_INDEX_SHA256) == 64, "Unbound raw index"
assert type(EXPECTED_FILES) is int and 0 < EXPECTED_FILES <= 4096, "Unbound file count"
assert type(EXPECTED_BYTES) is int and 0 < EXPECTED_BYTES <= 64 * 1024 * 1024, "Unbound byte count"
RAW = Path(__file__).resolve().parent / "raw-records"


def read_copy(path, limit):
    before = path.lstat()
    assert path.resolve() == path and stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    assert 0 <= before.st_size <= limit
    data = path.read_bytes()
    after = path.lstat()
    fields = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
    assert tuple(getattr(before, k) for k in fields) == tuple(getattr(after, k) for k in fields)
    assert len(data) == after.st_size
    return data


index_bytes = read_copy(RAW / "index.json", 4 * 1024 * 1024)
assert hashlib.sha256(index_bytes).hexdigest() == RAW_INDEX_SHA256
index = json.loads(index_bytes)
assert index["payloadFiles"] == len(index["files"]) == EXPECTED_FILES
assert index["payloadBytes"] == sum(r["bytes"] for r in index["files"]) == EXPECTED_BYTES
assert all(type(r["bytes"]) is int and 0 <= r["bytes"] <= 32 * 1024 * 1024 for r in index["files"])
payloads, originals = {}, {}
for row in index["files"]:
    relative = Path(row["path"])
    assert relative.parts and not relative.is_absolute() and relative.as_posix() == row["path"]
    assert all(p not in (".", "..") for p in relative.parts) and row["path"] != "index.json"
    data = read_copy(RAW / relative, row["bytes"])
    assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
    assert row["path"] not in payloads
    payloads[row["path"]] = data
    original = row["original"]  # Dictionary key only: never open the original path.
    assert (original["bytes"], original["sha256"]) == (row["bytes"], row["sha256"])
    key = (original["path"], original["sha256"], original["bytes"])
    assert key not in originals or originals[key] == data
    originals[key] = data
members = list(RAW.rglob("*"))
assert all(not p.is_symlink() and (p.is_dir() or p.is_file()) for p in members)
assert sorted(payloads) == sorted(p.relative_to(RAW).as_posix() for p in members if p.is_file() and p != RAW / "index.json")


def retained(ref):
    return originals[(ref["path"], ref["sha256"], ref["bytes"])]


def durable(evidence, ref):
    assert all(evidence[k] is True for k in ("complete", "fsynced", "closed"))
    assert evidence["errors"] == [] and evidence["fileBytes"] == ref["bytes"] and evidence["sha256"] == ref["sha256"]
    retained(ref)


arms = {}
allowed = {"accept", "content-type", "next-action", "next-router-state-tree", "accept-language"}
managed = {"host", "connection", "content-length", "origin", "referer", "accept-encoding", "user-agent",
    "sec-ch-ua-platform", "sec-ch-ua", "sec-ch-ua-mobile", "sec-fetch-site", "sec-fetch-mode", "sec-fetch-dest"}
for arm, owner in (("cloud", 59256), ("stock", 59943)):
    prefix = "files/" + arm + "/work/client/"
    client, prework, publication = (json.loads(payloads[prefix + name]) for name in ("result.json", "prework-result.json", "publication.json"))
    terminal = json.loads(payloads["files/" + arm + "/owner/terminal.json"])
    assert terminal["pid"] == owner and terminal["rawExitCode"] == 0
    assert not terminal["timeout"] and not terminal["forcedCleanup"]
    assert terminal["parentOwnedGroupGone"] and terminal["allObservedOwnedGroupsGone"]
    assert all(not terminal[k] for k in ("errors", "signals", "interruptedSignals", "remainingObservedPids"))
    assert client["suite"] == "NEXT_RSC_BROWSER_BODY_PREWORK_CLIENT_V1" and client["controlOnly"] is True
    assert all(client[k] is True for k in ("passed", "responseProbeExecuted", "collectionComplete", "browserClosed", "requestFidelityVerified"))
    assert all(client[k] == [] for k in ("collectionErrors", "validationErrors", "errors", "pageerrors", "consoleerrors", "failedrequests"))
    assert client["fullOriginalContractExecuted"] is False and client["fullNextAccepted"] is False
    preceding = client["precedingWorkload"]
    assert all(preceding[k] is True for k in ("executed", "collectionComplete", "passed"))
    assert json.loads(retained(preceding["result"])) == prework
    durable(preceding["publication"], preceding["result"])
    assert prework["passed"] and prework["collectionComplete"] and prework["errors"] == prework["transportErrors"] == []
    assert prework["fullOriginalContractExecuted"] is False and prework["browserExecuted"] is False and prework["fullNextAccepted"] is False
    assert prework["collectionFrame"] == dict(httpRecords=24, portableRecords=5, portableChecks=52, supplementalRecords=6, supplementalChecks=80,
        streamChunks=3, allHttpBodiesPublished=True, allPortableCollected=True, allSupplementalCollected=True, streamCapturePublished=True)
    assert len(prework["http"]) == 24 and all(r["passed"] for r in prework["http"])
    assert prework["cacheInvalidation"]["before"]["generation"] == 1 and prework["cacheInvalidation"]["after"]["generation"] == 2
    assert prework["streaming"] == dict(chunks=3, shellChunk=0, readyChunk=1, complete=True, incrementalDeliveryObserved=True)
    for ref in prework["rawFiles"]:
        retained(ref)
    fetch, read, response = client["browserFetch"], client["bodyRead"], client["browserFetch"]["response"]
    assert fetch["attempted"] and fetch["settled"] and fetch["outcome"] == read["outcome"] == "fulfilled"
    assert read["attempted"] and read["bytes"] == 2963 and read["postReadLimitBytes"] == 4194304 and read["allocationPrebounded"] is False
    assert response["status"] == 200 and response["redirected"] is False
    headers = {r["name"].lower(): r["value"] for r in response["headers"]}
    assert "content-encoding" not in headers and headers["content-type"].startswith("text/x-component")
    assert headers["x-action-redirect"] == "/action-result?value=browser-action;push"
    body = retained(client["browserBody"])
    assert body == payloads[prefix + "browser-body.bin"] and len(body) == 2963 and b"NEXT_ACTION_RESULT" in body and b"browser-action" in body
    durable(client["browserBodyPublication"], client["browserBody"])
    capture = json.loads(retained(client["requestCapture"]))
    request, events = client["request"], client["cdpEvents"]
    assert capture["method"] == request["method"] == "POST" and capture["path"] == request["path"] == "/actions"
    assert request["url"] == client["origin"] + "/actions"
    request_body = retained(capture["body"])
    assert len(request_body) == 391 and request["body"] == capture["body"] and request["bodyReserialized"] is False
    retained(capture["headerEvidence"])
    posts = [r for r in events if r["event"] == "Network.requestWillBeSent" and r["payload"].get("request", {}).get("method") == "POST" and r["payload"]["request"]["url"] == request["url"]]
    assert len(posts) == 1 and posts[0]["payload"]["hasUserGesture"] is True
    selected_id = posts[0]["payload"]["requestId"]
    req_extra = [r for r in events if r["event"] == "Network.requestWillBeSentExtraInfo" and r["payload"]["requestId"] == selected_id]
    res_extra = [r for r in events if r["event"] == "Network.responseReceivedExtraInfo" and r["payload"]["requestId"] == selected_id]
    endings = [r for r in events if r["event"] in ("Network.loadingFinished", "Network.loadingFailed") and r["payload"]["requestId"] == selected_id]
    assert len(req_extra) == len(res_extra) == len(endings) == 1 and endings[0]["event"] == "Network.loadingFinished"
    assert request["extraInfo"] == dict(request=req_extra[0], response=res_extra[0])
    assert client["networkTerminal"] == dict(kind="loadingFinished", requestId=selected_id, payload=endings[0]["payload"])
    actual = {k.lower(): v for k, v in req_extra[0]["payload"]["headers"].items()}
    captured = {r["name"].lower(): r["value"] for r in capture["headers"]}
    assert len(capture["headers"]) == len(captured) == 19 and set(captured) == allowed | managed | {"x-next-public-request-correlation"}
    assert len(request["scriptHeaders"]) == 5 and {r["name"]: r["value"] for r in request["scriptHeaders"]} == {k: captured[k] for k in allowed}
    assert len(request["scriptHeaderObservedMatches"]) == 5 and all(r["matches"] is True and actual[r["name"]] == r["observed"] == r["expected"] == captured[r["name"]] for r in request["scriptHeaderObservedMatches"])
    omissions = request["browserManagedOmissions"]
    assert len(omissions) == 13 and {r["name"] for r in omissions} == managed and "x-next-public-request-correlation" not in actual
    for r in omissions:
        expected = {"host": urlsplit(client["origin"]).netloc, "origin": client["origin"], "referer": request["url"]}.get(r["name"], captured[r["name"]])
        assert r["scriptOverrideAttempted"] is False and r["capturedValue"] == captured[r["name"]]
        assert r["matchesCapturedWithOriginMapping"] is True and r["observedValue"] == actual[r["name"]] == expected
    selected = [r for r in request["requests"] if r["role"] == "selected-post"]
    assert len(selected) == 1 and selected[0]["body"] == dict(bytes=391, sha256=capture["body"]["sha256"])
    assert not any(r["role"] == "unexpected" and r["url"].startswith(("http:", "https:")) for r in request["requests"])
    synthetic = client["syntheticDocument"]
    assert synthetic["fulfilled"] == synthetic["routeTimes"] == 1 and synthetic["unrouteCompletedBeforeFetch"] is True
    assert synthetic["observedLocation"] == dict(origin=client["origin"], href=request["url"], scripts=0)
    assert publication["state"] == "RSC_HTTP_RESPONSE_CLIENT_PUBLICATION_COMPLETE_V1" and publication["complete"] is True and publication["errors"] == []
    assert retained(publication["result"]) == payloads[prefix + "result.json"]
    assert publication["browserBody"] == client["browserBody"] and publication["browserBodyPublication"] == client["browserBodyPublication"]
    assert all(publication[k] is True for k in ("collectionComplete", "browserClosed", "responseProbeExecuted"))
    durable(publication["resultPublication"], publication["result"])
    arms[arm] = dict(originalOwner=owner, browserBodyBytes=len(body), browserBodySHA256=hashlib.sha256(body).hexdigest())

print(json.dumps(dict(state="RETAINED_BROWSER_BODY_PREWORK_GOLDEN_SAMPLE_VERIFIED_V1", passed=True,
    payloadFiles=EXPECTED_FILES, payloadBytes=EXPECTED_BYTES, arms=arms, retainedDataOnly=True,
    freshRuntimeExecuted=False, originalStrictBrowserFailureWaived=False, fullNextAccepted=False)))
