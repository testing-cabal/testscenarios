#  testscenarios: extensions to python unittest to allow declarative
#  dependency injection ('scenarios') by tests.
#
# Copyright (c) 2009, Robert Collins <robertc@robertcollins.net>
#
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

import unittest

import testtools
from testtools.matchers import EndsWith

import testscenarios


class LoggingResult(testtools.TestResult):
    """TestResult that logs its event to a list."""

    def __init__(self, log):
        self._events = log
        super().__init__()

    def startTest(self, test):
        self._events.append(("startTest", test))
        super().startTest(test)

    def stop(self):
        self._events.append("stop")
        super().stop()

    def stopTest(self, test):
        self._events.append(("stopTest", test))
        super().stopTest(test)

    def addFailure(self, test, err=None, details=None):
        self._events.append(("addFailure", test, err))
        super().addFailure(test, err, details)

    def addError(self, test, err=None, details=None):
        self._events.append(("addError", test, err))
        super().addError(test, err, details)

    def addSkip(self, test, reason=None, details=None):
        # Extract reason from details if not provided directly
        if reason is None and details and "reason" in details:
            reason = details["reason"].as_text()
        self._events.append(("addSkip", test, reason))
        super().addSkip(test, reason, details)

    def addSuccess(self, test, details=None):
        self._events.append(("addSuccess", test))
        super().addSuccess(test, details)

    def startTestRun(self):
        self._events.append("startTestRun")
        super().startTestRun()

    def stopTestRun(self):
        self._events.append("stopTestRun")
        super().stopTestRun()

    def done(self):
        self._events.append("done")
        super().done()

    def tags(self, new_tags, gone_tags):
        self._events.append(("tags", new_tags, gone_tags))
        super().tags(new_tags, gone_tags)

    def time(self, a_datetime):
        self._events.append(("time", a_datetime))
        super().time(a_datetime)


class TestTestWithScenarios(testtools.TestCase):
    scenarios = testscenarios.scenarios.per_module_scenarios(
        "impl", (("unittest", "unittest"), ("unittest2", "unittest2"))
    )

    @property
    def Implementation(self):
        if isinstance(self.impl, tuple):
            self.skipTest("import failed - module not installed?")

        class Implementation(testscenarios.WithScenarios, self.impl.TestCase):
            pass

        return Implementation

    def test_no_scenarios_no_error(self):
        class ReferenceTest(self.Implementation):
            def test_pass(self):
                pass

        test = ReferenceTest("test_pass")
        result = unittest.TestResult()
        test.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(1, result.testsRun)

    def test_with_one_scenario_one_run(self):
        class ReferenceTest(self.Implementation):
            scenarios = [("demo", {})]

            def test_pass(self):
                pass

        test = ReferenceTest("test_pass")
        log = []
        result = LoggingResult(log)
        test.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(1, result.testsRun)
        self.expectThat(log[0][1].id(), EndsWith("ReferenceTest.test_pass(demo)"))

    def test_with_two_scenarios_two_run(self):
        class ReferenceTest(self.Implementation):
            scenarios = [("1", {}), ("2", {})]

            def test_pass(self):
                pass

        test = ReferenceTest("test_pass")
        log = []
        result = LoggingResult(log)
        test.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(2, result.testsRun)
        self.expectThat(log[0][1].id(), EndsWith("ReferenceTest.test_pass(1)"))
        self.expectThat(log[4][1].id(), EndsWith("ReferenceTest.test_pass(2)"))

    def test_attributes_set(self):
        class ReferenceTest(self.Implementation):
            scenarios = [("1", {"foo": 1, "bar": 2}), ("2", {"foo": 2, "bar": 4})]

            def test_check_foo(self):
                self.assertEqual(self.foo * 2, self.bar)

        test = ReferenceTest("test_check_foo")
        log = []
        result = LoggingResult(log)
        test.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(2, result.testsRun)

    def test_scenarios_attribute_cleared(self):
        class ReferenceTest(self.Implementation):
            scenarios = [("1", {"foo": 1, "bar": 2}), ("2", {"foo": 2, "bar": 4})]

            def test_check_foo(self):
                self.assertEqual(self.foo * 2, self.bar)

        test = ReferenceTest("test_check_foo")
        log = []
        result = LoggingResult(log)
        test.run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(2, result.testsRun)
        self.assertNotEqual(None, test.scenarios)
        self.assertEqual(None, log[0][1].scenarios)
        self.assertEqual(None, log[4][1].scenarios)

    def test_countTestCases_no_scenarios(self):
        class ReferenceTest(self.Implementation):
            def test_check_foo(self):
                pass

        test = ReferenceTest("test_check_foo")
        self.assertEqual(1, test.countTestCases())

    def test_countTestCases_empty_scenarios(self):
        class ReferenceTest(self.Implementation):
            scenarios = []

            def test_check_foo(self):
                pass

        test = ReferenceTest("test_check_foo")
        self.assertEqual(1, test.countTestCases())

    def test_countTestCases_1_scenarios(self):
        class ReferenceTest(self.Implementation):
            scenarios = [("1", {"foo": 1, "bar": 2})]

            def test_check_foo(self):
                pass

        test = ReferenceTest("test_check_foo")
        self.assertEqual(1, test.countTestCases())

    def test_countTestCases_2_scenarios(self):
        class ReferenceTest(self.Implementation):
            scenarios = [("1", {"foo": 1, "bar": 2}), ("2", {"foo": 2, "bar": 4})]

            def test_check_foo(self):
                pass

        test = ReferenceTest("test_check_foo")
        self.assertEqual(2, test.countTestCases())

    def test_debug_2_scenarios(self):
        log = []

        class ReferenceTest(self.Implementation):
            scenarios = [("1", {"foo": 1, "bar": 2}), ("2", {"foo": 2, "bar": 4})]

            def test_check_foo(self):
                log.append(self)

        test = ReferenceTest("test_check_foo")
        test.debug()
        self.assertEqual(2, len(log))
        self.assertEqual(None, log[0].scenarios)
        self.assertEqual(None, log[1].scenarios)
        self.assertNotEqual(log[0].id(), log[1].id())
