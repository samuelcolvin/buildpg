.DEFAULT_GOAL := all

.PHONY: install
install:
	pip install -U setuptools pip
	pip install -U -r tests/requirements.txt
	pip install -U .

.PHONY: isort
isort:
	isort -rc -w 120 buildpg
	isort -rc -w 120 tests

.PHONY: lint
lint:
	python setup.py check -rms
	flake8 buildpg/ tests/
	pytest buildpg -p no:sugar -q

.PHONY: test
test:
	pytest --cov=buildpg

.PHONY: testcov
testcov:
	pytest --cov=buildpg
	@echo "building coverage html"
	@coverage html

.PHONY: all
all: testcov lint
