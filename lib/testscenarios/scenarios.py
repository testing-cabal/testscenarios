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

__all__ = [
    'apply_scenario',
    'apply_scenarios',
    'generate_scenarios',
    ]

import unittest

from testtools.testcase import clone_test_with_new_id
from testtools import iterate_tests


def apply_scenario((name, parameters), test):
    """Apply scenario to test.

    :param scenario: A tuple (name, parameters) to apply to the test. The test
        is cloned, its id adjusted to have (name) after it, and the parameters
        dict is used to update the new test.
    :param test: The test to apply the scenario to. This test is unaltered.
    :return: A new test cloned from test, with the scenario applied.
    """
    scenario_suffix = '(' + name + ')'
    newtest = clone_test_with_new_id(test,
        test.id() + scenario_suffix)
    test_desc = test.shortDescription()
    if test_desc is not None:
        newtest_desc = "%(test_desc)s %(scenario_suffix)s" % vars()
        newtest.shortDescription = (lambda: newtest_desc)
    for key, value in parameters.iteritems():
        setattr(newtest, key, value)
    return newtest


def apply_scenarios(scenarios, test):
    """Apply many scenarios to a test.

    :param scenarios: An iterable of scenarios.
    :param test: A test to apply the scenarios to.
    :return: A generator of tests.
    """
    for scenario in scenarios:
        yield apply_scenario(scenario, test)


def generate_scenarios(test_or_suite):
    """Yield the tests in test_or_suite with scenario multiplication done.

    TestCase objects with no scenarios specified are yielded unaltered. Tests
    with scenarios are not yielded at all, instead the results of multiplying
    them by the scenarios they specified gets yielded.

    :param test_or_suite: A TestCase or TestSuite.
    :return: A generator of tests - objects satisfying the TestCase protocol.
    """
    for test in iterate_tests(test_or_suite):
        scenarios = getattr(test, 'scenarios', None)
        if scenarios:
            for newtest in apply_scenarios(scenarios, test):
                newtest.scenarios = None
                yield newtest
        else:
            yield test
