#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if you have any)
# python manage.py migrate

echo "Build completed successfully!"
