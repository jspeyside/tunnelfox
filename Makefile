clean:
	find . -name "*.pyc" -type f -delete
	find . -name "__pycache__" -type d -delete


init:
	pip install -r requirements.text

report:
	coverage report -m

test:
	tox
