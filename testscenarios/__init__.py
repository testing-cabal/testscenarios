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


"""Support for running tests with different scenarios declaratively

Testscenarios provides clean dependency injection for python unittest style
tests. This can be used for interface testing (testing many implementations via
a single test suite) or for classic dependency injection (provide tests with
dependencies externally to the test code itself, allowing easy testing in
different situations).

See the README for a manual, and the docstrings on individual functions and
methods for details.
"""

from testscenarios._version import __version__

__all__ = [
    'TestWithScenarios',
    'WithScenarios',
    'apply_scenario',
    'apply_scenarios',
    'generate_scenarios',
    'load_tests_apply_scenarios',
    'multiply_scenarios',
    'per_module_scenarios',
    '__version__',
    ]


from testscenarios.scenarios import (  # noqa: E402
    apply_scenario,
    apply_scenarios,
    generate_scenarios,
    load_tests_apply_scenarios,
    multiply_scenarios,
    per_module_scenarios,
    )
from testscenarios.testcase import TestWithScenarios, WithScenarios  # noqa: E402


def test_suite():
    import testscenarios.tests  # noqa: F401
    return testscenarios.tests.test_suite()


def load_tests(standard_tests, module, loader):
    standard_tests.addTests(loader.loadTestsFromNames(["testscenarios.tests"]))
    return standard_tests
