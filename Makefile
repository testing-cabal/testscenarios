PYTHONPATH:=$(shell pwd)/lib:${PYTHONPATH}
PYTHON ?= python

all:

# it would be nice to use doctest directly to run the README, but that's 
# only supported from python2.6 onwards, so we need a script
check:
	PYTHONPATH=$(PYTHONPATH):.:./lib $(PYTHON) run_doctest.py README
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) ./test_all.py $(TESTRULE)

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm -f

TAGS: lib/testscenarios/*.py lib/testscenarios/tests/*.py
	ctags -e -R lib/testscenarios/

tags: lib/testscenarios/*.py lib/testscenarios/tests/*.py
	ctags -R lib/testscenarios/

.PHONY: all check clean
