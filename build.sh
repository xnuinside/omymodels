#!/bin/bash
# Build script for omymodels package

# Merge changelog into README (keep full changelog in README.md for PyPI)
sed '/## Changelog/q' README.md > new_README.md
cat CHANGELOG.txt >> new_README.md
rm README.md
mv new_README.md README.md

# Build package (PyPI supports Markdown directly via pyproject.toml readme field)
rm -rf dist
poetry build
twine check dist/*
