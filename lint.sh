#!/usr/bin/env bash
set -e

echo "Running isort on all Python files in app/..."
isort app/
echo "Running black on all Python files in app/..."
black app/

echo "Formatting complete."