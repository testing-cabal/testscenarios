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

import sys
import unittest

import testscenarios


def test_suite():
    result = unittest.TestSuite()
    standard_tests = unittest.TestSuite()
    module = sys.modules['testscenarios.tests']
    loader = unittest.TestLoader()
    return load_tests(standard_tests, module, loader)


def load_tests(standard_tests, module, loader):
    test_modules = [
        'testcase',
        'scenarios',
        ]
    prefix = "testscenarios.tests.test_"
    test_mod_names = [prefix + test_module for test_module in test_modules]
    standard_tests.addTests(loader.loadTestsFromNames(test_mod_names))
    return standard_tests
