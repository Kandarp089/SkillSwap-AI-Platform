#!/usr/bin/env bash
set -o errexit

echo "========================================"
echo "SkillSwap AI - Production Build"
echo "========================================"

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Running Django system checks..."
python manage.py check --deploy

echo "========================================"
echo "Build completed successfully"
echo "========================================"
