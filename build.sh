#!/bin/bash

# Exit on error
set -e

echo "Installing dependencies..."
npm install

echo "Building frontend..."
npm run build

echo "Creating static directory if it doesn't exist..."
mkdir -p workforce/static/assets

echo "Copying build files to Django static directory..."
cp -r dist/* workforce/static/

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!" 