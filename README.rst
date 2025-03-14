*****************************************************************
testscenarios: extensions to python unittest to support scenarios
*****************************************************************

  Copyright (c) 2009, Robert Collins <robertc@robertcollins.net>
  
  Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
  license at the users choice. A copy of both licenses are available in the
  project source as Apache-2.0 and BSD. You may not use this file except in
  compliance with one of these two licences.
  
  Unless required by applicable law or agreed to in writing, software
  distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
  license you chose for the specific language governing permissions and
  limitations under that license.


testscenarios provides clean dependency injection for python unittest style
tests. This can be used for interface testing (testing many implementations via
a single test suite) or for classic dependency injection (provide tests with
dependencies externally to the test code itself, allowing easy testing in
different situations).

Dependencies
============

* testtools <https://github.com/testing-cabal/testtools>


Why TestScenarios
=================

Standard Python unittest.py provides on obvious method for running a single
test_foo method with two (or more) scenarios: by creating a mix-in that
provides the functions, objects or settings that make up the scenario. This is
however limited and unsatisfying. Firstly, when two projects are cooperating
on a test suite (for instance, a plugin to a larger project may want to run
the standard tests for a given interface on its implementation), then it is
easy for them to get out of sync with each other: when the list of TestCase
classes to mix-in with changes, the plugin will either fail to run some tests
or error trying to run deleted tests. Secondly, its not as easy to work with
runtime-created-subclasses (a way of dealing with the aforementioned skew)
because they require more indirection to locate the source of the test, and will
often be ignored by e.g. pyflakes pylint etc.

It is the intent of testscenarios to make dynamically running a single test
in multiple scenarios clear, easy to debug and work with even when the list
of scenarios is dynamically generated.


Defining Scenarios
==================

A **scenario** is a tuple of a string name for the scenario, and a dict of
parameters describing the scenario.  The name is appended to the test name, and
the parameters are made available to the test instance when it's run.

Scenarios are presented in **scenario lists** which are typically Python lists
but may be any iterable.


Getting Scenarios applied
=========================

At its heart the concept is simple. For a given test object with a list of
scenarios we prepare a new test object for each scenario. This involves:

* Clone the test to a new test with a new id uniquely distinguishing it.
* Apply the scenario to the test by setting each key, value in the scenario
  as attributes on the test object.

There are some complicating factors around making this happen seamlessly. These
factors are in two areas:

* Choosing what scenarios to use. (See Setting Scenarios For A Test).
* Getting the multiplication to happen. 

Subclasssing
++++++++++++

If you can subclass TestWithScenarios, then the ``run()`` method in
TestWithScenarios will take care of test multiplication. It will at test
execution act as a generator causing multiple tests to execute. For this to 
work reliably TestWithScenarios must be first in the MRO and you cannot
override run() or __call__. This is the most robust method, in the sense
that any test runner or test loader that obeys the python unittest protocol
will run all your scenarios.

Manual generation
+++++++++++++++++

If you cannot subclass TestWithScenarios (e.g. because you are using
TwistedTestCase, or TestCaseWithResources, or any one of a number of other
useful test base classes, or need to override run() or __call__ yourself) then 
you can cause scenario application to happen later by calling
``testscenarios.generate_scenarios()``. For instance::

  >>> import unittest
  >>> try:
  ...     from StringIO import StringIO
  ... except ImportError:
  ...     from io import StringIO
  >>> from testscenarios.scenarios import generate_scenarios

This can work with loaders and runners from the standard library, or possibly other
implementations::

  >>> loader = unittest.TestLoader()
  >>> test_suite = unittest.TestSuite()
  >>> runner = unittest.TextTestRunner(stream=StringIO())

  >>> mytests = loader.loadTestsFromNames(['doc.test_sample'])
  >>> test_suite.addTests(generate_scenarios(mytests))
  >>> runner.run(test_suite)
  <unittest...TextTestResult run=1 errors=0 failures=0>

Testloaders
+++++++++++

Some test loaders support hooks like ``load_tests`` and ``test_suite``.
Ensuring your tests have had scenario application done through these hooks can
be a good idea - it means that external test runners (which support these hooks
like ``nose``, ``trial``, ``tribunal``) will still run your scenarios. (Of
course, if you are using the subclassing approach this is already a surety).
With ``load_tests``::

  >>> def load_tests(standard_tests, module, loader):
  ...     result = loader.suiteClass()
  ...     result.addTests(generate_scenarios(standard_tests))
  ...     return result

as a convenience, this is available in ``load_tests_apply_scenarios``, so a
module using scenario tests need only say ::

  >>> from testscenarios import load_tests_apply_scenarios as load_tests

