#!/bin/bash

# Build package (PyPI supports Markdown directly via pyproject.toml readme field)
rm -rf dist
poetry build
twine check dist/*
