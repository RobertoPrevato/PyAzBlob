.PHONY: release test


artifacts: test
	python setup.py sdist bdist_wheel


prepforbuild:
	pip install --upgrade twine setuptools wheel


testrelease:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*


release:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*


testcov:
	pytest --cov-report html --cov=pyazblob tests/


test:
	flake8 && pytest -v -W ignore
