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
from testscenarios.scenarios import generate_scenarios
from testtools.tests.helpers import LoggingResult


class TestGenerateScenarios(unittest.TestCase):

    def test_generate_scenarios_preserves_normal_test(self):
        class ReferenceTest(unittest.TestCase):
            def test_pass(self):
                pass
        test = ReferenceTest("test_pass")
        self.assertEqual([test], list(generate_scenarios(test)))

    def test_normal_test_with_one_scenario(self):
        class ReferenceTest(unittest.TestCase):
            scenarios = [('demo', {})]
            def test_pass(self):
                pass
        test = ReferenceTest("test_pass")
        tests = list(generate_scenarios(test))
        self.assertEqual(
            'testscenarios.tests.test_scenarios.ReferenceTest.test_pass(demo)',
            tests[0].id())

    def test_normal_test_two_scenarios(self):
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

    def test_attributes_set(self):
        class ReferenceTest(unittest.TestCase):
            scenarios = [
                ('1', {'foo': 1, 'bar': 2}),
                ('2', {'foo': 2, 'bar': 4})]
            def test_check_foo(self):
                pass
        test = ReferenceTest("test_check_foo")
        tests = list(generate_scenarios(test))
        self.assertEqual(1, tests[0].foo)
        self.assertEqual(2, tests[0].bar)
        self.assertEqual(2, tests[1].foo)
        self.assertEqual(4, tests[1].bar)

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
