# TSPI-15 Core

TSPI-15 is an experimental, beginner-friendly programming language with a dedicated Python interpreter. Version 0.1 focuses on readable syntax, basic expressions, conditions, functions, and clear errors.

## Requirements

- Python 3.10 or newer
- No third-party runtime dependencies

## Install locally

From the repository root:

~~~sh
python -m pip install -e .
~~~

## Run a program

~~~sh
tspi15 examples/hello.tspi
~~~

Or without installing the command:

~~~sh
PYTHONPATH=src python -m tspi15.cli examples/hello.tspi
~~~

## Quick example

~~~tspi
var name = "Alex"
show "Hello, " + name

var score = 10 + "5"
show score

when score >= 15:
    show "Passed"
otherwise:
    show "Try again"

function get_score:
    return score

show get_score
~~~

## Implemented in v0.1

- Variables with inferred or explicit types: `number`, `text`, `boolean`
- `show` output
- Arithmetic, comparisons, `and`, and `or`
- Automatic conversions where defined in `docs/SYNTAX.md`
- `when` / `otherwise` blocks with four-space indentation
- Functions without parameters and value-returning `return`
- Global variables; redeclaration with `var` replaces the previous value and type
- Comments and escapes: `\n`, `\t`, `\"`, `\\`
- Line-numbered syntax and runtime errors
- Automated tests using Python's standard `unittest`

## Limitations

No user input, loops, function parameters, local scopes, or multi-error recovery. Every function call must execute a value-returning `return`; otherwise it raises a runtime error.

## Run tests

~~~sh
python -m unittest discover -s tests -v
~~~

## Project status

This is an early v0.1 implementation; syntax and behavior may evolve as testing continues.

## License

No open-source license has been granted. Unless a license is added, all rights are reserved by default.
