PYTHONPATH = PYTHONPATH=./

.PHONY: test
test: # Runs pytest
	$(PYTHONPATH) python -m unittest

.PHONY: lint
lint: # Lint code
	flake8 --exclude tests --ignore=E203,W503 .
	mypy .
	black --line-length 79 --skip-string-normalization --check .

.PHONY: check
check: lint test