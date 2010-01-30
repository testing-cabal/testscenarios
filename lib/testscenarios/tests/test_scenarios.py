#  testscenarios: extensions to python unittest to allow declarative
#  dependency injection ('scenarios') by tests.
#  Copyright (C) 2009  Robert Collins <robertc@robertcollins.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import unittest

import testscenarios
from testscenarios.scenarios import (
    apply_scenario,
    apply_scenarios,
    generate_scenarios,
    )
import testtools
from testtools.tests.helpers import LoggingResult


class TestGenerateScenarios(testtools.TestCase):

    def hook_apply_scenarios(self):
        self.addCleanup(setattr, testscenarios.scenarios, 'apply_scenarios',
            apply_scenarios)
        log = []
        def capture(scenarios, test):
            log.append((scenarios, test))
            return apply_scenarios(scenarios, test)
        testscenarios.scenarios.apply_scenarios = capture
        return log

    def test_generate_scenarios_preserves_normal_test(self):
        class ReferenceTest(unittest.TestCase):
            def test_pass(self):
                pass
        test = ReferenceTest("test_pass")
        log = self.hook_apply_scenarios()
        self.assertEqual([test], list(generate_scenarios(test)))
        self.assertEqual([], log)

    def test_tests_with_scenarios_calls_apply_scenarios(self):
        class ReferenceTest(unittest.TestCase):
            scenarios = [('demo', {})]
            def test_pass(self):
                pass
        test = ReferenceTest("test_pass")
        log = self.hook_apply_scenarios()
        tests = list(generate_scenarios(test))
        self.assertEqual(
            'testscenarios.tests.test_scenarios.ReferenceTest.test_pass(demo)',
            tests[0].id())
        self.assertEqual([([('demo', {})], test)], log)

    def test_all_scenarios_yielded(self):
        class ReferenceTest(unittest.TestCase):
            scenarios = [('1', {}), ('2', {})]
            def test_pass(self):
                pass
        test = ReferenceTest("test_pass")
        tests = list(generate_scenarios(test))
        self.assertEqual(
            'testscenarios.tests.test_scenarios.ReferenceTest.test_pass(1)',
            tests[0].id())
        self.assertEqual(
            'testscenarios.tests.test_scenarios.ReferenceTest.test_pass(2)',
            tests[1].id())

    def test_scenarios_attribute_cleared(self):
        class ReferenceTest(unittest.TestCase):
            scenarios = [
                ('1', {'foo': 1, 'bar': 2}),
                ('2', {'foo': 2, 'bar': 4})]
            def test_check_foo(self):
                pass
        test = ReferenceTest("test_check_foo")
        tests = list(generate_scenarios(test))
        for adapted in tests:
            self.assertEqual(None, adapted.scenarios)

    def test_multiple_tests(self):
        class Reference1(unittest.TestCase):
            scenarios = [('1', {}), ('2', {})]
            def test_something(self):
                pass
        class Reference2(unittest.TestCase):
            scenarios = [('3', {}), ('4', {})]
            def test_something(self):
                pass
        suite = unittest.TestSuite()
        suite.addTest(Reference1("test_something"))
        suite.addTest(Reference2("test_something"))
        tests = list(generate_scenarios(suite))
        self.assertEqual(4, len(tests))


class TestApplyScenario(testtools.TestCase):

    def setUp(self):
        super(TestApplyScenario, self).setUp()

        self.scenario_name = 'demo'
        self.scenario_attrs = {'foo': 'bar'}
        self.scenario = (self.scenario_name, self.scenario_attrs)

        class ReferenceTest(unittest.TestCase):
            def test_pass(self):
                pass
        self.ReferenceTest = ReferenceTest

    def test_sets_specified_id(self):
        raw_test = self.ReferenceTest('test_pass')
        raw_id = "testscenarios.tests.test_scenarios.ReferenceTest.test_pass"
        scenario_name = self.scenario_name
        expect_id = "%(raw_id)s(%(scenario_name)s)" % vars()
        modified_test = apply_scenario(self.scenario, raw_test)
        self.assertEqual(expect_id, modified_test.id())

    def test_sets_specified_attributes(self):
        raw_test = self.ReferenceTest('test_pass')
        modified_test = apply_scenario(self.scenario, raw_test)
        self.assertEqual('bar', modified_test.foo)

class TestApplyScenarios(testtools.TestCase):

    def test_calls_apply_scenario(self):
        self.addCleanup(setattr, testscenarios.scenarios, 'apply_scenario',
            apply_scenario)
        log = []
        def capture(scenario, test):
            log.append((scenario, test))
        testscenarios.scenarios.apply_scenario = capture
        scenarios = ["foo", "bar"]
        result = list(apply_scenarios(scenarios, "test"))
        self.assertEqual([('foo', 'test'), ('bar', 'test')], log)

    def test_preserves_scenarios_attribute(self):
        class ReferenceTest(unittest.TestCase):
            scenarios = [('demo', {})]
            def test_pass(self):
                pass
        test = ReferenceTest("test_pass")
        tests = list(apply_scenarios(ReferenceTest.scenarios, test))
        self.assertEqual([('demo', {})], ReferenceTest.scenarios)
        self.assertEqual(ReferenceTest.scenarios, tests[0].scenarios)
