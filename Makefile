local:
	pipenv run python test/serve.py

wheel:
	rm -rf *.whl
	python setup.py sdist bdist_wheel
	mv dist/*.whl .
	rm -rf dist/ *.egg-info/ build/