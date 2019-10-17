api:
	FLASK_ENV=development \
	FLASK_APP=test/serve_api.py \
	pipenv run flask run -p 8081 --host=0.0.0.0

.PHONY: app
app:
	FLASK_APP=test/serve_test.py \
	FLASK_ENV=development \
	pipenv run flask run -p 8080 --host=0.0.0.0

wheel:
	rm -rf *.whl
	python setup.py sdist bdist_wheel
	mv dist/*.whl .
	rm -rf dist/ *.egg-info/ build/
