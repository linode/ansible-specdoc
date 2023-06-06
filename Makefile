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
	pip install -r requirements-dev.txt -r requirements.txt

build: deps
	python setup.py build && python -m build

install: clean_dist build
	pip3 install --force dist/*.whl

clean_dist:
	python setup.py clean --dist

.PHONY: lint test build
