#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

# Install production dependencies
pip install -r requirements.txt

# Collect static assets for WhiteNoise
python manage.py collectstatic --no-input

# Apply any pending database migrations
python manage.py migrate

