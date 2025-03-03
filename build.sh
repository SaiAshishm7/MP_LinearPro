#!/bin/bash
# Install dependencies
npm install

# Build the frontend
npm run build

# Copy the build files to the Django static directory
cp -r dist/* workforce/static/ 