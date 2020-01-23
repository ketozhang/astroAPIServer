api:
	FLASK_ENV=development \
	FLASK_APP=test/serve_api.py \
	pipenv run flask run -p 8081 --host=0.0.0.0

.PHONY: app
app:
	FLASK_APP=test/serve_test.py \
	FLASK_ENV=development \
	pipenv run flask run -p 8080 --host=0.0.0.0

boilerplate:
	FLASK_APP=test/boilerplate.py \
	FLASK_ENV=development \
		pipenv run flask run -p 8081 --host=0.0.0.0

.PHONY: dist
dist:
	rm -rf dist/
	python setup.py sdist bdist_wheel
	rm -rf *.egg-info/ build/ 
