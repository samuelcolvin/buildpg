.DEFAULT_GOAL := all
isort = isort -rc buildpg tests
black = black -S -l 120 --py36 buildpg tests

.PHONY: install
install:
	pip install -U setuptools pip
	pip install -U -r tests/requirements.txt
	pip install -e .

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: lint
lint:
	python setup.py check -rms
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
all: testcov lint
