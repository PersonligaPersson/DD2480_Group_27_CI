#!/bin/bash
# Lints all .py files in the project.
pylint $(find "branches/$1" -type f -name "*.py") --rcfile=config/.pylintrc
