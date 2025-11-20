#!/bin/bash
# HEO Foundation - cPanel Deployment Script
# Run this script after uploading files to your cPanel server

set -e

echo "=== HEO Foundation Deployment Script ==="
echo ""

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_VERSION="3.11"  # Update to match your cPanel Python version

echo "Project directory: $PROJECT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/env" ]; then
    echo "Creating virtual environment..."
    python$PYTHON_VERSION -m venv "$PROJECT_DIR/env"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$PROJECT_DIR/env/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r "$PROJECT_DIR/requirements.txt"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/cache"
mkdir -p "$PROJECT_DIR/media"
mkdir -p "$PROJECT_DIR/staticfiles"

# Set permissions
echo "Setting permissions..."
chmod 755 "$PROJECT_DIR"
chmod 644 "$PROJECT_DIR/.htaccess"
chmod 600 "$PROJECT_DIR/.env"

# Run Django commands
echo "Running database migrations..."
python "$PROJECT_DIR/manage.py" migrate --settings=heo_foundation.settings

echo "Collecting static files..."
python "$PROJECT_DIR/manage.py" collectstatic --noinput --settings=heo_foundation.settings

echo "Creating cache table..."
python "$PROJECT_DIR/manage.py" createcachetable --settings=heo_foundation.settings 2>/dev/null || true

# Check for common issues
echo ""
echo "=== Running Deployment Checks ==="

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "WARNING: .env file not found. Copy .env.production to .env and update values."
fi

# Check DEBUG setting
if grep -q "DEBUG=True" "$PROJECT_DIR/.env" 2>/dev/null; then
    echo "WARNING: DEBUG is set to True in .env. Set to False for production!"
fi

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Ensure .env file is configured with production values"
echo "2. Update .htaccess paths to match your cPanel username"
echo "3. Create a superuser: python manage.py createsuperuser"
echo "4. Restart the Python app in cPanel"
echo ""
