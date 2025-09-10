# LedgerFlow Testing and Quality Gates Makefile

.PHONY: help install test test-unit test-integration test-property test-performance test-all
.PHONY: lint format type-check quality-gates coverage clean
.PHONY: dev-setup dev-up dev-down migrate upgrade downgrade

# Default target
help:
	@echo "LedgerFlow Testing and Quality Gates"
	@echo ""
	@echo "Available targets:"
	@echo "  install          Install all dependencies"
	@echo "  dev-setup        Set up development environment"
	@echo "  dev-up           Start development services (PostgreSQL, Redis)"
	@echo "  dev-down         Stop development services"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests with coverage"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-property    Run property-based tests"
	@echo "  test-performance Run performance tests"
	@echo "  test-all         Run all test suites"
	@echo ""
	@echo "Quality Gates:"
	@echo "  lint             Run ruff linting"
	@echo "  format           Format code with ruff"
	@echo "  type-check       Run mypy type checking"
	@echo "  quality-gates    Run all quality gates"
	@echo "  coverage         Generate coverage report"
	@echo ""
	@echo "Database:"
	@echo "  migrate          Generate new migration"
	@echo "  upgrade          Apply pending migrations"
	@echo "  downgrade        Rollback last migration"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Clean up generated files"

# Installation and setup
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e ".[dev]"

dev-setup: install
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ledgerflow" > .env; \
		echo "REDIS_URL=redis://localhost:6379/0" >> .env; \
		echo "FLASK_ENV=development" >> .env; \
		echo "SECRET_KEY=dev-secret-key" >> .env; \
	fi
	@echo "Development environment ready!"

dev-up:
	@echo "Starting development services..."
	docker-compose up -d postgres redis
	@echo "Waiting for services to be ready..."
	sleep 5
	@echo "Services are ready!"

dev-down:
	@echo "Stopping development services..."
	docker-compose down

# Testing targets
test: quality-gates test-unit test-integration test-property
	@echo "All tests completed successfully!"

test-unit:
	@echo "Running unit tests..."
	pytest tests/ -v \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=90 \
		-m "not slow and not integration and not performance" \
		--maxfail=10

test-integration:
	@echo "Running integration tests..."
	pytest tests/ -v \
		-m "integration" \
		--maxfail=5

test-property:
	@echo "Running property-based tests..."
	pytest tests/test_property_based.py -v \
		-m "property" \
		--maxfail=3

test-performance:
	@echo "Running performance tests..."
	pytest tests/perf/ -v \
		-m "performance" \
		--tb=short \
		--maxfail=1

test-all: test test-performance
	@echo "All test suites completed!"

# Quality gates
lint:
	@echo "Running ruff linting..."
	ruff check app/ tests/

format:
	@echo "Formatting code with ruff..."
	ruff format app/ tests/

format-check:
	@echo "Checking code formatting..."
	ruff format --check app/ tests/

type-check:
	@echo "Running mypy type checking..."
	mypy app/ --strict

quality-gates: lint format-check type-check
	@echo "All quality gates passed!"

coverage:
	@echo "Generating coverage report..."
	pytest tests/ \
		--cov=app \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-fail-under=90 \
		-m "not slow and not performance"
	@echo "Coverage report generated in htmlcov/"

# Database operations
migrate:
	@echo "Generating new migration..."
	alembic revision --autogenerate -m "$(MSG)"

upgrade:
	@echo "Applying pending migrations..."
	alembic upgrade head

downgrade:
	@echo "Rolling back last migration..."
	alembic downgrade -1

# Utilities
clean:
	@echo "Cleaning up generated files..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Cleanup completed!"

# CI/CD targets
ci-test:
	@echo "Running CI test suite..."
	make quality-gates
	make test-unit
	make test-integration
	make test-property

ci-performance:
	@echo "Running CI performance tests..."
	make test-performance

# Accessibility testing
accessibility:
	@echo "Running accessibility tests..."
	npm install -g @lhci/cli@0.12.x
	python app.py &
	sleep 10
	lhci autorun
	pkill -f "python app.py"