test:
	pytest -s

lint:
	pylint ./tests ./ansible_specdoc

deps:
	pip install -r requirements-dev.txt -r requirements.txt

build: deps
	python setup.py build && python -m build

install: clean_dist build
	pip3 install --force dist/*.whl

clean_dist:
	python setup.py clean --dist

.PHONY: lint test build