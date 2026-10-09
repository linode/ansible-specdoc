PYTHON ?= python3
SPECDOC_VERSION ?= 0.0.0

test:
	pytest -s

black:
	black tests ansible_specdoc

isort:
	isort tests ansible_specdoc

autoflake:
	autoflake tests ansible_specdoc

format: black isort autoflake

lint:
	pylint tests ansible_specdoc
	isort --check-only tests ansible_specdoc
	autoflake --check tests ansible_specdoc
	black --check --verbose tests ansible_specdoc

deps:
	$(PYTHON) -m pip install -e ".[dev]"

create-version:
	@printf '"""The version of this ansible-specdoc package."""\n\n__version__ = "$(patsubst v%,%,$(or $(SPECDOC_VERSION),0.0.0))"\n' > ansible_specdoc/version.py

build: deps create-version
	$(PYTHON) -m build --sdist --wheel

install: clean_dist build
	pip3 install --force dist/*.whl

clean_dist:
	rm -rf dist ansible_specdoc.egg-info build

.PHONY: lint test build create-version
