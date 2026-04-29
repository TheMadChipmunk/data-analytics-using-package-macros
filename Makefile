# Makefile for Challenge 06: Using Package Macros

.PHONY: test
test:
	@echo "🧪 Running tests for Challenge 04: Using Package Macros"
	@pytest tests/ -v

.PHONY: test-verbose
test-verbose:
	@pytest tests/ -vv -s

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make test         - Run all tests"
	@echo "  make test-verbose - Run tests with full output"
