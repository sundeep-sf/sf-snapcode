.PHONY: clean test install lint help

help:
	@echo "Available commands:"
	@echo "  clean    - Remove build artifacts and cache files"
	@echo "  test     - Run tests with coverage"
	@echo "  install  - Install package in development mode"
	@echo "  lint     - Run pre-commit hooks"

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type d -name '.*_cache' -exec rm -r {} +
	find . -type d -name 'htmlcov' -exec rm -r {} +
	find . -type d -name '*.egg-info' -exec rm -r {} +
	find . -type f -name '.coverage*' -delete

test: install
	pytest --cov=src/snapcode --cov-report=term-missing tests

install:
	uv pip install -e ".[test]"

lint:
	pre-commit run --all-files
