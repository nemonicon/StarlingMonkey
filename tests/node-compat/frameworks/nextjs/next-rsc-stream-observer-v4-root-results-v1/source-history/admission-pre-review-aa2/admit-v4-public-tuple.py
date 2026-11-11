#!/usr/bin/env python3
"""Finite saved-DATA admission. No targets, imports of project code, or identity claim."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

MARKER = "NEXT_STANDARD_HANDLER_RETURN_OBSERVER_V4"
HEADER = "x-next-public-request-correlation"
FIELDS = ["marker", "version", "event", "method", "path", "pathStatus",
          "snapshotStatus", "corrState", "corrCount", "corr"]
COMPOSITION = "COORDINATED_NEXT_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_DATA_REVIEW_PASSED_V1"
COMPOSITION_SHA = "730c2698578692e35789918930d6be1cf8fb837a4e5362bcef5b802919795c2f"
PROTOCOL_SHA = "ba27dc3f03b49520e09d73f41a7edaf66a96d61101bbe3acbc5a178be65fa825"
PROOFS = ["rawChildBytesVerified", "siblingDefiningInstancesVerified",
          "sharedNominalResourceAliasesVerified", "fieldsNominalResourceAliasesVerified",
          "metadataGetterCanonicalOptionsVerified", "synchronousLiftLowerWithInnerPostReturnVerified",
          "innerExplicitPostReturnPreserved", "observerManualPostReturnAbsent",
          "internalIncomingHandlerImportComposedAway", "finalInputsPreserved"]
CAPS = {"stdout": 8 << 20, "browserResult": 8 << 20, "publicManifest": 4096,
        "actionManifest": 1 << 20, "compositionReview": 1 << 20, "requestBody": 65536,
        "netlog": 20 << 20}


class Refusal(Exception):
    pass


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def pairs(values):
    out = {}
    for key, value in values:
        need(key not in out, "duplicate-json-key")
        out[key] = value
    return out


def decode_json(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite-json")))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def hex64(value):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value) is not None


def b64(value):
    need(isinstance(value, str) and len(value) <= 90000, "request-base64-shape")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, TypeError):
        raise Refusal("request-base64-invalid")
    need(base64.b64encode(raw).decode("ascii") == value, "request-base64-noncanonical")
    return raw


def headers(value):
    need(isinstance(value, dict), "header-map-shape")
    out = {}
    for name, item in value.items():
        need(isinstance(name, str) and isinstance(item, str), "header-type")
        name = name.lower()
        need(name not in out, "duplicate-casefolded-header")
        out[name] = item
    return out


def publication(value, raw):
    need(isinstance(value, dict), "request-publication-missing")
    need(all(value.get(k) is True for k in ["complete", "fsynced", "closed"])
         and type(value.get("fileBytes")) is int and value["fileBytes"] == len(raw)
         and value.get("sha256") == digest(raw) and value.get("errors") == [],
         "request-publication-incomplete")


def multipart(raw, content_type, action):
    match = re.fullmatch(r"multipart/form-data; boundary=([A-Za-z0-9'()+_,./:=?-]{1,70})", content_type)
    need(match is not None, "multipart-content-type")
    boundary = match[1].encode("ascii")
    chunks = raw.split(b"--" + boundary)
    need(len(chunks) == 5 and chunks[0] == b"" and chunks[-1] == b"--\r\n", "multipart-framing")
    parts = {}
    for part in chunks[1:-1]:
        match = re.fullmatch(br'\r\nContent-Disposition: form-data; name="([^"\r\n]+)"\r\n\r\n(.*?)\r\n', part, re.S)
        need(match is not None, "multipart-part-shape")
        name, value = match[1].decode("ascii"), match[2].decode("utf-8")
        need(name not in parts, "multipart-duplicate-part")
        parts[name] = value
    need(parts == {"_1_$ACTION_ID_" + action: "", "_1_value": "browser-action", "0": '["$K1"]'},
         "multipart-semantic-parts")
    return {"boundary": boundary.decode(), "orderObserved": list(parts),
            "boundarySubstitutionAllowed": True, "wireEqualityClaimed": False}


def netlog_evidence(m, browser, pw, origin, nonce, raw):
    meta, log = browser.get("netlog", {}), m["netlog"]
    need(meta.get("file") == m["refs"]["netlog"] and meta.get("completeJson") is True
         and meta.get("fsynced") is True and meta.get("errors") == [], "netlog-publication")
    types, events = log["constants"]["logEventTypes"], log["events"]
    need(isinstance(events, list) and len(events) <= 200000, "netlog-event-cap")
    sends = []
    for index, event in enumerate(events):
        params = event.get("params", {})
        if event.get("type") != types["HTTP_TRANSACTION_SEND_REQUEST_HEADERS"] or params.get("line") != "POST /actions HTTP/1.1\r\n":
            continue
        lines = params.get("headers")
        need(isinstance(lines, list) and len(lines) <= 128, "netlog-header-shape")
        parsed = {}
        for line in lines:
            need(isinstance(line, str) and ":" in line, "netlog-header-shape")
            name, value = line.split(":", 1)
            need(name.lower() not in parsed, "netlog-duplicate-header")
            parsed[name.lower()] = value.strip(" ")
        if parsed.get(HEADER) == nonce:
            sends.append((index, event, parsed))
    need(len(sends) == 1, "netlog-public-post-cardinality")
    index, send, actual = sends[0]
    need(all(actual.get(k) == v for k, v in pw.items()), "netlog-playwright-header-mismatch")
    need(actual.get("origin") == origin and actual.get("host") == origin.removeprefix("http://")
         and actual.get("content-length") == str(len(raw)), "netlog-origin-or-length")
    source = send.get("source")
    need(isinstance(source, dict) and set(source) == {"id", "type", "start_time"}
         and type(source["id"]) is int and type(source["type"]) is int
         and isinstance(source["start_time"], str), "netlog-source-shape")
    jobs = [e for e in events if e.get("source") == source and e.get("type") == types["URL_REQUEST_START_JOB"]
            and e.get("params", {}).get("method") == "POST" and e["params"].get("url") == origin + "/actions"]
    bodies = [e for e in events if e.get("source") == source and e.get("type") == types["HTTP_TRANSACTION_SEND_REQUEST_BODY"]]
    need(len(jobs) == 1 and len(bodies) == 1 and type(bodies[0].get("params", {}).get("length")) is int
         and bodies[0]["params"]["length"] == len(raw), "netlog-request-job-or-body-cardinality")
    return {"retainedSendEventIndex": index, "localSourceDescriptiveOnly": source,
            "retainedPublicPostCardinality": 1, "historyCompleteProved": False,
            "wireBytesOrCrossProtocolIdentityProved": False}


def browser_evidence(m):
    browser, manifest, actions = m["browserResult"], m["publicManifest"], m["actionManifest"]
    origin = manifest.get("origin")
    need(isinstance(origin, str) and re.fullmatch(r"http://127\.0\.0\.1:[1-9][0-9]{0,4}", origin), "public-origin")
    need(int(origin.rsplit(":", 1)[1]) <= 65535 and type(manifest.get("schemaVersion")) is int
         and manifest["schemaVersion"] == 1, "public-origin-or-schema")
    nonces = manifest.get("nonceByTest", {})
    nonce = nonces.get("server-action")
    need(manifest.get("headerName") == HEADER and hex64(nonce), "declared-public-context")
    need(all(hex64(v) for v in nonces.values()) and len(set(nonces.values())) == len(nonces), "public-nonce-ambiguity")
    need(browser.get("origin") == origin and browser.get("browserClosed") is True, "browser-origin-or-close")
    need(browser.get("publicRequestCorrelation", {}).get("manifest") == manifest, "browser-public-manifest-mismatch")
    selected = [key for key, value in actions.get("node", {}).items()
                if value.get("exportedName") == "submitFixture"
                and value.get("filename") == "app/actions/actions.js"
                and "app/actions/page" in value.get("workers", {})]
    need(len(selected) == 1, "action-manifest-ambiguity")
    action = selected[0]
    need(isinstance(action, str) and re.fullmatch("[0-9a-f]{42}", action), "action-id-shape")
    rs = browser.get("resourceStreamObservation", {})
    need(rs.get("finalized") is True and rs.get("collectionComplete") is True and rs.get("errors") == [],
         "browser-observer-collection-uncertain")
    need(rs.get("actualActionManifest") == m["refs"]["actionManifest"] and rs.get("requiredActionId") == action,
         "browser-action-manifest-mismatch")
    observations = rs.get("observations")
    need(isinstance(observations, list) and len(observations) == 1, "browser-observation-cardinality")
    admission = observations[0].get("admission", {})
    need(admission.get("passed") is True and admission.get("errors") == []
         and admission.get("CDPBodyMatchedPlaywright") is True
         and admission.get("publicContextVerified") is True and admission.get("currentActionId") == action,
         "browser-request-admission-unavailable")
    raw = m["requestBody"]
    need(admission.get("actualRequestBody") == m["refs"]["requestBody"], "request-body-ref-mismatch")
    publication(admission.get("actualRequestBodyPublication"), raw)
    url = origin + "/actions"
    posts = browser.get("actionPosts")
    need(isinstance(posts, list) and len(posts) == 1 and posts[0].get("url") == url, "playwright-post-cardinality")
    post = posts[0]
    need(type(post.get("bytes")) is int and post["bytes"] == len(raw) and b64(post.get("bodyBase64")) == raw,
         "playwright-request-body-mismatch")
    pw = headers(post.get("headers"))
    need(pw.get(HEADER) == nonce and pw.get("next-action") == action, "playwright-public-action-header")
    events = browser.get("cdpEvents")
    need(isinstance(events, list) and len(events) <= 65536, "cdp-events-shape")
    scoped = [e for e in events if e.get("test") == "server-action"]
    starts = [e["payload"] for e in scoped if e.get("event") == "Network.requestWillBeSent"
              and e.get("payload", {}).get("request", {}).get("url") == url
              and e["payload"]["request"].get("method") == "POST"]
    need(len(starts) == 1, "cdp-post-cardinality")
    start = starts[0]
    request_id = start.get("requestId")
    need(isinstance(request_id, str) and admission.get("cdpRequestId") == request_id, "cdp-admission-id")
    reuse = [e for e in scoped if e.get("event") == "Network.requestWillBeSent"
             and e.get("payload", {}).get("requestId") == request_id]
    need(len(reuse) == 1 and "redirectResponse" not in start, "cdp-id-reused-or-redirected")
    request = start["request"]
    need(isinstance(request.get("postData"), str) and request["postData"].encode("utf-8") == raw, "cdp-request-body-mismatch")
    entries = request.get("postDataEntries")
    need(isinstance(entries, list) and 0 < len(entries) <= 16
         and b"".join(b64(x.get("bytes")) for x in entries) == raw, "cdp-request-entries-mismatch")
    extra = [e["payload"] for e in scoped if e.get("event") == "Network.requestWillBeSentExtraInfo"
             and e.get("payload", {}).get("requestId") == request_id]
    need(len(extra) == 1, "cdp-extra-info-cardinality")
    cdph, extrah = headers(request.get("headers")), headers(extra[0].get("headers"))
    for h in [cdph, extrah]:
        need(all(h.get(k) == pw.get(k) for k in [HEADER, "next-action", "content-type"]), "request-header-mismatch")
    need(extrah.get("origin") == origin and extrah.get("host") == origin.removeprefix("http://")
         and extrah.get("referer") == url and extrah.get("content-length") == str(len(raw)), "request-origin-or-length")
    parts = multipart(raw, pw.get("content-type", ""), action)
    netlog = netlog_evidence(m, browser, pw, origin, nonce, raw)
    return {"method": "POST", "path": "/actions", "corr": nonce, "corrState": "valid", "corrCount": 1,
            "actionId": action, "requestBytes": len(raw), "requestSHA256": digest(raw),
            "CDPRequestIdDescriptiveOnly": request_id, "multipart": parts, "netlog": netlog,
            "declaredNonces": list(nonces.values())}


def records(raw):
    need(isinstance(raw, bytes) and len(raw) <= CAPS["stdout"], "stdout-cap-or-type")
    text = raw.decode("utf-8")
    rows, faults = [], []
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        if "NEXT_STANDARD_HANDLER_RETURN_OBSERVER_" not in line:
            continue
        try:
            need(MARKER in line, "unexpected-observer-version")
            need(line.endswith("\n") and len(line.encode()) <= 512, "observer-record-framing-or-cap")
            row = decode_json(line.encode())
            need(isinstance(row, dict) and row.get("marker") == MARKER
                 and type(row.get("version")) is int and row["version"] == 4, "observer-schema")
            need(row.get("event") != "record-limit", "observer-record-limit")
            need(list(row) == FIELDS and row.get("event") == "inner-handler-import-returned", "observer-schema")
            need(row["snapshotStatus"] == "success", "unknown-getter-or-snapshot")
            need(row["method"] in ["GET", "POST", "unknown"], "observer-method")
            need((row["pathStatus"] == "present-target" and row["path"] in ["/actions", "/action-result"])
                 or (row["pathStatus"] in ["present-other", "absent"] and row["path"] is None), "observer-path-status")
            state, count, corr = row["corrState"], row["corrCount"], row["corr"]
            need(type(count) is int and ((state == "missing" and count == 0 and corr is None)
                 or (state == "valid" and count == 1 and hex64(corr))
                 or (state == "invalid" and count == 1 and corr is None)
                 or (state == "duplicate" and count == 2 and corr is None)), "observer-correlation-schema")
            rows.append({"line": number, "record": row})
        except (Refusal, ValueError, TypeError) as error:
            faults.append({"line": number, "code": str(error) if isinstance(error, Refusal) else "malformed-observer-json"})
    need(len(rows) <= 65536, "observer-total-record-cap")
    return rows, faults


def evaluate(m):
    result = {"schemaVersion": 1, "state": "V4_PUBLIC_TUPLE_NOT_ADMITTED_V1",
              "outerPublicTupleWitnessAdmitted": False, "prospectivePublicTupleJoinAdmitted": False,
              "reasons": [], "recordFaults": [], "targetRows": [], "excludedPresentOtherRows": [],
              "distinctKnownRows": [], "blockingRows": [], "sourceProvenance": m.get("refs", {}),
              "physicalIdentityProved": False, "crossLaneSequenceJoinPerformed": False,
              "silentProducerFailuresUniversallyExcluded": False, "oldV3JoinUpgraded": False,
              "HTTPOrReactEOFProved": False, "fullNextAccepted": False}
    try:
        comp, capture = m["compositionReview"], m["captureEvidence"]
        need(m["refs"]["compositionReview"].get("sha256") == COMPOSITION_SHA
             and comp.get("state") == COMPOSITION and comp.get("verifiedPassed") is True
             and comp.get("verifiedDataReviewPassed") is True and all(comp.get(k) is True for k in PROOFS)
             and comp.get("observerProtocol", {}).get("sha256") == PROTOCOL_SHA, "composition-prerequisite")
        need(type(capture.get("schemaVersion")) is int and capture["schemaVersion"] == 1
             and capture.get("state") == "V4_CLOSED_CAPTURE_ASSESSMENT_V1"
             and isinstance(capture.get("provenance"), list) and len(capture["provenance"]) > 0, "capture-assessment-missing")
        need(capture.get("stdout") == m["refs"]["stdout"] and capture.get("servedEnvelope") == comp.get("envelope"), "capture-artifact-mismatch")
        need(all(capture.get(k) is True for k in ["finalized", "complete", "childStopped", "eofObserved", "fsynced", "closed", "allObservedBytesRetained"])
             and all(capture.get(k) is False for k in ["overflow", "unretainedTail"])
             and capture.get("captureErrors") == [], "capture-incomplete-or-lost")
        need(capture.get("originalOwnerQuiescent") is True and capture.get("originalOwnerClean") is True
             and type(capture.get("originalOwnerRawExitCode")) is int and capture["originalOwnerRawExitCode"] in [0, 1],
             "original-owner-not-clean-quiescent")
        need(capture.get("outcomeCoverage") in ["declared-sample-covered", "observed-only", "unknown"]
             and isinstance(capture.get("unknownGetterOrUnobserved"), list)
             and isinstance(capture.get("captureAmbiguities"), list), "capture-outcome-assessment-missing")
        target = browser_evidence(m)
        result["target"] = target
        rows, faults = records(m["stdout"])
        result["ordinaryRecordCount"], result["recordFaults"] = len(rows), faults
        for item in rows:
            row = item["record"]
            if row["method"] == "unknown" or row["pathStatus"] == "absent":
                result["blockingRows"].append({**item, "reason": "unknown-method-or-absent-path"})
            elif row["pathStatus"] == "present-other":
                result["excludedPresentOtherRows"].append(item)
            elif row["method"] == "GET" or row["corrState"] == "missing":
                result["distinctKnownRows"].append(item)
            elif row["path"] != "/actions":
                result["blockingRows"].append({**item, "reason": "other-target-literal-POST-conservative-blocker"})
            elif row["corrState"] == "valid" and row["corr"] == target["corr"]:
                result["targetRows"].append(item)
            elif row["corrState"] == "valid" and row["corr"] in target["declaredNonces"]:
                result["distinctKnownRows"].append(item)
            else:
                result["blockingRows"].append({**item, "reason": "competing-target-correlation"})
        result["outerPublicTupleWitnessAdmitted"] = not faults and len(result["targetRows"]) == 1
        if faults:
            result["reasons"].append("malformed-limited-or-wrong-version-record")
        if len(result["targetRows"]) != 1:
            result["reasons"].append("target-public-tuple-cardinality")
        if result["blockingRows"]:
            result["reasons"].append("competing-or-unknown-records")
        if capture["unknownGetterOrUnobserved"] or capture["captureAmbiguities"]:
            result["reasons"].append("getter-unobserved-or-capture-blockers")
        if capture["outcomeCoverage"] != "declared-sample-covered":
            result["reasons"].append("outcome-coverage-not-established")
        result["captureAssessmentDelegation"] = capture
        result["prospectivePublicTupleJoinAdmitted"] = result["outerPublicTupleWitnessAdmitted"] and not result["reasons"]
        if result["prospectivePublicTupleJoinAdmitted"]:
            result["state"] = "V4_DECLARED_SAMPLE_PUBLIC_TUPLE_JOIN_ADMITTED_V1"
        elif result["outerPublicTupleWitnessAdmitted"]:
            result["state"] = "V4_PUBLIC_TUPLE_WITNESS_JOIN_INCONCLUSIVE_V1"
    except (Refusal, KeyError, TypeError, ValueError, AttributeError) as error:
        result["reasons"].append(str(error) if isinstance(error, Refusal) else "evidence-shape-or-decode-invalid")
    return result


def read_file(path, cap):
    path = Path(path)
    need(path.is_absolute() and path.resolve() == path, "noncanonical-input-path")
    before = path.stat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= cap, "input-physical-or-cap")
    raw = path.read_bytes()
    after = path.stat()
    keys = ["st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns"]
    need(all(getattr(before, k) == getattr(after, k) for k in keys) and len(raw) == before.st_size, "input-changed")
    return raw


def read_ref(value, cap):
    need(isinstance(value, dict) and isinstance(value.get("path"), str) and hex64(value.get("sha256"))
         and type(value.get("bytes")) is int and 0 <= value["bytes"] <= cap, "input-ref-shape-or-cap")
    raw = read_file(value["path"], cap)
    need(len(raw) == value["bytes"] and digest(raw) == value["sha256"], "input-ref-content-mismatch")
    return raw


def load_input(packet):
    need(type(packet.get("schemaVersion")) is int and packet["schemaVersion"] == 1
         and packet.get("state") == "V4_PUBLIC_TUPLE_INPUT_V1", "input-packet-schema")
    refs = packet.get("refs")
    need(isinstance(refs, dict) and set(refs) == set(CAPS), "input-role-set")
    material = {"refs": refs, "captureEvidence": packet["captureEvidence"]}
    for name, cap in CAPS.items():
        raw = read_ref(refs[name], cap)
        material[name] = raw if name in ["stdout", "requestBody"] else decode_json(raw)
    # These are explicit delegated DATA attestations, not inferred from an empty log.
    for ref in material["captureEvidence"].get("provenance", []):
        read_ref(ref, 2 << 20)
    return material


def fixture_suite(doc):
    need(doc.get("state") == "INERT_V4_PUBLIC_TUPLE_FIXTURES_V1", "fixture-schema")
    answers = []
    for case in doc["cases"]:
        m = copy.deepcopy(doc["base"])
        for change in case.get("set", []):
            at = m
            for key in change["path"][:-1]:
                at = at[key]
            at[change["path"][-1]] = change["value"]
        m["stdout"] = m["stdout"].encode("utf-8")
        m["requestBody"] = b64(m["requestBody"])
        out = evaluate(m)
        ok = all(out[k] == v for k, v in case["expect"].items())
        answers.append({"id": case["id"], "passed": ok, "state": out["state"], "reasons": out["reasons"]})
    return {"state": "INERT_V4_PUBLIC_TUPLE_FIXTURE_RESULTS_V1", "passed": all(x["passed"] for x in answers),
            "cases": answers, "actualHostOrGetterBehaviorProved": False}


def main():
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "--fixtures":
            out = fixture_suite(decode_json(read_file(sys.argv[2], 1 << 20)))
            success = out["passed"]
        else:
            need(len(sys.argv) == 2, "usage: admit-v4-public-tuple.py INPUT.json | --fixtures FIXTURES.json")
            out = evaluate(load_input(decode_json(read_file(sys.argv[1], 1 << 20))))
            success = out["prospectivePublicTupleJoinAdmitted"]
        print(json.dumps(out, indent=2, allow_nan=False))
        return 0 if success else 1
    except (Refusal, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"state": "V4_INPUT_REFUSED_V1", "prospectivePublicTupleJoinAdmitted": False,
                          "reasons": [str(error)], "fullNextAccepted": False}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
