.PHONY: test
test:
	python3 -m unittest

.PHONY: lint
lint: # Lint code
	flake8 --exclude test.py .
	mypy .
	black --line-length 79 --skip-string-normalization --check .

.PHONY: check
check: lint test
