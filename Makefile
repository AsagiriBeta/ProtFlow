# Makefile for ProtFlow project

.PHONY: help install install-dev test lint format clean docs run

help:
	@echo "ProtFlow Development Commands:"
	@echo "  make install      - Install package in production mode"
	@echo "  make install-dev  - Install package in development mode with dev dependencies"
	@echo "  make test         - Run tests with coverage"
	@echo "  make lint         - Run linters (flake8, mypy)"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Clean build artifacts and cache"
	@echo "  make docs         - Generate documentation"
	@echo "  make run          - Run example pipeline"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,viz,docs]"

test:
	pytest tests/ -v --cov=esm3_pipeline --cov-report=html --cov-report=term

test-quick:
	pytest tests/ -v

lint:
	flake8 esm3_pipeline scripts --max-line-length=127
	mypy esm3_pipeline --ignore-missing-imports || true

format:
	black esm3_pipeline scripts tests
	isort esm3_pipeline scripts tests

format-check:
	black --check esm3_pipeline scripts tests
	isort --check-only esm3_pipeline scripts tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	rm -rf esm3_pipeline/.cache/

docs:
	@echo "Documentation available in:"
	@echo "  - README.md"
	@echo "  - API.md"
	@echo "  - CONTRIBUTING.md"

run:
	python -m scripts.runner --help

# Example: run full pipeline on sample data
example:
	python -m scripts.runner --parse-gbk --predict --p2rank --report --limit 2

# Check dependencies
check-deps:
	@echo "Checking system dependencies..."
	@command -v java >/dev/null 2>&1 && echo "✓ Java installed" || echo "✗ Java missing"
	@command -v obabel >/dev/null 2>&1 && echo "✓ OpenBabel installed" || echo "✗ OpenBabel missing"
	@command -v vina >/dev/null 2>&1 && echo "✓ AutoDock Vina installed" || echo "✗ Vina missing"
	@command -v antismash >/dev/null 2>&1 && echo "✓ antiSMASH installed" || echo "✗ antiSMASH missing (optional)"

# Setup for macOS
setup-macos:
	bash scripts/setup_macos.sh

# Setup for Ubuntu/Debian
setup-ubuntu:
	bash scripts/setup_ubuntu.sh

