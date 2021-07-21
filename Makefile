.DEFAULT_GOAL := all
isort = isort buildpg tests
black = black -S -l 120 --target-version py38 buildpg tests

.PHONY: install
install:
	pip install -U setuptools pip
	pip install -U -r tests/requirements.txt
	pip install -r tests/requirements-linting.txt
	pip install -e .

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: lint
lint:
	flake8 buildpg/ tests/
	$(isort) --check-only
	$(black) --check

.PHONY: test
test:
	pytest --cov=buildpg

.PHONY: testcov
testcov:
	pytest --cov=buildpg
	@echo "building coverage html"
	@coverage html

.PHONY: all
all: lint testcov
