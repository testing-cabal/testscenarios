PYTHONPATH:=$(shell pwd)/lib:${PYTHONPATH}

all:

check:
	PYTHONPATH=$(PYTHONPATH) python ./test_all.py $(TESTRULE)

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm -f

TAGS: lib/testscenarios/*.py lib/testscenarios/tests/*.py
	ctags -e -R lib/testscenarios/

tags: lib/testscenarios/*.py lib/testscenarios/tests/*.py
	ctags -R lib/testscenarios/

.PHONY: all check clean
