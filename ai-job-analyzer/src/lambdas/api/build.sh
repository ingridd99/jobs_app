#!/bin/bash

# Packages all API Lambda handlers into a single zip.
# We put them all in ONE zip to keep it simple —
# API Gateway will call the right handler based on the route.

echo "Building API Lambda package..."

# Clean previous build.
rm -rf package/
rm -f lambda_function.zip

# Create package directory.
mkdir package

# Copy all handler files into package.
cp health.py package/
cp get_jobs.py package/
cp create_job.py package/
cp analytics.py package/

# No external dependencies needed — boto3 is pre-installed on Lambda.

# Create zip.
cd package
zip -r ../lambda_function.zip .
cd ..

echo "Done! Created lambda_function.zip"