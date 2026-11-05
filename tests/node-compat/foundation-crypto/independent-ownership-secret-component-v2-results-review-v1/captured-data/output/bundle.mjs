// tests/node-compat/foundation-crypto/ownership-secret-component-candidate-v2/guest.mjs
const EXPECTED = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7";
const KEY_B64 = "CwsLCwsLCwsLCwsLCwsLCwsLCws";
const initial = {
	keyImportsAttempted: 0,
	signCalls: 0,
	verifyCalls: 0,
	retainedKeys: 0,
	pendingOperations: 0
};
const count = {
	inspectCalls: 0,
	runCalls: 0,
	clearCalls: 0,
	validateCalls: 0,
	keyImportsAttempted: 0,
	keyImportsFulfilled: 0,
	signCalls: 0,
	verifyCalls: 0
};
let rawKey = null;
let jwkKey = null;
let knownConstructor = null;
let observations = [];
function check(value, message) {
	if (!value) throw new Error("CRYPTO_OWNER_CHECK:" + message);
}
function same(a, b, message) {
	check(JSON.stringify(a) === JSON.stringify(b), message);
}
function hex(bytes) {
	let result = "";
	for (const byte of bytes) result += byte.toString(16).padStart(2, "0");
	return result;
}
function window(bytes) {
	const backing = new Uint8Array(bytes.length + 16);
	backing.fill(165);
	backing.set(bytes, 8);
	return {
		backing,
		view: backing.subarray(8, 8 + bytes.length)
	};
}
function message() {
	return window(new Uint8Array([
		72,
		105,
		32,
		84,
		104,
		101,
		114,
		101
	]));
}
function counters() {
	return { ...count };
}
function returned(value) {
	if (value instanceof ArrayBuffer) return {
		type: "ArrayBuffer",
		bytes: value.byteLength,
		fullHex: value.byteLength <= 1024 ? hex(new Uint8Array(value)) : null,
		fullBytesRetained: value.byteLength <= 1024
	};
	if (value === null || [
		"string",
		"boolean",
		"number",
		"undefined"
	].includes(typeof value)) return {
		type: typeof value,
		...value === void 0 ? {} : { value }
	};
	return {
		type: typeof value,
		opaque: true,
		fullOpaqueValueClaim: false
	};
}
function note(operation, phase, value) {
	observations.push({
		operation,
		phase,
		returned: returned(value)
	});
}
function state() {
	return {
		rawRetained: rawKey !== null,
		jwkRetained: jwkKey !== null,
		strongApplicationKeyOwners: Number(rawKey !== null) + Number(jwkKey !== null),
		pendingOperationsInstrumented: false,
		finalizersOrWipesObserved: false
	};
}
function keyRecord(key, extractable) {
	check(typeof globalThis.CryptoKey === "function" && key instanceof globalThis.CryptoKey, "genuine global CryptoKey");
	check(Object.getPrototypeOf(key) === globalThis.CryptoKey.prototype, "actual key prototype/global identity");
	const result = {
		instanceOfGlobalCryptoKey: true,
		globalConstructorStable: knownConstructor === globalThis.CryptoKey,
		type: key.type,
		extractable: key.extractable,
		algorithm: key.algorithm,
		usages: [...key.usages]
	};
	check(result.globalConstructorStable && result.type === "secret" && result.extractable === extractable, "key type/extractable/global");
	same(Object.keys(result.algorithm).sort(), [
		"hash",
		"length",
		"name"
	], "exact algorithm dictionary fields");
	check(result.algorithm.name === "HMAC" && result.algorithm.length === 160 && result.algorithm.hash?.name === "SHA-256", "full HMAC algorithm metadata");
	same(Object.keys(result.algorithm.hash), ["name"], "exact hash dictionary");
	same(result.usages, ["sign", "verify"], "full usages");
	check(key.algorithm === result.algorithm && key.usages === key.usages, "cached algorithm/usages references");
	return result;
}
async function importKey(...args) {
	count.keyImportsAttempted++;
	note("importKey", "before", void 0);
	const result = await globalThis.crypto.subtle.importKey(...args);
	note("importKey", "returned", result);
	count.keyImportsFulfilled++;
	return result;
}
async function sign(algorithm, key, data) {
	count.signCalls++;
	note("sign", "before", void 0);
	const result = await globalThis.crypto.subtle.sign(algorithm, key, data);
	note("sign", "returned", result);
	return result;
}
async function verify(algorithm, key, signature, data) {
	count.verifyCalls++;
	note("verify", "before", void 0);
	const result = await globalThis.crypto.subtle.verify(algorithm, key, signature, data);
	note("verify", "returned", result);
	return result;
}
async function exercise(key, extractable) {
	const input = message(), before = hex(input.backing), firstBuffer = await sign("HMAC", key, input.view);
	check(firstBuffer instanceof ArrayBuffer, "sign returns actual ArrayBuffer");
	const first = new Uint8Array(firstBuffer), firstHex = hex(first);
	check(first.length === 32 && firstHex === EXPECTED, "full RFC4231 signature");
	const secondBuffer = await sign({ name: "HMAC" }, key, input.view);
	check(secondBuffer instanceof ArrayBuffer, "second actual ArrayBuffer");
	const second = new Uint8Array(secondBuffer), secondHex = hex(second);
	check(second.length === 32 && secondHex === EXPECTED && hex(first) === firstHex, "complete prior-output stability after next sign");
	check(firstBuffer !== secondBuffer, "successive nonempty independent backing");
	const saved = first[0];
	first[0] ^= 255;
	check(hex(second) === secondHex && hex(input.backing) === before, "mutation leaves full second/input bytes intact");
	first[0] = saved;
	check(hex(first) === firstHex, "restore full first signature");
	const signature = window(second), signatureBefore = hex(signature.backing), valid = await verify("HMAC", key, signature.view, input.view), bad = new Uint8Array(second);
	bad[0] ^= 1;
	const invalid = await verify({ name: "HMAC" }, key, bad, input.view);
	check(valid === true && invalid === false, "full correct/tampered verify booleans");
	check(hex(input.backing) === before && hex(signature.backing) === signatureBefore, "full input/signature windows and sentinels immutable");
	return {
		key: keyRecord(key, extractable),
		firstSignatureHex: firstHex,
		secondSignatureHex: secondHex,
		signatureBytes: 32,
		priorFullBytesStable: true,
		independentNonemptyBacking: true,
		mutationRestored: true,
		valid,
		invalid,
		inputBeforeHex: before,
		inputAfterHex: hex(input.backing),
		inputWindow: {
			byteOffset: input.view.byteOffset,
			byteLength: input.view.byteLength,
			backingBytes: input.backing.byteLength
		},
		signatureBeforeHex: signatureBefore,
		signatureAfterHex: hex(signature.backing)
	};
}
function errorRecord(error) {
	return {
		thrownType: typeof error,
		typeError: error instanceof TypeError,
		name: error instanceof Error && typeof error.name === "string" ? error.name : null,
		message: error instanceof Error && typeof error.message === "string" ? error.message : null
	};
}
async function rejection(operation) {
	let promise;
	try {
		promise = operation();
	} catch (error) {
		return {
			kind: "synchronous-throw",
			error: errorRecord(error)
		};
	}
	if (!(promise instanceof Promise)) return {
		kind: "unexpected-non-promise",
		returnedType: typeof promise
	};
	try {
		return {
			kind: "unexpected-fulfillment",
			returnedType: typeof await promise
		};
	} catch (error) {
		return {
			kind: "native-promise-rejection",
			error: errorRecord(error)
		};
	}
}
function sentinels() {
	const reads = {
		algorithmName: 0,
		dataByteLength: 0,
		dataPrimitive: 0,
		dataString: 0,
		signatureByteLength: 0,
		signaturePrimitive: 0
	};
	return {
		reads,
		algorithm: { get name() {
			reads.algorithmName++;
			return "HMAC";
		} },
		data: {
			get byteLength() {
				reads.dataByteLength++;
				return 8;
			},
			[Symbol.toPrimitive]() {
				reads.dataPrimitive++;
				return 0;
			},
			toString() {
				reads.dataString++;
				return "harmless-data";
			}
		},
		signature: {
			get byteLength() {
				reads.signatureByteLength++;
				return 32;
			},
			[Symbol.toPrimitive]() {
				reads.signaturePrimitive++;
				return 0;
			}
		}
	};
}
async function prototypeRefusals() {
	check(rawKey !== null, "valid raw-key positive control must precede prototype probes");
	const s = sentinels(), v = sentinels();
	const signRefusal = await rejection(() => {
		count.signCalls++;
		return globalThis.crypto.subtle.sign(s.algorithm, globalThis.CryptoKey.prototype, s.data);
	});
	observations.push({
		operation: "prototype-sign",
		phase: "returned",
		record: signRefusal,
		reads: { ...s.reads }
	});
	const verifyRefusal = await rejection(() => {
		count.verifyCalls++;
		return globalThis.crypto.subtle.verify(v.algorithm, globalThis.CryptoKey.prototype, v.signature, v.data);
	});
	observations.push({
		operation: "prototype-verify",
		phase: "returned",
		record: verifyRefusal,
		reads: { ...v.reads }
	});
	for (const record of [signRefusal, verifyRefusal]) check(record.kind === "native-promise-rejection" && record.error.typeError === true, "prototype-key must reject as TypeError promise");
	check(Object.values(s.reads).every((n) => n === 0) && Object.values(v.reads).every((n) => n === 0), "key refusal before harmless algorithm/data conversions");
	const positive = sentinels(), input = message(), tag = await sign(positive.algorithm, rawKey, input.view);
	check(positive.reads.algorithmName === 1 && hex(new Uint8Array(tag)) === EXPECTED, "valid key reaches algorithm getter and same HMAC vector");
	const positiveVerify = sentinels();
	check(await verify(positiveVerify.algorithm, rawKey, new Uint8Array(tag), input.view) === true && positiveVerify.reads.algorithmName === 1, "valid verify getter positive control");
	const ordinaryInvalid = await rejection(() => {
		count.signCalls++;
		return globalThis.crypto.subtle.sign("HMAC", {}, input.view);
	});
	observations.push({
		operation: "ordinary-invalid-key",
		phase: "returned",
		record: ordinaryInvalid
	});
	check(ordinaryInvalid.kind === "native-promise-rejection" && ordinaryInvalid.error.typeError, "ordinary invalid-key refusal preserved");
	const getters = [];
	for (const name of [
		"algorithm",
		"extractable",
		"type",
		"usages"
	]) {
		const getter = Object.getOwnPropertyDescriptor(globalThis.CryptoKey.prototype, name)?.get;
		check(typeof getter === "function", "existing getter");
		let error;
		try {
			getter.call(globalThis.CryptoKey.prototype);
		} catch (value) {
			error = value;
		}
		check(error instanceof TypeError, "prototype getter refusal");
		getters.push({
			name,
			error: errorRecord(error)
		});
	}
	let constructorError;
	try {
		new globalThis.CryptoKey();
	} catch (error) {
		constructorError = error;
	}
	check(constructorError instanceof TypeError, "global no-constructor behavior");
	return {
		signRefusal,
		verifyRefusal,
		signConversionReads: s.reads,
		verifyConversionReads: v.reads,
		positiveAlgorithmReads: positive.reads.algorithmName,
		positiveVerifyAlgorithmReads: positiveVerify.reads.algorithmName,
		positiveFullSignatureHex: hex(new Uint8Array(tag)),
		ordinaryInvalid,
		getters,
		constructorError: errorRecord(constructorError),
		onlyNewGuardedArtifactAllowed: true,
		uniqueNativeErrorCauseInferred: false
	};
}
function inspect() {
	count.inspectCalls++;
	check(typeof globalThis.CryptoKey === "function" && typeof globalThis.crypto?.subtle?.importKey === "function", "actual installed WebCrypto globals");
	if (knownConstructor === null) knownConstructor = globalThis.CryptoKey;
	check(knownConstructor === globalThis.CryptoKey, "global constructor identity");
	return JSON.stringify({
		schemaVersion: 1,
		kind: "crypto-owner-inspect-v1",
		initial,
		counters: counters(),
		state: state(),
		globalCryptoKeyInstalled: true,
		constructorStable: true,
		cryptoOperationsAtSnapshot: 0,
		fullNativeOwnershipOrZeroizationObserved: false
	});
}
async function run(caseId) {
	count.runCalls++;
	observations = [];
	try {
		check(Number.isInteger(caseId) && caseId >= 0 && caseId < 4, "finite ordinary case0..3");
		if (knownConstructor === null) knownConstructor = globalThis.CryptoKey;
		let result;
		if (caseId === 0) {
			const input = window((/* @__PURE__ */ new Uint8Array(20)).fill(11)), before = hex(input.backing);
			rawKey = await importKey("raw", input.view, {
				name: "HMAC",
				hash: "SHA-256"
			}, false, ["sign", "verify"]);
			const importInputPreserved = hex(input.backing) === before;
			input.view.fill(0);
			result = {
				format: "raw",
				importInputPreserved,
				callerKeyBytesChangedAfterImport: true,
				callerBackingHex: hex(input.backing),
				operations: await exercise(rawKey, false)
			};
			check(importInputPreserved, "raw import input immutable");
		} else if (caseId === 1) {
			const jwk = {
				kty: "oct",
				k: KEY_B64,
				alg: "HS256",
				key_ops: ["sign", "verify"],
				ext: true
			}, before = JSON.stringify(jwk);
			jwkKey = await importKey("jwk", jwk, {
				name: "HMAC",
				hash: { name: "SHA-256" }
			}, true, ["sign", "verify"]);
			const importInputPreserved = JSON.stringify(jwk) === before;
			jwk.k = "AA";
			result = {
				format: "jwk",
				importInputPreserved,
				callerJwkChangedAfterImport: true,
				operations: await exercise(jwkKey, true)
			};
			check(importInputPreserved, "JWK import input immutable");
		} else if (caseId === 2) {
			check(rawKey !== null && jwkKey !== null, "retained keys require both prior imports");
			result = {
				format: "retained-pair",
				raw: await exercise(rawKey, false),
				jwk: await exercise(jwkKey, true),
				strongApplicationOwners: true
			};
		} else result = await prototypeRefusals();
		return JSON.stringify({
			schemaVersion: 1,
			kind: "crypto-owner-run-v1",
			caseId,
			completed: true,
			result,
			observations,
			initial,
			counters: counters(),
			state: state(),
			gcOrEntropyRequested: false,
			finalizerCountOrWipeProof: false
		});
	} catch (error) {
		return JSON.stringify({
			schemaVersion: 1,
			kind: "crypto-owner-run-v1",
			caseId,
			completed: false,
			error: errorRecord(error),
			observations,
			initial,
			counters: counters(),
			state: state(),
			semanticFailureNotNativeTrapProof: true
		});
	}
}
function clear() {
	count.clearCalls++;
	rawKey = null;
	jwkKey = null;
	return JSON.stringify({
		schemaVersion: 1,
		kind: "crypto-owner-clear-v1",
		initial,
		counters: counters(),
		state: state(),
		applicationReferencesReleased: true,
		collectionOrNativeFreeOrWipeObserved: false
	});
}
async function validate() {
	const entryCounters = counters(), entryState = state();
	count.validateCalls++;
	const before = JSON.parse(inspect()), records = [];
	for (let id = 0; id < 4; id++) {
		const record = JSON.parse(await run(id));
		records.push(record);
		if (!record.completed) break;
	}
	const released = JSON.parse(clear()), after = JSON.parse(inspect());
	return JSON.stringify({
		schemaVersion: 1,
		kind: "crypto-owner-within-export-validation-v1",
		entryCounters,
		entryState,
		before,
		records,
		released,
		after,
		withinOneOuterExport: true,
		separateHostCallInterleavingProved: false,
		finalizerOrWipeObserved: false
	});
}
export { clear, inspect, run, validate };
