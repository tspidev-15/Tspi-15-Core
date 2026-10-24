# TSPI-15 Tests

Automated tests are in `test_interpreter.py` and use Python's standard `unittest` library.

Run from the repository root:

~~~sh
python -m unittest discover -s tests -v
~~~

The suite covers variables, output, arithmetic, conversions, comparisons, conditions, redeclaration, uninitialized variables, functions, errors, escapes, comments, and indentation.