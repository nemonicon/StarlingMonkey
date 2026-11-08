"""Pure Root policy fixtures; no originals, guards, actor code or targets load."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cohort_policy_under_test',HERE/'policy.py')
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
REF=dict(path='/fixture/owner.json',sha256='0'*64,bytes=1)


def publication(native=True):
    terminal=dict(rawExitCode=1,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,
        allObservedOwnedGroupsGone=True,errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[],
        finalGroups=[dict(alive=False,signalAllowed=False)])
    observation=dict(ownedGroupsClean=True,protectedInputsPreserved=True)
    browser=dict(passed=False,functionalPassed=True,browserClosed=True,tests=[{},{}],
        netlog=dict(completeJson=True,fsynced=True,errors=[],file=REF))
    client=dict(http=[{} for _ in range(24)],portableCache=dict(records=[{} for _ in range(5)]),
        portableCacheValidation=dict(passed=False),supplemental=dict(observations=[{} for _ in range(6)]),
        supplementalValidation=dict(passed=False),streaming=dict(complete=False),
        cacheInvalidation=dict(passed=False),browser=browser,browserExit=dict(code=1,signal=None))
    result=dict(passed=False,originalApplicationInputsPreserved=True,prepared=True,
        originalInputsPreserved=True,readonlyAppPreserved=True,
        client=dict(exit=dict(code=1,signal=None,error=None)),
        server=dict(exit=dict(code=0,signal=None,error=None),forcedCleanup=False,
            stdoutCapture=dict(state='RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1',limitBytes=8388608,
                complete=True,pipeEof=True,fileClosed=True,fileBoundVerified=True,finalized=True,
                overflow=False,partialWritePossible=False,unretainedBytesUnknown=False,errors=[],
                fileBytes=42,completeWriteBytes=42,lastReservedWriteCeiling=42)))
    if not native:
        result.update(client)
        result.pop('server')
        client=result
    return terminal,observation,result,client


class Policy(unittest.TestCase):
    def test_unbound_refuses_without_io(self):
        self.assertEqual(p.ACTOR_REFS,dict(a=None,b=None,c=None,d=None))
        self.assertEqual(p.NEW_REVIEW_REFS,dict(b=None,d=None))
        with self.assertRaisesRegex(ValueError,'Unbound Root Source'): p.require_bound()

    def test_authentic_old_schema_is_not_rewritten(self):
        for arm in 'ac':
            review=json.loads(Path(p.OLD_REVIEW_REFS[arm]['path']).read_bytes())
            before=copy.deepcopy(review)
            policy=p.schema_policy(arm,review)
            self.assertEqual(review,before)
            self.assertEqual(policy['ownerReviewKey'],'complementaryOwnerWorldReview' if arm=='a' else 'actualOwnerWorldReview')
            self.assertEqual('deployedCompletionDiagnosticObserved' in review,arm!='a')
            bad=copy.deepcopy(review)
            if arm=='a': bad['deployedCompletionDiagnosticObserved']=False
            else: del bad['deployedCompletionDiagnosticObserved']
            with self.assertRaises((ValueError,KeyError)): p.schema_policy(arm,bad)

    def test_variant_schema_is_explicit(self):
        for arm in 'bd':
            review=dict(state='COORDINATED_NEXT_AWAIT_VARIANT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1',
                variant=arm.upper(),verifiedPassed=True,completeReturnedImportAuditVerified=True,
                actualOwnerWorldReview=REF,deployedCompletionDiagnosticObserved=False,
                **{key:False for key in p.COMMON_FALSE})
            self.assertFalse(p.schema_policy(arm,review)['reviewRewritten'])
            review['variant']='D' if arm=='b' else 'B'
            with self.assertRaises(ValueError): p.schema_policy(arm,review)

    def test_clean_semantic_failure_continues_without_conversion(self):
        for arm in ['stock','a','b','c','d']:
            args=publication(arm!='stock')
            outcome=p.classify_published(arm,*args)
            self.assertTrue(outcome['valid'])
            self.assertFalse(outcome['originalAllPassed'])
            self.assertEqual(outcome['rawExitCode'],1)

    def test_raw_one_cannot_pass_a_true_result(self):
        for arm in ['a','stock']:
            args=publication(arm!='stock')
            args[2]['passed']=True
            args[1]['hostExperimentPassed' if arm=='stock' else 'passed']=False
            outcome=p.classify_published(arm,*args)
            self.assertTrue(outcome['valid'])
            self.assertFalse(outcome['originalAllPassed'])
            args[0]['rawExitCode']=0
            args[1]['hostExperimentPassed' if arm=='stock' else 'passed']=True
            self.assertTrue(p.classify_published(arm,*args)['originalAllPassed'])

    def test_recorded_deadlines_and_partial_bodies_are_outcomes(self):
        args=publication()
        client=args[3]
        client['browser']['tests'][0]=dict(timedOut=True,passed=False)
        client['portableCache']['records'][0]=dict(error=dict(name='TimeoutError'),bodyBytes=3)
        client['supplemental']['observations'][0]=dict(error=dict(name='AbortError'))
        self.assertTrue(p.classify_published('c',*args)['valid'])

    def test_strict_positive_does_not_waive_counter(self):
        args=publication()
        args[3]['browser'].update(passed=True,functionalPassed=True)
        args[3]['browserExit']=dict(code=0,signal=None)
        outcome=p.classify_published('d',*args)
        self.assertTrue(outcome['valid'])
        self.assertFalse(outcome['originalAllPassed'])

    def test_stop_invariants(self):
        mutations=[
            lambda t,o,r,c:t.update(timeout=True),
            lambda t,o,r,c:t.update(rawExitCode=2),
            lambda t,o,r,c:t.update(parentOwnedGroupGone=False),
            lambda t,o,r,c:o.update(protectedInputsPreserved=False),
            lambda t,o,r,c:r['server']['stdoutCapture'].update(overflow=True),
            lambda t,o,r,c:r['server']['stdoutCapture'].update(fileBytes=8388609),
            lambda t,o,r,c:r['server']['stdoutCapture'].update(completeWriteBytes=41),
            lambda t,o,r,c:r['server'].update(forcedCleanup=True),
            lambda t,o,r,c:c.update(http=[]),
            lambda t,o,r,c:c['supplemental'].update(observations=[]),
            lambda t,o,r,c:c['browser'].update(browserClosed=False),
            lambda t,o,r,c:c['browser']['netlog'].update(completeJson=False),
            lambda t,o,r,c:c.update(browserExit=dict(code=None,signal='SIGKILL')),
        ]
        for change in mutations:
            args=publication();change(*args)
            self.assertFalse(p.classify_published('a',*args)['valid'])

    def test_stock_has_no_native_capture_contract(self):
        args=publication(False)
        self.assertNotIn('server',args[2])
        self.assertTrue(p.classify_published('stock',*args)['valid'])

    def test_fixed_plan_and_source_cli_contracts(self):
        plan=json.loads((HERE/'plan.json').read_bytes())
        self.assertEqual([x['arm'] for x in plan['trials']],['stock','a','b','c','d','stock','d','c','b','a'])
        self.assertEqual([x['ownerSeconds'] for x in plan['trials']],[300,600,600,600,600,300,600,600,600,600])
        for name in p.ROOT_FILES:
            text=(HERE/name).read_text();ast.parse(text,filename=name)
            self.assertNotIn('sys.argv =',text)
            self.assertNotIn('sys.argv=',text)
            self.assertNotIn('.HERE=',text)
            self.assertNotIn('.ACTOR=',text)
        native=(HERE/'run-native-trial.py').read_text()
        self.assertIn('len(sys.argv)==2',native)
        self.assertIn('owned.main()',native)
        cohort=(HERE/'run-cohort.py').read_text()
        self.assertIn("'stock',item['authority']['path']",cohort)
        self.assertIn("if stopped: break",cohort)
        self.assertNotIn("if child.returncode==1:",cohort)


if __name__=='__main__': unittest.main()
