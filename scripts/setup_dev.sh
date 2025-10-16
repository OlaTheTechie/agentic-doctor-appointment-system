#!/bin/bash
# Development environment setup script

set -e

echo "Setting up Doctor Appointment System Development Environment"
echo "=============================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest black isort mypy flake8

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p data/chat_storage

# Copy environment template
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "Please edit .env file with your API keys"
fi

# Run initial tests
echo "Running initial tests..."
python -m pytest tests/ -v --tb=short || echo "Some tests failed - this is normal for initial setup"

echo ""
echo "Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run 'make run-server' to start the backend"
echo "3. Run 'make run-ui' to start the UI"
echo ""
echo "Available commands:"
echo "- make help          Show all available commands"
echo "- make test          Run all tests"
echo "- make lint          Check code quality"
echo "- make format        Format code"
echo ""