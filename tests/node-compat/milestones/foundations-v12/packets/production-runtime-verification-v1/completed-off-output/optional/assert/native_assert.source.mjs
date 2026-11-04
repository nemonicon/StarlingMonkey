import __smBuiltin0, * as root from "node:assert";
import __smBuiltin1, * as strict from "node:assert/strict";
// tests/node-compat/foundation-assert/checks.mjs
const OwnNames = Object.getOwnPropertyNames;
const Is = Object.is;
const ErrorCtor = Error;
const expectedNames = [
	"AssertionError",
	"CallTracker",
	"deepEqual",
	"deepStrictEqual",
	"default",
	"doesNotMatch",
	"doesNotReject",
	"doesNotThrow",
	"equal",
	"fail",
	"ifError",
	"match",
	"notDeepEqual",
	"notDeepStrictEqual",
	"notEqual",
	"notStrictEqual",
	"ok",
	"partialDeepStrictEqual",
	"rejects",
	"strict",
	"strictEqual",
	"throws"
];
function assertChecks(a, s) {
	const results = [];
	function must(value, label) {
		if (!value) throw new ErrorCtor(`Assert differential check failed: ${label}`);
	}
	function check(name, run) {
		results.push({
			name,
			result: run()
		});
	}
	function succeeds(run) {
		must(run() === void 0, "successful assertion returns undefined");
		return true;
	}
	function assertion(run, actual, expected) {
		let caught;
		try {
			run();
		} catch (error) {
			caught = error;
		}
		must(caught instanceof a.AssertionError, "AssertionError identity");
		must(Is(caught.actual, actual) && Is(caught.expected, expected), "actual and expected identity");
		return {
			name: caught.name,
			code: caught.code,
			operator: caught.operator,
			generatedMessage: caught.generatedMessage
		};
	}
	function code(run) {
		try {
			run();
		} catch (error) {
			return {
				name: error.name,
				code: error.code
			};
		}
		throw new ErrorCtor("Expected an exception");
	}
	function rethrows(run, sentinel) {
		try {
			run();
		} catch (error) {
			must(error === sentinel, "thrown identity");
			return true;
		}
		throw new ErrorCtor("Expected thrown identity");
	}
	check("finite namespaces", () => {
		for (const m of [a, s]) {
			must(OwnNames(m).sort().join(",") === expectedNames.join(","), "exact22 exports");
			must(m.then === void 0 && typeof m.default === "function", "safe namespace inspection");
		}
		return expectedNames;
	});
	check("root and strict graph", () => {
		must(a.default === a.ok && a.default.ok === a.ok, "root default/ok");
		must(s.default === a.strict && s.default.strict === s.default && a.default.strict === s.default, "strict root");
		must(s.default !== a.default && s.ok === a.ok && s.default.ok === a.ok, "strict ok");
		must(s.equal === a.strictEqual && s.notEqual === a.notStrictEqual && s.deepEqual === a.deepStrictEqual && s.notDeepEqual === a.notDeepStrictEqual, "strict aliases");
		for (const name of expectedNames) if (name !== "default") must(a.default[name] === a[name], `default member ${name}`);
		for (const name of expectedNames) if (name !== "default") must(s.default[name] === s[name], `strict member ${name}`);
		return true;
	});
	check("function names and arities", () => expectedNames.map((name) => [
		name,
		a[name].name,
		a[name].length,
		s[name].name,
		s[name].length
	]));
	check("default own property order", () => [OwnNames(a.default), OwnNames(s.default)]);
	check("truthy primitive and object", () => {
		for (const value of [
			true,
			1,
			"x",
			{},
			[],
			Symbol("x"),
			1n
		]) succeeds(() => a.ok(value));
		return true;
	});
	check("ok missing", () => assertion(() => a.ok(), void 0, true));
	check("ok false", () => assertion(() => a.ok(false), false, true));
	check("ok empty message", () => assertion(() => a.ok(0, ""), 0, true));
	check("ok custom message", () => assertion(() => a.ok(null, "chosen"), null, true));
	check("success never converts message", () => {
		const value = { toString() {
			throw new ErrorCtor("message must stay unread");
		} };
		return succeeds(() => a.ok(true, value));
	});
	check("error message rethrows same object", () => {
		const marker = new ErrorCtor("marker");
		return rethrows(() => a.strictEqual(1, 2, marker), marker);
	});
	check("fail no arguments", () => assertion(() => a.fail(), void 0, void 0));
	check("fail null retains actual", () => assertion(() => a.fail(null), null, void 0));
	check("fail empty string", () => assertion(() => a.fail(""), void 0, void 0));
	check("fail custom message", () => assertion(() => a.fail("chosen"), void 0, void 0));
	check("fail error identity", () => {
		const marker = new ErrorCtor("marker");
		return rethrows(() => a.fail(marker), marker);
	});
	check("loose equality and NaN", () => {
		succeeds(() => a.equal(1, "1"));
		succeeds(() => a.equal(NaN, NaN));
		return true;
	});
	check("loose equality coercion", () => {
		let calls = 0;
		succeeds(() => a.equal({ valueOf() {
			calls++;
			return 7;
		} }, 7));
		return calls;
	});
	check("equal mismatch", () => assertion(() => a.equal(1, 2), 1, 2));
	check("notEqual mismatch NaN", () => assertion(() => a.notEqual(NaN, NaN), NaN, NaN));
	check("notEqual success", () => succeeds(() => a.notEqual(1, "2")));
	check("strict SameValue", () => {
		succeeds(() => a.strictEqual(NaN, NaN));
		succeeds(() => a.notStrictEqual(0, -0));
		return true;
	});
	check("strict signed zero failure", () => assertion(() => a.strictEqual(0, -0), 0, -0));
	check("notStrict reference failure", () => {
		const value = {};
		return assertion(() => a.notStrictEqual(value, value), value, value);
	});
	check("strict subpath equality override", () => assertion(() => s.equal(1, "1"), 1, "1"));
	check("equality missing arguments", () => [
		code(() => a.equal(1)),
		code(() => a.notEqual()),
		code(() => a.strictEqual(1)),
		code(() => a.notStrictEqual())
	]);
	check("AssertionError supplied fields", () => {
		const actual = {}, expected = {};
		const error = new a.AssertionError({
			actual,
			expected,
			operator: "custom",
			message: "chosen"
		});
		must(error.actual === actual && error.expected === expected, "constructor reference retention");
		return [
			error.name,
			error.code,
			error.operator,
			error.generatedMessage,
			error.message,
			error.toString()
		];
	});
	check("AssertionError invalid options", () => [code(() => new a.AssertionError(null)), code(() => new a.AssertionError([]))]);
	check("throws constructor", () => succeeds(() => a.throws(() => {
		throw new TypeError("x");
	}, TypeError)));
	check("throws predicate true", () => {
		const marker = {};
		let got;
		succeeds(() => a.throws(() => {
			throw marker;
		}, function verify(value) {
			got = value;
			return true;
		}));
		must(got === marker, "predicate receives original");
		return true;
	});
	check("throws predicate exact true required", () => {
		const marker = new ErrorCtor("x");
		const predicate = () => 1;
		return assertion(() => a.throws(() => {
			throw marker;
		}, predicate), marker, predicate);
	});
	check("throws regex", () => succeeds(() => a.throws(() => {
		throw new ErrorCtor("needle");
	}, /needle/)));
	check("throws mismatching Error message is rendered", () => {
		const marker = /* @__PURE__ */ new TypeError("x");
		const message = new ErrorCtor("chosen");
		return assertion(() => a.throws(() => {
			throw marker;
		}, RangeError, message), marker, RangeError);
	});
	check("throws primitive undefined", () => succeeds(() => a.throws(() => {
		throw void 0;
	})));
	check("throws missing exception", () => assertion(() => a.throws(() => {}), void 0, void 0));
	check("throws callback before matcher validation", () => {
		let called = 0;
		const error = code(() => a.throws(() => {
			called++;
			throw 9;
		}, 4));
		return [called, error];
	});
	check("throws invalid callback", () => code(() => a.throws(4)));
	check("throws ambiguous message", () => code(() => a.throws(() => {
		throw new ErrorCtor("same");
	}, "same")));
	check("doesNotThrow success skips matcher validation", () => succeeds(() => a.doesNotThrow(() => 3, 4)));
	check("doesNotThrow unwanted", () => {
		const marker = new ErrorCtor("x");
		return assertion(() => a.doesNotThrow(() => {
			throw marker;
		}), marker, void 0);
	});
	check("doesNotThrow unmatched rethrows", () => {
		const marker = /* @__PURE__ */ new TypeError("x");
		return rethrows(() => a.doesNotThrow(() => {
			throw marker;
		}, RangeError), marker);
	});
	check("matcher predicate exceptions propagate", () => {
		const marker = new ErrorCtor("predicate");
		return rethrows(() => a.throws(() => {
			throw 3;
		}, () => {
			throw marker;
		}), marker);
	});
	check("ifError nullish", () => {
		succeeds(() => a.ifError(null));
		succeeds(() => a.ifError(void 0));
		return true;
	});
	check("ifError false is unwanted", () => assertion(() => a.ifError(false), false, null));
	check("match and doesNotMatch successes", () => {
		succeeds(() => a.match("abc", /b/));
		succeeds(() => a.doesNotMatch("abc", /z/));
		return true;
	});
	check("match RegExp lastIndex", () => {
		const re = /a/g;
		succeeds(() => a.match("aa", re));
		const first = re.lastIndex;
		succeeds(() => a.match("aa", re));
		return [first, re.lastIndex];
	});
	check("match native exec ignores override", () => {
		const re = /b/;
		re.exec = () => {
			throw new ErrorCtor("must use primordial exec");
		};
		return succeeds(() => a.match("abc", re));
	});
	check("match mismatch", () => {
		const re = /z/;
		return assertion(() => a.match("abc", re), "abc", re);
	});
	check("doesNotMatch mismatch", () => {
		const re = /b/;
		return assertion(() => a.doesNotMatch("abc", re), "abc", re);
	});
	check("match nonstring AssertionError", () => {
		const re = /x/;
		return assertion(() => a.match(7, re), 7, re);
	});
	check("match invalid regexp validated first", () => code(() => a.match(7, {})));
	check("match error message identity", () => {
		const marker = new ErrorCtor("chosen");
		return rethrows(() => a.match("abc", /z/, marker), marker);
	});
	check("named binding remains initial default mutation", () => {
		const old = a.default.equal;
		try {
			a.default.equal = 17;
			must(a.equal === old && s.equal !== 17, "named binding capture");
		} finally {
			a.default.equal = old;
		}
		return true;
	});
	check("strict self state and root state independent", () => {
		const root = a.default.equal, strict = s.default.equal;
		try {
			s.default.equal = 19;
			must(a.default.equal === root && s.equal === strict, "strict mutation isolation");
		} finally {
			s.default.equal = strict;
		}
		return true;
	});
	check("primitive equality grid", () => {
		const values = [
			void 0,
			null,
			false,
			true,
			0,
			-0,
			1,
			NaN,
			Infinity,
			"",
			"0",
			"1",
			0n,
			1n
		];
		const table = [];
		for (let i = 0; i < values.length; i++) for (let j = 0; j < values.length; j++) {
			const row = [i, j];
			for (const name of [
				"equal",
				"notEqual",
				"strictEqual",
				"notStrictEqual"
			]) try {
				must(a[name](values[i], values[j]) === void 0, "grid success");
				row.push("pass");
			} catch (error) {
				must(error instanceof a.AssertionError && error.code === "ERR_ASSERTION", "grid assertion");
				row.push(error.operator);
			}
			table.push(row);
		}
		return table;
	});
	return results;
}
function prototypeOnlyChecks(a) {
	const results = [];
	for (const name of [
		"deepEqual",
		"notDeepEqual",
		"deepStrictEqual",
		"notDeepStrictEqual",
		"partialDeepStrictEqual",
		"rejects",
		"doesNotReject",
		"CallTracker"
	]) for (const construct of [false, true]) {
		let failure;
		try {
			if (construct) new a[name]();
			else a[name]();
		} catch (error) {
			failure = error;
		}
		if (failure?.code !== "ERR_SM_NODE_UNSUPPORTED") throw new ErrorCtor(`Deferred ${name} ${construct} did not fail`);
		results.push({
			name,
			construct,
			code: failure.code,
			operation: failure.operation
		});
	}
	for (const [name, run] of [
		["fail legacy", () => a.fail(1, 2)],
		["throws validation object", () => a.throws(() => {
			throw new ErrorCtor("x");
		}, { message: "x" })],
		["doesNotThrow validation object", () => a.doesNotThrow(() => {
			throw new ErrorCtor("x");
		}, {})],
		["AssertionError details", () => new a.AssertionError({ details: [] })]
	]) {
		let error;
		try {
			run();
		} catch (caught) {
			error = caught;
		}
		if (error?.code !== "ERR_SM_NODE_UNSUPPORTED") throw new ErrorCtor(`Expected typed deferred operation ${name}`);
		results.push({
			name,
			code: error.code,
			operation: error.operation
		});
	}
	const oldIs = Object.is, oldNaN = Number.isNaN, oldExec = RegExp.prototype.exec;
	const oldApply = Reflect.apply, oldString = globalThis.String;
	try {
		const poisoned = () => {
			throw new ErrorCtor("mutated primordial");
		};
		Object.is = Number.isNaN = RegExp.prototype.exec = Reflect.apply = globalThis.String = poisoned;
		a.strictEqual(NaN, NaN);
		a.equal(NaN, NaN);
		a.match("abc", /b/);
		a.throws(() => {
			throw new ErrorCtor("x");
		}, /x/);
		let caught;
		try {
			a.equal(1, 2);
		} catch (error) {
			caught = error;
		}
		if (caught?.code !== "ERR_ASSERTION") throw new ErrorCtor("Captured diagnostics failed");
	} finally {
		Object.is = oldIs;
		Number.isNaN = oldNaN;
		RegExp.prototype.exec = oldExec;
		Reflect.apply = oldApply;
		globalThis.String = oldString;
	}
	results.push({
		name: "captured primordials survive mutation",
		passed: true
	});
	const marker = {
		get secret() {
			throw new ErrorCtor("must not inspect");
		},
		toString() {
			throw new ErrorCtor("must not stringify");
		}
	};
	let caught;
	try {
		a.strictEqual(marker, {});
	} catch (error) {
		caught = error;
	}
	if (caught?.actual !== marker || caught?.code !== "ERR_ASSERTION") throw new ErrorCtor("Opaque diagnostics inspected application object");
	results.push({
		name: "safe opaque diagnostic rendering",
		passed: true
	});
	return results;
}
// tests/node-compat/foundation-assert/native-require.cjs.native-profile.mjs
const __smModule = { exports: {} };
(function(module, exports) {
	const root = __smBuiltin0;
	const canonical = __smBuiltin0;
	const strict = __smBuiltin1;
	const canonicalStrict = __smBuiltin1;
	module.exports = function inspect(rootDefault, strictDefault) {
		let call, construct;
		try {
			root.deepStrictEqual({}, {});
		} catch (error) {
			call = error.code;
		}
		try {
			new strict.rejects();
		} catch (error) {
			construct = error.code;
		}
		return {
			rootType: typeof root,
			strictType: typeof strict,
			same: root === canonical && root === rootDefault && strict === canonicalStrict && strict === strictDefault,
			strictGraph: root.strict === strict && strict.strict === strict && root.ok === strict.ok,
			aliasOverrides: strict.equal === root.strictEqual && strict.notEqual === root.notStrictEqual,
			defaultProperty: typeof root.default,
			rejectedCall: call,
			rejectedConstruction: construct
		};
	};
}).call(__smModule.exports, __smModule, __smModule.exports);
var native_require_cjs_native_profile_default = __smModule.exports;
// tests/node-compat/foundation-assert/native-component.mjs
const snapshotValue = { count: 0 };
const snapshotError = new root.AssertionError({
	actual: snapshotValue,
	expected: true,
	operator: "snapshot",
	message: "snapshot"
});
root.ok(snapshotValue);
let calls = 0;
async function run() {
	try {
		const rootId = String.fromCharCode(97, 115, 115, 101, 114, 116);
		const strictId = rootId + String.fromCharCode(47, 115, 116, 114, 105, 99, 116);
		const bare = await import(rootId), bareStrict = await import(strictId), again = await import(rootId);
		const originalEqual = root.default.equal;
		let sharedMutation;
		try {
			root.default.equal = 19;
			sharedMutation = bare.default.equal === 19 && root.equal === originalEqual && strict.equal === root.strictEqual;
		} finally {
			root.default.equal = originalEqual;
		}
		const aliases = {
			names: Object.getOwnPropertyNames(bare).sort(),
			strictNames: Object.getOwnPropertyNames(bareStrict).sort(),
			canonicalNamespaceStable: await import("node:assert") === root,
			bareCache: bare === again,
			rootValues: Object.keys(root).every((name) => root[name] === bare[name]),
			strictValues: Object.keys(strict).every((name) => strict[name] === bareStrict[name]),
			moduleTag: Object.prototype.toString.call(bare),
			nullNamespacePrototype: Object.getPrototypeOf(bare) === null,
			thenType: typeof bare.then,
			sharedMutation
		};
		snapshotValue.count++;
		return JSON.stringify({
			calls: ++calls,
			snapshotCount: snapshotValue.count,
			snapshotIdentity: snapshotError.actual === snapshotValue && snapshotError instanceof root.AssertionError,
			namespaceIdentity: await Promise.resolve(root) === root && await Promise.resolve(strict) === strict,
			cases: assertChecks(root, strict),
			profile: prototypeOnlyChecks(root),
			aliases,
			commonJS: native_require_cjs_native_profile_default(root.default, strict.default)
		});
	} catch (error) {
		return JSON.stringify({ failure: {
			name: error.name,
			code: error.code,
			message: error.message,
			stack: error.stack
		} });
	}
}
export { run };
