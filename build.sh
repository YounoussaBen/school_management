#!/usr/bin/env bash

set -o errexit  # Exit on error

# Upgrade pip to the latest version
pip install --upgrade pip


# Install the required packages
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser if applicable
python manage.py createsu