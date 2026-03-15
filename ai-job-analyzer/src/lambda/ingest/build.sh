#!/bin/bash

# This script packages the Lambda function into a zip file.
# Lambda requires all code + dependencies in a single zip.

echo "Building Lambda package..."

# Clean previous build
rm -rf package/
rm -f lambda_function.zip

# Install dependencies into a "package" folder
pip install -r requirements.txt -t package/

# Copy our handler into the package folder
cp handler.py package/

# Create zip from the package folder
cd package
zip -r ../lambda_function.zip .
cd ..

echo "Done! Created lambda_function.zip"