import doctest
import sys

for n in sys.argv:
    print doctest.testfile(n, raise_on_error=False, )
