local:
	pipenv run python test/serve_api.py

.PHONY: test
test:
	pipenv run python test/serve_test.py

wheel:
	rm -rf *.whl
	python setup.py sdist bdist_wheel
	mv dist/*.whl .
	rm -rf dist/ *.egg-info/ build/
