# Lints all .py files in the project.
pylint $(git ls-files '*.py') --rcfile=../config/.pylintrc