Python 2.7 and greater support a different calling convention for `load_tests``
<https://bugs.launchpad.net/bzr/+bug/607412>.  `load_tests_apply_scenarios`
copes with both.

With ``test_suite``::

  >>> def test_suite():
  ...     loader = TestLoader()
  ...     tests = loader.loadTestsFromName(__name__)
  ...     result = loader.suiteClass()
  ...     result.addTests(generate_scenarios(tests))
  ...     return result


Setting Scenarios for a test
============================

A sample test using scenarios can be found in the doc/ folder.

See `pydoc testscenarios` for details.

On the TestCase
+++++++++++++++

You can set a scenarios attribute on the test case::

  >>> class MyTest(unittest.TestCase):
  ...
  ...     scenarios = [
  ...         ('scenario1', dict(param=1)),
  ...         ('scenario2', dict(param=2)),]

This provides the main interface by which scenarios are found for a given test.
Subclasses will inherit the scenarios (unless they override the attribute).

After loading
+++++++++++++

Test scenarios can also be generated arbitrarily later, as long as the test has
not yet run. Simply replace (or alter, but be aware that many tests may share a
single scenarios attribute) the scenarios attribute. For instance in this
example some third party tests are extended to run with a custom scenario. ::

  >>> import testtools
  >>> class TestTransport:
  ...     """Hypothetical test case for bzrlib transport tests"""
  ...     pass
  ...
  >>> stock_library_tests = unittest.TestLoader().loadTestsFromNames(
  ...     ['doc.test_sample'])
  ...
  >>> for test in testtools.iterate_tests(stock_library_tests):
  ...     if isinstance(test, TestTransport):
  ...         test.scenarios = test.scenarios + [my_vfs_scenario]
  ...
  >>> suite = unittest.TestSuite()
  >>> suite.addTests(generate_scenarios(stock_library_tests))

Generated tests don't have a ``scenarios`` list, because they don't normally
require any more expansion.  However, you can add a ``scenarios`` list back on
to them, and then run them through ``generate_scenarios`` again to generate the
cross product of tests. ::

  >>> class CrossProductDemo(unittest.TestCase):
  ...     scenarios = [('scenario_0_0', {}),
  ...                  ('scenario_0_1', {})]
  ...     def test_foo(self):
  ...         return
  ...
  >>> suite = unittest.TestSuite()
  >>> suite.addTests(generate_scenarios(CrossProductDemo("test_foo")))
  >>> for test in testtools.iterate_tests(suite):
  ...     test.scenarios = [
  ...         ('scenario_1_0', {}), 
  ...         ('scenario_1_1', {})]
  ...
  >>> suite2 = unittest.TestSuite()
  >>> suite2.addTests(generate_scenarios(suite))
  >>> print(suite2.countTestCases())
  4

Dynamic Scenarios
+++++++++++++++++

A common use case is to have the list of scenarios be dynamic based on plugins
and available libraries. An easy way to do this is to provide a global scope
scenarios somewhere relevant to the tests that will use it, and then that can
be customised, or dynamically populate your scenarios from a registry etc.
For instance::

  >>> hash_scenarios = []
  >>> try:
  ...     from hashlib import md5
  ... except ImportError:
  ...     pass
  ... else:
  ...     hash_scenarios.append(("md5", dict(hash=md5)))
  >>> try:
  ...     from hashlib import sha1
  ... except ImportError:
  ...     pass
  ... else:
  ...     hash_scenarios.append(("sha1", dict(hash=sha1)))
  ...
  >>> class TestHashContract(unittest.TestCase):
  ...
  ...     scenarios = hash_scenarios
  ...
  >>> class TestHashPerformance(unittest.TestCase):
  ...
  ...     scenarios = hash_scenarios


Forcing Scenarios
+++++++++++++++++

The ``apply_scenarios`` function can be useful to apply scenarios to a test
that has none applied. ``apply_scenarios`` is the workhorse for
``generate_scenarios``, except it takes the scenarios passed in rather than
introspecting the test object to determine the scenarios. The
``apply_scenarios`` function does not reset the test scenarios attribute,
allowing it to be used to layer scenarios without affecting existing scenario
selection.


Generating Scenarios
====================

Some functions (currently one :-) are available to ease generation of scenario
lists for common situations.

Testing Per Implementation Module
+++++++++++++++++++++++++++++++++

It is reasonably common to have multiple Python modules that provide the same
capabilities and interface, and to want apply the same tests to all of them.

In some cases, not all of the statically defined implementations will be able
to be used in a particular testing environment.  For example, there may be both
a C and a pure-Python implementation of a module.  You want to test the C
module if it can be loaded, but also to have the tests pass if the C module has
not been compiled.

The ``per_module_scenarios`` function generates a scenario for each named
module. The module object of the imported module is set in the supplied
attribute name of the resulting scenario.
Modules which raise ``ImportError`` during import will have the
``sys.exc_info()`` of the exception set instead of the module object. Tests
can check for the attribute being a tuple to decide what to do (e.g. to skip).

Note that for the test to be valid, all access to the module under test must go
through the relevant attribute of the test object.  If one of the
implementations is also directly imported by the test module or any other,
testscenarios will not magically stop it being used.


Advice on Writing Scenarios
===========================

If a parameterised test is because of a bug run without being parameterized,
it should fail rather than running with defaults, because this can hide bugs.


Producing Scenarios
===================

The `multiply_scenarios` function produces the cross-product of the scenarios
passed in::

  >>> from testscenarios.scenarios import multiply_scenarios
  >>> 
  >>> scenarios = multiply_scenarios(
  ...      [('scenario1', dict(param1=1)), ('scenario2', dict(param1=2))],
  ...      [('scenario2', dict(param2=1))],
  ...      )
  >>> scenarios == [('scenario1,scenario2', {'param2': 1, 'param1': 1}),
  ...               ('scenario2,scenario2', {'param2': 1, 'param1': 2})]
  True
