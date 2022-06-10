PACKAGE := slapaclsuite
TESTS_DIR := tests
.DEFAULT: test
.PHONY: all test coverage coveragereport flake8 pylint rpm rpm3 clean
TEST_FLAGS_FOR_SUITE := -m unittest discover -f -s $(TESTS_DIR)

PYTHON3 = $(shell which python3 2>/dev/null)
ifneq (, $(PYTHON3))
  PYTHON_BIN = $(PYTHON3)
  RPM_MAKE_TARGET = rpm3
endif

COVERAGE3 = $(shell which coverage-3 2>/dev/null)
ifneq (, $(COVERAGE3))
  COVERAGE = $(COVERAGE3)
endif

all: test

test:
	$(PYTHON_BIN) -B $(TEST_FLAGS_FOR_SUITE)

coverage:
	$(COVERAGE) run $(TEST_FLAGS_FOR_SUITE)
	@rm -rf $(TESTS_DIR)/__pycache__

coveragereport:
	$(COVERAGE) report -m $(PACKAGE)/*.py $(PACKAGE)/*/*.py $(TESTS_DIR)/*.py

flake8:
	@find ./* `git submodule --quiet foreach 'echo -n "-path ./$$path -prune -o "'` -type f -name '*.py' -exec flake8 --show-source --max-line-length=100 {} \;

pylint:
	@find ./* -path ./$(TESTS_DIR) -prune -o -type f -name '*.py' -exec pylint -r no --disable=superfluous-parens --rcfile=/dev/null {} \;
	@find ./$(TESTS_DIR) -type f -name '*.py' -exec pylint -r no --disable=protected-access,locally-disabled --rcfile=/dev/null {} \;

rpm:  $(RPM_MAKE_TARGET)

rpm3:
	fpm -s python -t rpm --python-bin $(PYTHON_BIN) --no-python-fix-name --python-package-name-prefix python3 --no-python-downcase-dependencies --rpm-dist "$$(rpmbuild -E '%{?dist}' | sed -e 's#^\.##')" --iteration 1 setup.py
	@rm -rf build $(PACKAGE).egg-info $(PACKAGE)/$(PACKAGE).egg-info

clean:
	rm -rf $(PACKAGE)/__pycache__
	rm -rf $(PACKAGE)/*/__pycache__
	rm -rf $(TESTS_DIR)/__pycache__
	rm -rf build $(PACKAGE).egg-info $(PACKAGE)/$(PACKAGE).egg-info
