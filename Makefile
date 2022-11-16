test:
	pytest -s

lint:
	pylint ./tests ./ansible_specdoc

build:
	pip3 install -r requirements-dev.txt && python setup.py build && python -m build

install: clean_dist build
	pip3 install --force dist/*.whl

clean_dist:
	python setup.py clean --dist

.PHONY: lint test build