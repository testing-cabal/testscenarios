PYTHONPATH:=$(shell pwd):${PYTHONPATH}
PYTHON ?= python

all: check

check:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m testtools.run \
	    testscenarios.test_suite

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm -f

TAGS: testscenarios/*.py testscenarios/tests/*.py
	ctags -e -R testscenarios/

tags: testscenarios/*.py testscenarios/tests/*.py
	ctags -R testscenarios/

release:
	python setup.py sdist bdist_wheel upload -s

.PHONY: all check release
