# Makefile for Doctor Appointment System

.PHONY: help install dev-install test lint format clean run-server run-ui build package

# Default target
help:
	@echo "Doctor Appointment System - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install      Install production dependencies"
	@echo "  dev-install  Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run-server   Start the FastAPI backend server"
	@echo "  run-ui       Start the Streamlit UI"
	@echo "  test         Run all tests"
	@echo "  lint         Run code linting"
	@echo "  format       Format code with black and isort"
	@echo ""
	@echo "Testing:"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-memory  Test memory chat system"
	@echo "  test-logging Test logging system"
	@echo ""
	@echo "Packaging:"
	@echo "  build        Build the package"
	@echo "  package      Create distribution packages"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Utilities:"
	@echo "  status       Check system status"
	@echo "  logs         Show recent logs"

# Installation
install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install -e .[dev,test]

# Development
run-server:
	python main.py

run-ui:
	python ui/run_enhanced_app.py

# Testing
test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/ -v -m "unit"

test-integration:
	python -m pytest tests/ -v -m "integration"

test-memory:
	python tests/test_persistent_chat.py

test-logging:
	python tests/test_logging.py

# Code Quality
lint:
	flake8 src/ ui/ tests/
	mypy src/

format:
	black src/ ui/ tests/ main.py
	isort src/ ui/ tests/ main.py

# Packaging
build:
	python -m build

package: clean build
	python setup.py sdist bdist_wheel

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Utilities
status:
	python check_system_status.py

logs:
	tail -f logs/*.log

# Docker (future)
docker-build:
	docker build -t doctor-appointment-system .

docker-run:
	docker run -p 8000:8000 -p 8501:8501 doctor-appointment-system