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
    'TestWithScenarios',
    ]

import unittest

from testtools.testcase import clone_test_with_new_id

class TestWithScenarios(unittest.TestCase):
    """A TestCase with support for scenarios via a scenarios attribute.
    
    When a test object which is an instance of TestWithScenarios is run,
    and there is a non-empty scenarios attribute on the object, the test is
    multiplied by the run method into one test per scenario. For this to work
    reliably the TestWithScenarios.run method must not be overriden in a
    subclass (or overridden compatibly with TestWithScenarios).
    """

    def run(self, result=None):
        scenarios = getattr(self, 'scenarios', None)
        if scenarios:
            for name, parameters in scenarios:
                newtest = clone_test_with_new_id(self,
                    self.id() + '(' + name + ')')
                newtest.scenarios = None
                for key, value in parameters.iteritems():
                    setattr(newtest, key, value)
                newtest.run(result)
            return
        else:
            return super(TestWithScenarios, self).run(result)
